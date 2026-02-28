import json
import boto3
from decimal import Decimal
import os

_table = None
_s3_client = None


def get_table():
    global _table
    if _table is None:
        endpoint = os.environ.get('DYNAMODB_ENDPOINT')
        if endpoint:
            dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint,
                region_name='us-east-1', aws_access_key_id='fake', aws_secret_access_key='fake')
        else:
            dynamodb = boto3.resource('dynamodb')
        _table = dynamodb.Table(os.environ['TABLE_NAME'])
    return _table


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        endpoint = os.environ.get('S3_ENDPOINT')
        if endpoint:
            _s3_client = boto3.client('s3', endpoint_url=endpoint,
                region_name='us-east-1', aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin',
                config=boto3.session.Config(signature_version='s3v4'))
        else:
            _s3_client = boto3.client('s3')
    return _s3_client


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def to_json(obj):
    return json.dumps(obj, default=decimal_default)
