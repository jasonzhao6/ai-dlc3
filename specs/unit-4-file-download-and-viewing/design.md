# Unit 4 — File Download & Viewing: Design

## No New DynamoDB Entities

This unit reuses existing entities from Units 1–3. No new tables or GSIs needed.

## API Design

Added to the existing `files_handler` Lambda from Unit 3.

**POST /files/download-url**
- Body: `{ "folderId": "...", "fileName": "...", "versionNumber": 3 }`
- `versionNumber` optional — defaults to latest version
- Admin or reader only (for that folder). Returns 403 for uploaders and viewers.
- Returns: `{ "downloadUrl": "..." }`

### Download Flow
1. Frontend calls POST /files/download-url with folderId, fileName, optional versionNumber
2. Lambda validates: user has reader/admin access to the folder
3. Lambda looks up the S3 key from DynamoDB (specific version or latest)
4. Lambda generates S3 pre-signed GET URL
5. Frontend redirects browser to the pre-signed URL to trigger download

## Role Enforcement

The role-based access control applies at two levels:

- **API level:** `files_handler` Lambda checks the user's role before generating download/upload URLs
  - Upload: admin, uploader → allowed; reader, viewer → 403
  - Download: admin, reader → allowed; uploader, viewer → 403

- **UI level:** React conditionally renders buttons based on role
  - Viewer: no upload button, no download button
  - Uploader: upload button visible, no download button
  - Reader: download button visible, no upload button
  - Admin: all buttons visible

## React Frontend Updates

- `FileList` — add download button (conditionally shown based on role)
- `FileVersionHistory` — add download button per version (conditionally shown)
- Role-based UI rendering using the `role` field from the session

## SAM Template Updates

- Add API Gateway route for POST /files/download-url
- No new Lambda needed — extends `files_handler` from Unit 3
