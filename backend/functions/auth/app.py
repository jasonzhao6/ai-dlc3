import json
import time
from db_util import get_table
from session_util import create_session, validate_session, delete_session
from password_util import hash_password, verify_password
from response_util import success, error


def lambda_handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if method == 'OPTIONS':
        return success({})

    if path == '/auth/login' and method == 'POST':
        return handle_login(event)
    elif path == '/auth/logout' and method == 'POST':
        return handle_logout(event)
    elif path == '/auth/change-password' and method == 'POST':
        return handle_change_password(event)
    elif path == '/auth/seed-admin' and method == 'POST':
        return handle_seed_admin(event)

    return error('Not found', 404)


def handle_login(event):
    body = json.loads(event.get('body') or '{}')
    username = body.get('username', '').strip()
    password = body.get('password', '')

    if not username or not password:
        return error('Username and password required')

    resp = get_table().get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    user = resp.get('Item')
    if not user:
        return error('Invalid credentials', 401)

    if not verify_password(password, user.get('passwordHash', '')):
        return error('Invalid credentials', 401)

    token = create_session(username, user['role'])
    return success({
        'sessionToken': token,
        'username': username,
        'role': user['role'],
        'mustChangePassword': user.get('mustChangePassword', False),
    })


def handle_logout(event):
    session = validate_session(event)
    if not session:
        return error('Unauthorized', 401)
    delete_session(session['token'])
    return success({'message': 'Logged out'})


def handle_change_password(event):
    session = validate_session(event)
    if not session:
        return error('Unauthorized', 401)

    body = json.loads(event.get('body') or '{}')
    current_pw = body.get('currentPassword', '')
    new_pw = body.get('newPassword', '')

    if not current_pw or not new_pw:
        return error('Current and new password required')

    table = get_table()
    username = session['username']
    resp = table.get_item(Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'})
    user = resp.get('Item')
    if not user:
        return error('User not found', 404)

    if not verify_password(current_pw, user.get('passwordHash', '')):
        return error('Current password is incorrect', 401)

    table.update_item(
        Key={'PK': f'USER#{username}', 'SK': f'USER#{username}'},
        UpdateExpression='SET passwordHash = :h, mustChangePassword = :f',
        ExpressionAttributeValues={':h': hash_password(new_pw), ':f': False},
    )
    return success({'message': 'Password changed'})


def handle_seed_admin(event):
    table = get_table()
    resp = table.get_item(Key={'PK': 'USER#admin', 'SK': 'USER#admin'})
    if resp.get('Item'):
        return success({'message': 'Admin already exists'})

    table.put_item(Item={
        'PK': 'USER#admin',
        'SK': 'USER#admin',
        'GSI1PK': 'USERS',
        'GSI1SK': 'USER#admin',
        'username': 'admin',
        'passwordHash': hash_password('ChangeMe123!'),
        'role': 'admin',
        'mustChangePassword': True,
        'createdAt': int(time.time()),
    })
    return success({'message': 'Admin created', 'defaultPassword': 'ChangeMe123!'})
