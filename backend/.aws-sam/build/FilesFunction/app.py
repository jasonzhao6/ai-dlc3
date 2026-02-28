import json
import uuid
import time
import os
import boto3
from db_util import get_table
from session_util import validate_session, require_role
from response_util import success, error
from boto3.dynamodb.conditions import Key

MAX_FILE_SIZE = 1_073_741_824  # 1 GB


def lambda_handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if method == 'OPTIONS':
        return success({})

    if path == '/files' and method == 'GET':
        return list_or_search_files(event)
    elif path == '/files/upload-url' and method == 'POST':
        return generate_upload_url(event)
    elif path == '/files/download-url' and method == 'POST':
        return generate_download_url(event)
    elif method == 'GET' and '/versions' in path:
        params = event.get('pathParameters') or {}
        return get_versions(event, params.get('folderId'), params.get('fileName'))

    return error('Not found', 404)


def _get_accessible_folder_ids(session):
    """Return list of folder IDs the user can access."""
    if session['role'] == 'admin':
        table = get_table()
        resp = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('FOLDERS'),
        )
        return [item['folderId'] for item in resp.get('Items', [])]
    else:
        table = get_table()
        resp = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{session["username"]}') & Key('SK').begins_with('FOLDER#'),
        )
        return [item['folderId'] for item in resp.get('Items', [])]


def _has_folder_access(session, folder_id):
    if session['role'] == 'admin':
        return True
    table = get_table()
    resp = table.get_item(Key={'PK': f'USER#{session["username"]}', 'SK': f'FOLDER#{folder_id}'})
    return 'Item' in resp


def list_or_search_files(event):
    session = validate_session(event)
    if not session:
        return error('Unauthorized', 401)

    params = event.get('queryStringParameters') or {}
    folder_id = params.get('folderId')
    search = params.get('search', '').strip().lower()
    sort_by = params.get('sortBy', 'name')
    sort_order = params.get('sortOrder', 'asc')

    table = get_table()

    if search:
        # Cross-folder search
        accessible = _get_accessible_folder_ids(session)
        if not accessible:
            return success({'files': []})

        # Query GSI4 for all files, filter by name and accessible folders
        resp = table.query(
            IndexName='GSI4',
            KeyConditionExpression=Key('GSI4PK').eq('FILES'),
        )
        files = []
        for item in resp.get('Items', []):
            if item.get('folderId') in accessible and search in item.get('fileName', '').lower():
                files.append(_format_file(item))
    else:
        if not folder_id:
            return error('folderId or search required')
        if not _has_folder_access(session, folder_id):
            return error('Forbidden', 403)

        # List files in folder (latest pointers only — SK = FILE#<name> without VERSION)
        resp = table.query(
            KeyConditionExpression=Key('PK').eq(f'FOLDER#{folder_id}') & Key('SK').begins_with('FILE#'),
        )
        files = []
        for item in resp.get('Items', []):
            # Only include latest pointers (no VERSION in SK)
            if '#VERSION#' not in item['SK']:
                files.append(_format_file(item))

    # Sort
    key_map = {'name': 'fileName', 'uploadedAt': 'uploadedAt', 'fileSize': 'fileSize'}
    sort_key = key_map.get(sort_by, 'fileName')
    files.sort(key=lambda f: f.get(sort_key, ''), reverse=(sort_order == 'desc'))

    return success({'files': files})


def _format_file(item):
    return {
        'fileName': item.get('fileName', ''),
        'folderId': item.get('folderId', ''),
        'folderName': item.get('folderName', ''),
        'fileSize': item.get('fileSize', 0),
        'uploadedBy': item.get('uploadedBy', ''),
        'uploadedAt': item.get('uploadedAt', 0),
        'latestVersion': item.get('latestVersion', item.get('versionNumber', 1)),
    }


