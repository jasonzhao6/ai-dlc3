import json
import uuid
import time
import os
import boto3
from db_util import get_table
from session_util import validate_session, require_role
from response_util import success, error
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if method == 'OPTIONS':
        return success({})

    # Assignments endpoints
    if path == '/folders/assignments' and method == 'POST':
        return assign_folders(event)
    elif path == '/folders/assignments' and method == 'DELETE':
        return unassign_folders(event)

    # Folder CRUD
    if path == '/folders' and method == 'POST':
        return create_folder(event)
    elif path == '/folders' and method == 'GET':
        return list_folders(event)
    elif method == 'DELETE' and '/folders/' in path:
        folder_id = event['pathParameters']['folderId']
        return delete_folder(event, folder_id)

    return error('Not found', 404)


def create_folder(event):
    session = require_role(event, ['admin'])
    if not session:
        return error('Forbidden', 403)

    body = json.loads(event.get('body') or '{}')
    folder_name = body.get('folderName', '').strip()
    parent_id = body.get('parentFolderId') or 'ROOT'

    if not folder_name:
        return error('folderName required')

    table = get_table()

    # Check duplicate name in same parent
    resp = table.query(
        IndexName='GSI2',
        KeyConditionExpression=Key('GSI2PK').eq(f'PARENT#{parent_id}'),
    )
    for item in resp.get('Items', []):
        if item.get('folderName') == folder_name:
            return error('Folder name already exists in this location', 409)

    folder_id = str(uuid.uuid4())
    table.put_item(Item={
        'PK': f'FOLDER#{folder_id}',
        'SK': f'FOLDER#{folder_id}',
        'GSI1PK': 'FOLDERS',
        'GSI1SK': f'FOLDER#{folder_id}',
        'GSI2PK': f'PARENT#{parent_id}',
        'GSI2SK': f'FOLDER#{folder_id}',
        'folderId': folder_id,
        'folderName': folder_name,
        'parentFolderId': parent_id,
        'createdAt': int(time.time()),
    })
    return success({'folderId': folder_id, 'folderName': folder_name}, 201)


def list_folders(event):
    session = validate_session(event)
    if not session:
        return error('Unauthorized', 401)

    table = get_table()

    if session['role'] == 'admin':
        # Admin sees all folders
        resp = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('FOLDERS'),
        )
        folders = []
        for item in resp.get('Items', []):
            # Get assigned users
            assign_resp = table.query(
                IndexName='GSI3',
                KeyConditionExpression=Key('GSI3PK').eq(f'FOLDER#{item["folderId"]}'),
            )
            users = [a['username'] for a in assign_resp.get('Items', [])]
            folders.append({
                'folderId': item['folderId'],
                'folderName': item['folderName'],
                'parentFolderId': item.get('parentFolderId', 'ROOT'),
                'assignedUsers': users,
            })
    else:
        # Non-admin sees only assigned folders
        assign_resp = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{session["username"]}') & Key('SK').begins_with('FOLDER#'),
        )
        folders = []
        for a in assign_resp.get('Items', []):
            f_resp = table.get_item(Key={'PK': f'FOLDER#{a["folderId"]}', 'SK': f'FOLDER#{a["folderId"]}'})
            f = f_resp.get('Item')
            if f:
                folders.append({
                    'folderId': f['folderId'],
                    'folderName': f['folderName'],
                    'parentFolderId': f.get('parentFolderId', 'ROOT'),
                })

    return success({'folders': folders})


def delete_folder(event, folder_id):
    session = require_role(event, ['admin'])
    if not session:
        return error('Forbidden', 403)

    table = get_table()
    existing = table.get_item(Key={'PK': f'FOLDER#{folder_id}', 'SK': f'FOLDER#{folder_id}'})
    if not existing.get('Item'):
        return error('Folder not found', 404)

    _recursive_delete(table, folder_id)
    return success({'message': f'Folder {folder_id} deleted'})


def _recursive_delete(table, folder_id):
    # Delete child folders first
    children = table.query(
        IndexName='GSI2',
        KeyConditionExpression=Key('GSI2PK').eq(f'PARENT#{folder_id}'),
    )
    for child in children.get('Items', []):
        _recursive_delete(table, child['folderId'])

    # Delete files in S3
    s3 = boto3.client('s3')
    bucket = os.environ['FILE_BUCKET']
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=f'{folder_id}/')
    if 'Contents' in resp:
        s3.delete_objects(
            Bucket=bucket,
            Delete={'Objects': [{'Key': o['Key']} for o in resp['Contents']]},
        )

    # Delete file metadata from DynamoDB
    file_resp = table.query(
        KeyConditionExpression=Key('PK').eq(f'FOLDER#{folder_id}') & Key('SK').begins_with('FILE#'),
    )
    with table.batch_writer() as batch:
        for item in file_resp.get('Items', []):
            batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})

    # Delete assignments
    assign_resp = table.query(
        IndexName='GSI3',
        KeyConditionExpression=Key('GSI3PK').eq(f'FOLDER#{folder_id}'),
    )
    with table.batch_writer() as batch:
        for item in assign_resp.get('Items', []):
            batch.delete_item(Key={'PK': f'USER#{item["username"]}', 'SK': f'FOLDER#{folder_id}'})

    # Delete folder itself
    table.delete_item(Key={'PK': f'FOLDER#{folder_id}', 'SK': f'FOLDER#{folder_id}'})


def assign_folders(event):
    session = require_role(event, ['admin'])
    if not session:
        return error('Forbidden', 403)

    body = json.loads(event.get('body') or '{}')
    username = body.get('username', '').strip()
    folder_ids = body.get('folderIds', [])

    if not username or not folder_ids:
        return error('username and folderIds required')

    table = get_table()

    # Verify user exists
    user_resp = table.get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    if not user_resp.get('Item'):
        return error('User not found', 404)

    with table.batch_writer() as batch:
        for fid in folder_ids:
            f_resp = table.get_item(Key={'PK': f'FOLDER#{fid}', 'SK': f'FOLDER#{fid}'})
            folder = f_resp.get('Item', {})
            batch.put_item(Item={
                'PK': f'USER#{username}',
                'SK': f'FOLDER#{fid}',
                'GSI3PK': f'FOLDER#{fid}',
                'GSI3SK': f'USER#{username}',
                'username': username,
                'folderId': fid,
                'folderName': folder.get('folderName', ''),
                'assignedAt': int(time.time()),
            })

    return success({'message': f'Folders assigned to {username}'})


def unassign_folders(event):
    session = require_role(event, ['admin'])
    if not session:
        return error('Forbidden', 403)

    body = json.loads(event.get('body') or '{}')
    username = body.get('username', '').strip()
    folder_ids = body.get('folderIds', [])

    if not username or not folder_ids:
        return error('username and folderIds required')

    table = get_table()
    with table.batch_writer() as batch:
        for fid in folder_ids:
            batch.delete_item(Key={'PK': f'USER#{username}', 'SK': f'FOLDER#{fid}'})

    return success({'message': f'Folders unassigned from {username}'})
