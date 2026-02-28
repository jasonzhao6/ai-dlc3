# Unit 4 — File Download & Viewing: Requirements

## User Stories

### US-022: Download File
- As an admin or reader, I want to download a file so that I can use it locally.
- Acceptance Criteria:
  - User clicks download on a file
  - System generates an S3 pre-signed URL for download
  - File downloads via the pre-signed URL
  - Uploaders and viewers cannot download

### US-023: Download Specific Version
- As an admin or reader, I want to download a specific version of a file so that I can access historical data.
- Acceptance Criteria:
  - User selects a version from the version history
  - System generates a pre-signed URL for that specific version
  - The correct version is downloaded

### US-024: View File Metadata (Viewer)
- As a viewer, I want to see file details in my assigned folders so that I know what files exist.
- Acceptance Criteria:
  - Viewer can see file name, size, upload date, and version in assigned folders
  - Download button is hidden/disabled for the viewer role
  - Upload button is hidden/disabled for the viewer role
  - Direct API requests to download or upload endpoints are rejected with 403 for viewers

## Dependencies
- Unit 1 (Auth & User Management) — authentication and role checks
- Unit 2 (Folder Management & Assignments) — folder access control
- Unit 3 (File Upload & Browsing) — files and file metadata must exist