def generate_upload_url(event):
    session = require_role(event, ['admin', 'uploader'])
    if not session:
        return error('Forbidden', 403)

    body = json.loads(event.get('body') or '{}')
    folder_id = body.get('folderId', '')
    file_name = body.get('fileName', '').strip()
    file_size = body.get('fileSize', 0)

    if not folder_id or not file_name:
        return error('folderId and fileName required')
    if file_size > MAX_FILE_SIZE:
        return error(f'File size exceeds maximum of 1GB')
    if not _has_folder_access(session, folder_id):
        return error('Forbidden', 403)

    table = get_table()
    now = int(time.time())

    # Determine version number
    existing = table.get_item(Key={'PK': f'FOLDER#{folder_id}', 'SK': f'FILE#{file_name}'})
    if existing.get('Item'):
        version = int(existing['Item'].get('latestVersion', 0)) + 1
    else:
        version = 1

    s3_key = f'{folder_id}/{file_name}/v{version}'

    # Get folder name
    f_resp = table.get_item(Key={'PK': f'FOLDER#{folder_id}', 'SK': f'FOLDER#{folder_id}'})
    folder_name = f_resp.get('Item', {}).get('folderName', '')

    # Write version entry
    table.put_item(Item={
        'PK': f'FOLDER#{folder_id}',
        'SK': f'FILE#{file_name}#VERSION#{version}',
        'fileId': str(uuid.uuid4()),
        'fileName': file_name,
        'folderId': folder_id,
        'folderName': folder_name,
        's3Key': s3_key,
        'fileSize': file_size,
        'uploadedBy': session['username'],
        'uploadedAt': now,
        'versionNumber': version,
    })

    # Update latest pointer
    table.put_item(Item={
        'PK': f'FOLDER#{folder_id}',
        'SK': f'FILE#{file_name}',
        'GSI4PK': 'FILES',
        'GSI4SK': f'FILE#{file_name}',
        'fileName': file_name,
        'folderId': folder_id,
        'folderName': folder_name,
        'latestVersion': version,
        'fileSize': file_size,
        'uploadedBy': session['username'],
        'uploadedAt': now,
    })

    # Generate pre-signed URL
    s3 = boto3.client('s3')
    upload_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': os.environ['FILE_BUCKET'],
            'Key': s3_key,
            'ContentLength': file_size,
        },
        ExpiresIn=3600,
    )

    return success({'uploadUrl': upload_url, 'versionNumber': version})


def generate_download_url(event):
    session = require_role(event, ['admin', 'reader'])
    if not session:
        return error('Forbidden', 403)

    body = json.loads(event.get('body') or '{}')
    folder_id = body.get('folderId', '')
    file_name = body.get('fileName', '')
    version_number = body.get('versionNumber')

    if not folder_id or not file_name:
        return error('folderId and fileName required')
    if not _has_folder_access(session, folder_id):
        return error('Forbidden', 403)

    table = get_table()

    if version_number:
        # Specific version
        resp = table.get_item(Key={
            'PK': f'FOLDER#{folder_id}',
            'SK': f'FILE#{file_name}#VERSION#{version_number}',
        })
        item = resp.get('Item')
    else:
        # Latest version — look up pointer then get version entry
        pointer = table.get_item(Key={'PK': f'FOLDER#{folder_id}', 'SK': f'FILE#{file_name}'})
        p = pointer.get('Item')
        if not p:
            return error('File not found', 404)
        v = int(p['latestVersion'])
        resp = table.get_item(Key={
            'PK': f'FOLDER#{folder_id}',
            'SK': f'FILE#{file_name}#VERSION#{v}',
        })
        item = resp.get('Item')

    if not item:
        return error('File version not found', 404)

    s3 = boto3.client('s3')
    download_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ['FILE_BUCKET'], 'Key': item['s3Key']},
        ExpiresIn=3600,
    )

    return success({'downloadUrl': download_url, 'fileName': file_name, 'versionNumber': item.get('versionNumber')})


def get_versions(event, folder_id, file_name):
    session = validate_session(event)
    if not session:
        return error('Unauthorized', 401)

    if not folder_id or not file_name:
        return error('folderId and fileName required')
    if not _has_folder_access(session, folder_id):
        return error('Forbidden', 403)

    table = get_table()
    resp = table.query(
        KeyConditionExpression=Key('PK').eq(f'FOLDER#{folder_id}') & Key('SK').begins_with(f'FILE#{file_name}#VERSION#'),
    )

    versions = []
    for item in resp.get('Items', []):
        versions.append({
            'versionNumber': item.get('versionNumber'),
            'fileSize': item.get('fileSize', 0),
            'uploadedBy': item.get('uploadedBy', ''),
            'uploadedAt': item.get('uploadedAt', 0),
        })

    versions.sort(key=lambda v: v['versionNumber'], reverse=True)
    return success({'versions': versions})
