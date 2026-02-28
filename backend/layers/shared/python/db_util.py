import json
import boto3
from decimal import Decimal
import os

_table = None


def get_table():
    global _table
    if _table is None:
        dynamodb = boto3.resource('dynamodb')
        _table = dynamodb.Table(os.environ['TABLE_NAME'])
    return _table


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def to_json(obj):
    return json.dumps(obj, default=decimal_default)
