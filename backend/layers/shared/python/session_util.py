import secrets
import time
from db_util import get_table
from boto3.dynamodb.conditions import Key

SESSION_TTL_SECONDS = 86400  # 24 hours


def create_session(username, role):
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    get_table().put_item(Item={
        'PK': f'SESSION#{token}',
        'SK': f'SESSION#{token}',
        'username': username,
        'role': role,
        'createdAt': now,
        'ttl': now + SESSION_TTL_SECONDS,
    })
    return token


def validate_session(event):
    """Extract and validate session token from Authorization header.
    Returns (username, role) or None."""
    headers = event.get('headers') or {}
    auth = headers.get('Authorization') or headers.get('authorization') or ''
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    resp = get_table().get_item(Key={'PK': f'SESSION#{token}', 'SK': f'SESSION#{token}'})
    item = resp.get('Item')
    if not item:
        return None
    if item.get('ttl', 0) < int(time.time()):
        return None
    return {'username': item['username'], 'role': item['role'], 'token': token}


def delete_session(token):
    get_table().delete_item(Key={'PK': f'SESSION#{token}', 'SK': f'SESSION#{token}'})


def delete_sessions_for_user(username):
    """Delete all sessions for a user. Scans SESSION# items matching username."""
    table = get_table()
    # Sessions don't have a GSI by username, so we scan with filter.
    # Acceptable because session count per user is small.
    resp = table.scan(
        FilterExpression='begins_with(PK, :prefix) AND username = :u',
        ExpressionAttributeValues={':prefix': 'SESSION#', ':u': username},
    )
    with table.batch_writer() as batch:
        for item in resp.get('Items', []):
            batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})


def require_role(event, allowed_roles):
    """Validate session and check role. Returns session dict or None."""
    session = validate_session(event)
    if not session:
        return None
    if session['role'] not in allowed_roles:
        return None
    return session
