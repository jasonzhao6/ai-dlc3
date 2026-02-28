# Unit 4 — File Download & Viewing: Tasks

## Infrastructure

- [ ] Add API Gateway route for POST /files/download-url to SAM template

## Backend — Files Lambda (extend)

- [ ] Implement POST /files/download-url — validate role (admin/reader only), look up S3 key, generate pre-signed GET URL
- [ ] Support optional versionNumber param (default to latest)
- [ ] Return 403 for uploaders and viewers on download endpoint
- [ ] Return 403 for readers and viewers on upload endpoint (if not already enforced)
- [ ] Test: HTTPS call to POST /files/download-url as admin — verify download works
- [ ] Test: HTTPS call to POST /files/download-url as reader — verify download works
- [ ] Test: HTTPS call to POST /files/download-url as uploader — verify 403
- [ ] Test: HTTPS call to POST /files/download-url as viewer — verify 403
- [ ] Test: Download a specific version and verify correct file content

## Frontend

- [ ] Add download button to FileList component (hidden for viewer and uploader roles)
- [ ] Add per-version download button to FileVersionHistory component
- [ ] Ensure upload button is hidden for reader and viewer roles
- [ ] Verify all role-based UI rendering works correctly across all 4 personas
