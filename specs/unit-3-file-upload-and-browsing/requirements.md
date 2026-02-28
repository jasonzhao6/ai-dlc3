# Unit 3 — File Upload & Browsing: Requirements

## User Stories

### US-016: Browse Files in a Folder
- As a user, I want to see files in a folder so that I can find what I need.
- Acceptance Criteria:
  - User sees a list of files in the current folder
  - Each file shows: name, size, date uploaded, and version number
  - Only files in assigned folders are visible (all folders for admin)

### US-017: Search Files by Name
- As a user, I want to search files by name so that I can quickly find specific files.
- Acceptance Criteria:
  - User enters a search term
  - Results show files with matching names across all accessible folders
  - Search is case-insensitive
  - Results show which folder each file is in

### US-018: Sort Files
- As a user, I want to sort the file list so that I can organize my view.
- Acceptance Criteria:
  - User can sort by file name (alphabetical, ascending/descending)
  - User can sort by date uploaded (newest/oldest first)
  - User can sort by file size (largest/smallest first)

### US-019: Upload File
- As an admin or uploader, I want to upload a file to a folder so that I can share it with others.
- Acceptance Criteria:
  - User selects a file and a target folder
  - System generates an S3 pre-signed URL for upload
  - File is uploaded directly to S3 via the pre-signed URL
  - File metadata (name, size, upload date, uploader, version) is stored in DynamoDB
  - Readers and viewers cannot upload

### US-020: File Size Limit
- As the system, I want to enforce a 1GB maximum file size so that storage is managed.
- Acceptance Criteria:
  - Files larger than 1GB are rejected before upload begins
  - The pre-signed URL is configured to reject uploads exceeding 1GB
  - User sees a clear error message for oversized files

### US-021: File Versioning
- As an admin or uploader, I want uploading a file with the same name to create a new version so that history is preserved.
- Acceptance Criteria:
  - Uploading a file with the same name in the same folder creates a new version
  - Previous versions are retained in S3
  - Version history is tracked in DynamoDB
  - Users can see the version list for a file

## Dependencies
- Unit 1 (Auth & User Management) — authentication and role checks
- Unit 2 (Folder Management & Assignments) — folders and access control

## Depends On This
- Unit 4 (File Download & Viewing)
