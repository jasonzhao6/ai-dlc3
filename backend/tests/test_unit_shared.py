"""Unit tests for shared layer modules — pure logic, no AWS calls."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))

from password_util import hash_password, verify_password
from response_util import success, error
from db_util import decimal_default, to_json
from decimal import Decimal
import json


# ---- password_util ----

class TestPasswordUtil:
    def test_hash_and_verify(self):
        pw = 'MySecret123'
        h = hash_password(pw)
        assert ':' in h
        assert verify_password(pw, h)

    def test_wrong_password(self):
        h = hash_password('correct')
        assert not verify_password('wrong', h)

    def test_empty_hash(self):
        assert not verify_password('anything', '')

    def test_malformed_hash(self):
        assert not verify_password('anything', 'nocolon')

    def test_different_hashes_for_same_password(self):
        h1 = hash_password('same')
        h2 = hash_password('same')
        assert h1 != h2  # different salts
        assert verify_password('same', h1)
        assert verify_password('same', h2)


# ---- response_util ----

class TestResponseUtil:
    def test_success_default_200(self):
        resp = success({'key': 'val'})
        assert resp['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in resp['headers']
        body = json.loads(resp['body'])
        assert body['key'] == 'val'

    def test_success_custom_status(self):
        resp = success({'ok': True}, 201)
        assert resp['statusCode'] == 201

    def test_error_default_400(self):
        resp = error('bad input')
        assert resp['statusCode'] == 400
        body = json.loads(resp['body'])
        assert body['error'] == 'bad input'

    def test_error_custom_status(self):
        resp = error('not found', 404)
        assert resp['statusCode'] == 404


# ---- db_util ----

class TestDbUtil:
    def test_decimal_int(self):
        assert decimal_default(Decimal('42')) == 42

    def test_decimal_float(self):
        assert decimal_default(Decimal('3.14')) == 3.14

    def test_non_decimal_raises(self):
        import pytest
        with pytest.raises(TypeError):
            decimal_default('string')

    def test_to_json_with_decimals(self):
        result = to_json({'count': Decimal('5'), 'price': Decimal('9.99')})
        parsed = json.loads(result)
        assert parsed['count'] == 5
        assert parsed['price'] == 9.99
