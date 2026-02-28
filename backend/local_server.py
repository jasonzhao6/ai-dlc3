#!/usr/bin/env python3
"""Local dev server — runs all Lambda handlers without Docker/SAM."""
import sys, os

# Add layer to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'layers', 'shared', 'python'))

os.environ['TABLE_NAME'] = 'file-share-local'
os.environ['FILE_BUCKET'] = 'local-bucket'
os.environ['DYNAMODB_ENDPOINT'] = 'http://localhost:8000'
os.environ['S3_ENDPOINT'] = 'http://localhost:9000'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'minioadmin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minioadmin'

# Reset cached table so it picks up the endpoint
import db_util
db_util._table = None

from functions.auth.app import lambda_handler as auth_handler
from functions.users.app import lambda_handler as users_handler
from functions.folders.app import lambda_handler as folders_handler
from functions.files.app import lambda_handler as files_handler

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

ROUTES = [
    ('/auth/', auth_handler),
    ('/users', users_handler),
    ('/folders', folders_handler),
    ('/files', files_handler),
]


class Handler(BaseHTTPRequestHandler):
    def _handle(self, method):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode() if content_len else None

        # Parse query string
        path = self.path
        query = None
        if '?' in path:
            path, qs = path.split('?', 1)
            from urllib.parse import parse_qs
            query = {k: v[0] for k, v in parse_qs(qs).items()}

        # Parse path parameters
        path_params = {}
        for prefix, _ in ROUTES:
            if path.startswith(prefix) and path != prefix.rstrip('/'):
                parts = path.split('/')
                if prefix == '/users' and len(parts) == 3:
                    path_params['username'] = parts[2]
                elif prefix == '/folders' and len(parts) == 3 and parts[2] != 'assignments':
                    path_params['folderId'] = parts[2]
                elif prefix == '/files' and '/versions' in path and len(parts) == 5:
                    path_params['folderId'] = parts[2]
                    path_params['fileName'] = parts[3]

        event = {
            'path': path,
            'httpMethod': method,
            'headers': dict(self.headers),
            'body': body,
            'queryStringParameters': query,
            'pathParameters': path_params or None,
        }

        handler = None
        for prefix, h in ROUTES:
            if path.startswith(prefix):
                handler = h
                break

        if not handler:
            self.send_response(404)
            self.end_headers()
            return

        resp = handler(event, None)
        self.send_response(resp.get('statusCode', 200))
        for k, v in (resp.get('headers') or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if resp.get('body'):
            self.wfile.write(resp['body'].encode())

    def do_GET(self): self._handle('GET')
    def do_POST(self): self._handle('POST')
    def do_PUT(self): self._handle('PUT')
    def do_DELETE(self): self._handle('DELETE')
    def do_OPTIONS(self): self._handle('OPTIONS')


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    print(f'Local dev server running on http://localhost:{port}')
    HTTPServer(('', port), Handler).serve_forever()
