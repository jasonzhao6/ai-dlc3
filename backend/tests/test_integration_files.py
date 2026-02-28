"""Integration tests for Files Lambda."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers', 'shared', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'auth'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'users'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'folders'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'files'))

from conftest import make_event, parse_response, seed_admin, auth_header


def _full_setup(aws_env):
    """Seed admin, create users (uploader, reader, viewer), create folder, assign all."""
    from functions.auth.app import lambda_handler as auth_handler
    from functions.users.app import lambda_handler as users_handler
    from functions.folders.app import lambda_handler as folders_handler

    admin_token = seed_admin(aws_env)

    # Create users
    tokens = {'admin': admin_token}
    for uname, role in [('uploader1', 'uploader'), ('reader1', 'reader'), ('viewer1', 'viewer')]:
        users_handler(make_event('/users', 'POST',
            body={'username': uname, 'password': 'p', 'role': role},
            headers=auth_header(admin_token)), None)
        login_resp = auth_handler(make_event('/auth/login', 'POST',
            body={'username': uname, 'password': 'p'}), None)
        tokens[uname] = parse_response(login_resp)['sessionToken']

    # Create folder
    f = parse_response(folders_handler(make_event('/folders', 'POST',
        body={'folderName': 'TestFolder'},
        headers=auth_header(admin_token)), None))
    folder_id = f['folderId']

    # Assign all users
    for uname in ['uploader1', 'reader1', 'viewer1']:
        folders_handler(make_event('/folders/assignments', 'POST',
            body={'username': uname, 'folderIds': [folder_id]},
            headers=auth_header(admin_token)), None)

    return tokens, folder_id


class TestUploadUrl:
    def test_admin_can_upload(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'test.txt', 'fileSize': 100},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 200
        body = parse_response(resp)
        assert 'uploadUrl' in body
        assert body['versionNumber'] == 1

    def test_uploader_can_upload(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'doc.pdf', 'fileSize': 500},
            headers=auth_header(tokens['uploader1'])), None)
        assert resp['statusCode'] == 200

    def test_reader_cannot_upload(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'x.txt', 'fileSize': 10},
            headers=auth_header(tokens['reader1'])), None)
        assert resp['statusCode'] == 403

    def test_viewer_cannot_upload(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'x.txt', 'fileSize': 10},
            headers=auth_header(tokens['viewer1'])), None)
        assert resp['statusCode'] == 403

    def test_file_size_limit(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'big.bin', 'fileSize': 2_000_000_000},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 400
        assert '1GB' in parse_response(resp)['error']

    def test_versioning(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        # Upload v1
        r1 = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'report.txt', 'fileSize': 100},
            headers=auth_header(tokens['admin'])), None)
        assert parse_response(r1)['versionNumber'] == 1

        # Upload v2 (same name)
        r2 = lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'report.txt', 'fileSize': 200},
            headers=auth_header(tokens['admin'])), None)
        assert parse_response(r2)['versionNumber'] == 2


class TestListFiles:
    def test_list_files_in_folder(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)

        # Upload a file first
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'a.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files', 'GET',
            query={'folderId': folder_id},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 200
        files = parse_response(resp)['files']
        assert len(files) == 1
        assert files[0]['fileName'] == 'a.txt'

    def test_list_requires_folder_access(self, aws_env):
        from functions.files.app import lambda_handler
        from functions.folders.app import lambda_handler as folders_handler
        tokens, folder_id = _full_setup(aws_env)

        # Create a second folder NOT assigned to viewer
        f2 = parse_response(folders_handler(make_event('/folders', 'POST',
            body={'folderName': 'Secret'},
            headers=auth_header(tokens['admin'])), None))

        resp = lambda_handler(make_event('/files', 'GET',
            query={'folderId': f2['folderId']},
            headers=auth_header(tokens['viewer1'])), None)
        assert resp['statusCode'] == 403

    def test_search_files(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)

        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'report.pdf', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'notes.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files', 'GET',
            query={'search': 'report'},
            headers=auth_header(tokens['admin'])), None)
        files = parse_response(resp)['files']
        assert len(files) == 1
        assert files[0]['fileName'] == 'report.pdf'

    def test_sort_by_name(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)

        for name in ['charlie.txt', 'alpha.txt', 'bravo.txt']:
            lambda_handler(make_event('/files/upload-url', 'POST',
                body={'folderId': folder_id, 'fileName': name, 'fileSize': 10},
                headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files', 'GET',
            query={'folderId': folder_id, 'sortBy': 'name', 'sortOrder': 'asc'},
            headers=auth_header(tokens['admin'])), None)
        files = parse_response(resp)['files']
        names = [f['fileName'] for f in files]
        assert names == ['alpha.txt', 'bravo.txt', 'charlie.txt']


class TestDownloadUrl:
    def test_admin_can_download(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt'},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 200
        assert 'downloadUrl' in parse_response(resp)

    def test_reader_can_download(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt'},
            headers=auth_header(tokens['reader1'])), None)
        assert resp['statusCode'] == 200

    def test_uploader_cannot_download(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt'},
            headers=auth_header(tokens['uploader1'])), None)
        assert resp['statusCode'] == 403

    def test_viewer_cannot_download(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'dl.txt'},
            headers=auth_header(tokens['viewer1'])), None)
        assert resp['statusCode'] == 403

    def test_download_specific_version(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        # Upload 2 versions
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'ver.txt', 'fileSize': 10},
            headers=auth_header(tokens['admin'])), None)
        lambda_handler(make_event('/files/upload-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'ver.txt', 'fileSize': 20},
            headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'ver.txt', 'versionNumber': 1},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 200
        assert parse_response(resp)['versionNumber'] == 1

    def test_download_nonexistent_file(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        resp = lambda_handler(make_event('/files/download-url', 'POST',
            body={'folderId': folder_id, 'fileName': 'nope.txt'},
            headers=auth_header(tokens['admin'])), None)
        assert resp['statusCode'] == 404


class TestVersionHistory:
    def test_get_versions(self, aws_env):
        from functions.files.app import lambda_handler
        tokens, folder_id = _full_setup(aws_env)
        # Upload 3 versions
        for i in range(3):
            lambda_handler(make_event('/files/upload-url', 'POST',
                body={'folderId': folder_id, 'fileName': 'multi.txt', 'fileSize': (i + 1) * 100},
                headers=auth_header(tokens['admin'])), None)

        resp = lambda_handler(make_event(f'/files/{folder_id}/multi.txt/versions', 'GET',
            headers=auth_header(tokens['admin']),
            path_params={'folderId': folder_id, 'fileName': 'multi.txt'}), None)
        assert resp['statusCode'] == 200
        versions = parse_response(resp)['versions']
        assert len(versions) == 3
        # Should be sorted newest first
        assert versions[0]['versionNumber'] == 3
        assert versions[2]['versionNumber'] == 1
