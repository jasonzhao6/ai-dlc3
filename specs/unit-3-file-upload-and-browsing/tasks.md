# Unit 3 — File Upload & Browsing: Tasks

## Infrastructure

- [ ] Add S3 file storage bucket to SAM template
- [ ] Add GSI-4 (cross-folder file search) to SAM template
- [ ] Add FilesFunction Lambda and API Gateway routes to SAM template

## Backend — Files Lambda

- [ ] Implement GET /files — list files in folder with sort support, filtered by user access
- [ ] Implement GET /files — search mode (cross-folder name search, case-insensitive)
- [ ] Implement GET /files/{folderId}/{fileName}/versions — return version history
- [ ] Implement POST /files/upload-url — validate access + size, determine version, generate pre-signed PUT URL, write metadata to DynamoDB
- [ ] Handle DynamoDB Decimal → int conversion for JSON serialization
- [ ] Test: HTTPS call to GET /files?folderId=... to list files
- [ ] Test: HTTPS call to GET /files?search=... to search files
- [ ] Test: HTTPS call to POST /files/upload-url and upload a file via the returned pre-signed URL
- [ ] Test: Upload same file name again and verify new version is created
- [ ] Test: Reject upload when fileSize > 1GB

## Frontend

- [ ] Build FileList component — display files with name, size, date, version
- [ ] Build FileSearchBar component — search input with cross-folder results
- [ ] Build FileSortControls component — sort by name/date/size
- [ ] Build FileUploadButton component — file picker, size validation, upload via pre-signed URL with progress
- [ ] Build FileVersionHistory component — show version list for a file
