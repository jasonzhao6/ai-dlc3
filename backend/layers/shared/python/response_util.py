from db_util import to_json

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
}


def success(body, status=200):
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': to_json(body),
    }


def error(message, status=400):
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': to_json({'error': message}),
    }
