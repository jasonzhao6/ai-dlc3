"""Integration tests for Folders Lambda."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'auth'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'users'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'folders'))

from conftest import make_event, parse_response, seed_admin, auth_header


def _setup(aws_env):
    """Seed admin, create a viewer user, return (admin_token, viewer_token)."""
    from functions.auth.app import lambda_handler as auth_handler
    from functions.users.app import lambda_handler as users_handler

    admin_token = seed_admin(aws_env)
    users_handler(make_event('/users', 'POST',
        body={'username': 'viewer1', 'password': 'p', 'role': 'viewer'},
        headers=auth_header(admin_token)), None)
    login_resp = auth_handler(make_event('/auth/login', 'POST',
        body={'username': 'viewer1', 'password': 'p'}), None)
    viewer_token = parse_response(login_resp)['sessionToken']
    return admin_token, viewer_token


class TestCreateFolder:
    def test_create_root_folder(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        resp = lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Documents'},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 201
        body = parse_response(resp)
        assert body['folderName'] == 'Documents'
        assert 'folderId' in body

    def test_create_nested_folder(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        parent = parse_response(lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Root'},
            headers=auth_header(admin_token)), None))

        resp = lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Child', 'parentFolderId': parent['folderId']},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 201

    def test_duplicate_name_rejected(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Docs'},
            headers=auth_header(admin_token)), None)
        resp = lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Docs'},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 409

    def test_create_folder_forbidden_for_non_admin(self, aws_env):
        from functions.folders.app import lambda_handler
        _, viewer_token = _setup(aws_env)
        resp = lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'X'},
            headers=auth_header(viewer_token)), None)
        assert resp['statusCode'] == 403


class TestListFolders:
    def test_admin_sees_all(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'A'},
            headers=auth_header(admin_token)), None)
        lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'B'},
            headers=auth_header(admin_token)), None)

        resp = lambda_handler(make_event('/folders', 'GET',
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 200
        folders = parse_response(resp)['folders']
        assert len(folders) == 2

    def test_non_admin_sees_only_assigned(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, viewer_token = _setup(aws_env)

        f1 = parse_response(lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Assigned'},
            headers=auth_header(admin_token)), None))
        lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'NotAssigned'},
            headers=auth_header(admin_token)), None)

        # Assign one folder
        lambda_handler(make_event('/folders/assignments', 'POST',
            body={'username': 'viewer1', 'folderIds': [f1['folderId']]},
            headers=auth_header(admin_token)), None)

        resp = lambda_handler(make_event('/folders', 'GET',
            headers=auth_header(viewer_token)), None)
        folders = parse_response(resp)['folders']
        assert len(folders) == 1
        assert folders[0]['folderName'] == 'Assigned'


class TestDeleteFolder:
    def test_delete_folder(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        f = parse_response(lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'ToDelete'},
            headers=auth_header(admin_token)), None))

        resp = lambda_handler(make_event(f'/folders/{f["folderId"]}', 'DELETE',
            headers=auth_header(admin_token),
            path_params={'folderId': f['folderId']}), None)
        assert resp['statusCode'] == 200

        # Verify gone
        list_resp = lambda_handler(make_event('/folders', 'GET',
            headers=auth_header(admin_token)), None)
        assert len(parse_response(list_resp)['folders']) == 0

    def test_delete_nonexistent(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        resp = lambda_handler(make_event('/folders/fake-id', 'DELETE',
            headers=auth_header(admin_token),
            path_params={'folderId': 'fake-id'}), None)
        assert resp['statusCode'] == 404


class TestAssignments:
    def test_assign_and_unassign(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, viewer_token = _setup(aws_env)

        f = parse_response(lambda_handler(make_event('/folders', 'POST',
            body={'folderName': 'Shared'},
            headers=auth_header(admin_token)), None))

        # Assign
        resp = lambda_handler(make_event('/folders/assignments', 'POST',
            body={'username': 'viewer1', 'folderIds': [f['folderId']]},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 200

        # Verify assigned
        list_resp = lambda_handler(make_event('/folders', 'GET',
            headers=auth_header(viewer_token)), None)
        assert len(parse_response(list_resp)['folders']) == 1

        # Unassign
        resp = lambda_handler(make_event('/folders/assignments', 'DELETE',
            body={'username': 'viewer1', 'folderIds': [f['folderId']]},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 200

        # Verify unassigned
        list_resp = lambda_handler(make_event('/folders', 'GET',
            headers=auth_header(viewer_token)), None)
        assert len(parse_response(list_resp)['folders']) == 0

    def test_assign_nonexistent_user(self, aws_env):
        from functions.folders.app import lambda_handler
        admin_token, _ = _setup(aws_env)
        resp = lambda_handler(make_event('/folders/assignments', 'POST',
            body={'username': 'ghost', 'folderIds': ['x']},
            headers=auth_header(admin_token)), None)
        assert resp['statusCode'] == 404
