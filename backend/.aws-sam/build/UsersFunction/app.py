import json
import time
from db_util import get_table
from session_util import validate_session, require_role, delete_sessions_for_user
from password_util import hash_password
from response_util import success, error
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if method == 'OPTIONS':
        return success({})

    session = require_role(event, ['admin'])
    if not session:
        return error('Forbidden', 403)

    if path == '/users' and method == 'POST':
        return create_user(event)
    elif path == '/users' and method == 'GET':
        return list_users()
    elif method == 'PUT' and path.startswith('/users/'):
        username = event['pathParameters']['username']
        return update_user(event, username)
    elif method == 'DELETE' and path.startswith('/users/'):
        username = event['pathParameters']['username']
        return delete_user(username)

    return error('Not found', 404)


def create_user(event):
    body = json.loads(event.get('body') or '{}')
    username = body.get('username', '').strip()
    password = body.get('password', '')
    role = body.get('role', '')

    if not username or not password or role not in ('uploader', 'reader', 'viewer'):
        return error('username, password, and role (uploader/reader/viewer) required')

    table = get_table()
    existing = table.get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    if existing.get('Item'):
        return error('Username already exists', 409)

    table.put_item(Item={
        'PK': f'USER#{username}',
        'SK': f'USER#{username}',
        'GSI1PK': 'USERS',
        'GSI1SK': f'USER#{username}',
        'username': username,
        'passwordHash': hash_password(password),
        'role': role,
        'mustChangePassword': False,
        'createdAt': int(time.time()),
    })

    # Optional folder assignments during creation
    folder_ids = body.get('folderIds', [])
    if folder_ids:
        _assign_folders(table, username, folder_ids)

    return success({'message': f'User {username} created'}, 201)


def list_users():
    table = get_table()
    resp = table.query(
        IndexName='GSI1',
        KeyConditionExpression=Key('GSI1PK').eq('USERS'),
    )
    users = []
    for item in resp.get('Items', []):
        username = item['username']
        # Get folder assignments for this user
        assign_resp = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{username}') & Key('SK').begins_with('FOLDER#'),
        )
        folders = [a['folderId'] for a in assign_resp.get('Items', [])]
        users.append({
            'username': username,
            'role': item['role'],
            'createdAt': item.get('createdAt'),
            'mustChangePassword': item.get('mustChangePassword', False),
            'assignedFolders': folders,
        })
    return success({'users': users})


def update_user(event, username):
    body = json.loads(event.get('body') or '{}')
    table = get_table()

    existing = table.get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    if not existing.get('Item'):
        return error('User not found', 404)

    updates = []
    values = {}
    names = {}
    if 'role' in body and body['role'] in ('uploader', 'reader', 'viewer', 'admin'):
        updates.append('#r = :r')
        values[':r'] = body['role']
        names['#r'] = 'role'
    if 'password' in body and body['password']:
        updates.append('passwordHash = :h')
        values[':h'] = hash_password(body['password'])

    if not updates:
        return error('Nothing to update')

    update_args = {
        'Key': {'PK': f'USER#{username}', 'SK': f'USER#{username}'},
        'UpdateExpression': 'SET ' + ', '.join(updates),
        'ExpressionAttributeValues': values,
    }
    if names:
        update_args['ExpressionAttributeNames'] = names
    table.update_item(**update_args)
    return success({'message': f'User {username} updated'})


def delete_user(username):
    if username == 'admin':
        return error('Cannot delete admin account')

    table = get_table()
    existing = table.get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    if not existing.get('Item'):
        return error('User not found', 404)

    # Delete user record
    table.delete_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})

    # Delete all folder assignments
    assign_resp = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{username}') & Key('SK').begins_with('FOLDER#'),
    )
    with table.batch_writer() as batch:
        for item in assign_resp.get('Items', []):
            batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})

    # Delete all sessions
    delete_sessions_for_user(username)

    return success({'message': f'User {username} deleted'})


def _assign_folders(table, username, folder_ids):
    with table.batch_writer() as batch:
        for fid in folder_ids:
            # Look up folder name
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
