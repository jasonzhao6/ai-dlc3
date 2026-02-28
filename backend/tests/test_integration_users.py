"""Integration tests for Users Lambda."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'auth'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'users'))

from conftest import make_event, parse_response, seed_admin, auth_header


def _get_admin_token(aws_env):
    return seed_admin(aws_env)


class TestCreateUser:
    def test_create_user_success(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        resp = lambda_handler(make_event('/users', 'POST',
            body={'username': 'alice', 'password': 'pass123', 'role': 'reader'},
            headers=auth_header(token)), None)
        assert resp['statusCode'] == 201
        assert 'alice' in parse_response(resp)['message']

    def test_create_user_duplicate(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        lambda_handler(make_event('/users', 'POST',
            body={'username': 'bob', 'password': 'p', 'role': 'viewer'},
            headers=auth_header(token)), None)
        resp = lambda_handler(make_event('/users', 'POST',
            body={'username': 'bob', 'password': 'p', 'role': 'viewer'},
            headers=auth_header(token)), None)
        assert resp['statusCode'] == 409

    def test_create_user_invalid_role(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        resp = lambda_handler(make_event('/users', 'POST',
            body={'username': 'x', 'password': 'p', 'role': 'superadmin'},
            headers=auth_header(token)), None)
        assert resp['statusCode'] == 400

    def test_create_user_no_auth(self, aws_env):
        from functions.users.app import lambda_handler
        resp = lambda_handler(make_event('/users', 'POST',
            body={'username': 'x', 'password': 'p', 'role': 'viewer'}), None)
        assert resp['statusCode'] == 403


class TestListUsers:
    def test_list_users(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        lambda_handler(make_event('/users', 'POST',
            body={'username': 'alice', 'password': 'p', 'role': 'reader'},
            headers=auth_header(token)), None)

        resp = lambda_handler(make_event('/users', 'GET', headers=auth_header(token)), None)
        assert resp['statusCode'] == 200
        users = parse_response(resp)['users']
        usernames = [u['username'] for u in users]
        assert 'admin' in usernames
        assert 'alice' in usernames

    def test_list_users_forbidden_for_non_admin(self, aws_env):
        from functions.users.app import lambda_handler as users_handler
        from functions.auth.app import lambda_handler as auth_handler
        token = _get_admin_token(aws_env)

        # Create a viewer
        users_handler(make_event('/users', 'POST',
            body={'username': 'viewer1', 'password': 'p', 'role': 'viewer'},
            headers=auth_header(token)), None)

        # Login as viewer
        login_resp = auth_handler(make_event('/auth/login', 'POST',
            body={'username': 'viewer1', 'password': 'p'}), None)
        viewer_token = parse_response(login_resp)['sessionToken']

        resp = users_handler(make_event('/users', 'GET', headers=auth_header(viewer_token)), None)
        assert resp['statusCode'] == 403


class TestUpdateUser:
    def test_update_role(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        lambda_handler(make_event('/users', 'POST',
            body={'username': 'alice', 'password': 'p', 'role': 'viewer'},
            headers=auth_header(token)), None)

        resp = lambda_handler(make_event('/users/alice', 'PUT',
            body={'role': 'uploader'},
            headers=auth_header(token),
            path_params={'username': 'alice'}), None)
        assert resp['statusCode'] == 200

    def test_update_nonexistent(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        resp = lambda_handler(make_event('/users/ghost', 'PUT',
            body={'role': 'viewer'},
            headers=auth_header(token),
            path_params={'username': 'ghost'}), None)
        assert resp['statusCode'] == 404


class TestDeleteUser:
    def test_delete_user(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        lambda_handler(make_event('/users', 'POST',
            body={'username': 'alice', 'password': 'p', 'role': 'viewer'},
            headers=auth_header(token)), None)

        resp = lambda_handler(make_event('/users/alice', 'DELETE',
            headers=auth_header(token),
            path_params={'username': 'alice'}), None)
        assert resp['statusCode'] == 200

        # Verify deleted
        list_resp = lambda_handler(make_event('/users', 'GET', headers=auth_header(token)), None)
        usernames = [u['username'] for u in parse_response(list_resp)['users']]
        assert 'alice' not in usernames

    def test_cannot_delete_admin(self, aws_env):
        from functions.users.app import lambda_handler
        token = _get_admin_token(aws_env)
        resp = lambda_handler(make_event('/users/admin', 'DELETE',
            headers=auth_header(token),
            path_params={'username': 'admin'}), None)
        assert resp['statusCode'] == 400
