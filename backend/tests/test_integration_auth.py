"""Integration tests for Auth Lambda."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'auth'))

from conftest import make_event, parse_response, auth_header


class TestSeedAdmin:
    def test_seed_creates_admin(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        assert resp['statusCode'] == 200
        body = parse_response(resp)
        assert body['message'] == 'Admin created'
        assert body['defaultPassword'] == 'ChangeMe123!'

    def test_seed_idempotent(self, aws_env):
        from functions.auth.app import lambda_handler
        lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        resp = lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        assert resp['statusCode'] == 200
        assert parse_response(resp)['message'] == 'Admin already exists'


class TestLogin:
    def _seed(self, aws_env):
        from functions.auth.app import lambda_handler
        lambda_handler(make_event('/auth/seed-admin', 'POST'), None)

    def test_login_success(self, aws_env):
        from functions.auth.app import lambda_handler
        self._seed(aws_env)
        resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
        assert resp['statusCode'] == 200
        body = parse_response(resp)
        assert 'sessionToken' in body
        assert body['role'] == 'admin'
        assert body['mustChangePassword'] is True

    def test_login_wrong_password(self, aws_env):
        from functions.auth.app import lambda_handler
        self._seed(aws_env)
        resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'wrong'}), None)
        assert resp['statusCode'] == 401

    def test_login_nonexistent_user(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'ghost', 'password': 'x'}), None)
        assert resp['statusCode'] == 401

    def test_login_empty_body(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/login', 'POST', body={}), None)
        assert resp['statusCode'] == 400


class TestLogout:
    def test_logout_success(self, aws_env):
        from functions.auth.app import lambda_handler
        lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        login_resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
        token = parse_response(login_resp)['sessionToken']

        resp = lambda_handler(make_event('/auth/logout', 'POST', headers=auth_header(token)), None)
        assert resp['statusCode'] == 200

        # Token should be invalid now
        resp2 = lambda_handler(make_event('/auth/logout', 'POST', headers=auth_header(token)), None)
        assert resp2['statusCode'] == 401

    def test_logout_no_token(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/logout', 'POST'), None)
        assert resp['statusCode'] == 401


class TestChangePassword:
    def test_change_password_success(self, aws_env):
        from functions.auth.app import lambda_handler
        lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        login_resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
        token = parse_response(login_resp)['sessionToken']

        resp = lambda_handler(make_event('/auth/change-password', 'POST',
            body={'currentPassword': 'ChangeMe123!', 'newPassword': 'NewPass456!'},
            headers=auth_header(token)), None)
        assert resp['statusCode'] == 200

        # Old password should fail
        resp2 = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
        assert resp2['statusCode'] == 401

        # New password should work
        resp3 = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'NewPass456!'}), None)
        assert resp3['statusCode'] == 200

    def test_change_password_wrong_current(self, aws_env):
        from functions.auth.app import lambda_handler
        lambda_handler(make_event('/auth/seed-admin', 'POST'), None)
        login_resp = lambda_handler(make_event('/auth/login', 'POST', body={'username': 'admin', 'password': 'ChangeMe123!'}), None)
        token = parse_response(login_resp)['sessionToken']

        resp = lambda_handler(make_event('/auth/change-password', 'POST',
            body={'currentPassword': 'wrong', 'newPassword': 'x'},
            headers=auth_header(token)), None)
        assert resp['statusCode'] == 401


class TestRouting:
    def test_options_returns_200(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/login', 'OPTIONS'), None)
        assert resp['statusCode'] == 200

    def test_unknown_path_returns_404(self, aws_env):
        from functions.auth.app import lambda_handler
        resp = lambda_handler(make_event('/auth/unknown', 'POST'), None)
        assert resp['statusCode'] == 404
