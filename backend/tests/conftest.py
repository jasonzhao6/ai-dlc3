import os
import sys
import json
import pytest
import boto3
from moto import mock_aws

# Add layer modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))

os.environ['TABLE_NAME'] = 'test-table'
os.environ['FILE_BUCKET'] = 'test-bucket'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'


@pytest.fixture
def aws_env():
    """Mock AWS services and create DynamoDB table + S3 bucket."""
    with mock_aws():
        # Reset cached table reference
        import db_util
        db_util._table = None

        # Create DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI2PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI2SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI3PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI3SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI4PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI4SK', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[
                {'IndexName': 'GSI1', 'KeySchema': [{'AttributeName': 'GSI1PK', 'KeyType': 'HASH'}, {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}], 'Projection': {'ProjectionType': 'ALL'}},
                {'IndexName': 'GSI2', 'KeySchema': [{'AttributeName': 'GSI2PK', 'KeyType': 'HASH'}, {'AttributeName': 'GSI2SK', 'KeyType': 'RANGE'}], 'Projection': {'ProjectionType': 'ALL'}},
                {'IndexName': 'GSI3', 'KeySchema': [{'AttributeName': 'GSI3PK', 'KeyType': 'HASH'}, {'AttributeName': 'GSI3SK', 'KeyType': 'RANGE'}], 'Projection': {'ProjectionType': 'ALL'}},
                {'IndexName': 'GSI4', 'KeySchema': [{'AttributeName': 'GSI4PK', 'KeyType': 'HASH'}, {'AttributeName': 'GSI4SK', 'KeyType': 'RANGE'}], 'Projection': {'ProjectionType': 'ALL'}},
            ],
            BillingMode='PAY_PER_REQUEST',
        )

        # Create S3 bucket
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        yield dynamodb


def make_event(path, method='GET', body=None, headers=None, query=None, path_params=None):
    """Helper to build a Lambda event dict."""
    event = {
        'path': path,
        'httpMethod': method,
        'headers': headers or {},
        'body': json.dumps(body) if body else None,
        'queryStringParameters': query,
        'pathParameters': path_params,
    }
    return event


def parse_response(response):
    """Parse Lambda response body."""
    return json.loads(response['body'])


def seed_admin(aws_env):
    """Seed admin and return session token."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'auth'))
    from functions.auth.app import lambda_handler as auth_handler
    # Seed
    auth_handler(make_event('/auth/seed-admin', 'POST'), None)
    # Login
    resp = auth_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
    data = parse_response(resp)
    return data['sessionToken']


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}
