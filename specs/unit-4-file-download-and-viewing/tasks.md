# Unit 4 — File Download & Viewing: Tasks

## Infrastructure

- [x] Add API Gateway route for POST /files/download-url to SAM template

## Backend — Files Lambda (extend)

- [x] Implement POST /files/download-url — validate role (admin/reader only), look up S3 key, generate pre-signed GET URL
- [x] Support optional versionNumber param (default to latest)
- [x] Return 403 for uploaders and viewers on download endpoint
- [x] Return 403 for readers and viewers on upload endpoint (if not already enforced)
- [x] Test: HTTPS call to POST /files/download-url as admin — verify download works
- [x] Test: HTTPS call to POST /files/download-url as reader — verify download works
- [x] Test: HTTPS call to POST /files/download-url as uploader — verify 403
- [x] Test: HTTPS call to POST /files/download-url as viewer — verify 403
- [x] Test: Download a specific version and verify correct file content

## Frontend

- [x] Add download button to FileList component (hidden for viewer and uploader roles)
- [x] Add per-version download button to FileVersionHistory component
- [x] Ensure upload button is hidden for reader and viewer roles
- [x] Verify all role-based UI rendering works correctly across all 4 personas
