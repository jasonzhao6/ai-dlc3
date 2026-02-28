# Unit 3 — File Upload & Browsing: Tasks

## Infrastructure

- [x] Add S3 file storage bucket to SAM template
- [x] Add GSI-4 (cross-folder file search) to SAM template
- [x] Add FilesFunction Lambda and API Gateway routes to SAM template

## Backend — Files Lambda

- [x] Implement GET /files — list files in folder with sort support, filtered by user access
- [x] Implement GET /files — search mode (cross-folder name search, case-insensitive)
- [x] Implement GET /files/{folderId}/{fileName}/versions — return version history
- [x] Implement POST /files/upload-url — validate access + size, determine version, generate pre-signed PUT URL, write metadata to DynamoDB
- [x] Handle DynamoDB Decimal → int conversion for JSON serialization
- [x] Test: HTTPS call to GET /files?folderId=... to list files
- [x] Test: HTTPS call to GET /files?search=... to search files
- [x] Test: HTTPS call to POST /files/upload-url and upload a file via the returned pre-signed URL
- [x] Test: Upload same file name again and verify new version is created
- [x] Test: Reject upload when fileSize > 1GB

## Frontend

- [x] Build FileList component — display files with name, size, date, version
- [x] Build FileSearchBar component — search input with cross-folder results
- [x] Build FileSortControls component — sort by name/date/size
- [x] Build FileUploadButton component — file picker, size validation, upload via pre-signed URL with progress
- [x] Build FileVersionHistory component — show version list for a file
