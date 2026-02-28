# User Stories — S3 File-Sharing System

## Personas

### Admin
- Full system access
- Can create, update, delete users
- Can create, delete folders (nested supported)
- Can assign/unassign folders to users (bulk supported)
- Can upload, download, and view all files in all folders

### Uploader
- Can view and upload files to assigned folders only
- Cannot download files
- Cannot manage users or folders

### Reader
- Can view and download files from assigned folders only
- Cannot upload files
- Cannot manage users or folders

### Viewer
- Can view file metadata in assigned folders only
- Cannot download or upload files
- Cannot manage users or folders

---

## User Stories

### Authentication & Session Management

**US-001: User Login**
- As a user, I want to log in with my username and password so that I can access the system.
- Acceptance Criteria:
  - User enters valid credentials and is redirected to the file browser
  - Invalid credentials show an error message
  - Session is created and stored in DynamoDB
  - Session token is returned to the client for subsequent requests

**US-002: User Logout**
- As a user, I want to log out so that my session is terminated securely.
- Acceptance Criteria:
  - Session is removed from DynamoDB
  - User is redirected to the login page
  - Subsequent requests with the old session token are rejected

**US-003: Session Validation**
- As the system, I want to validate session tokens on every request so that only authenticated users can access resources.
- Acceptance Criteria:
  - Every API request (except login) includes a session token
  - Invalid or expired tokens return a 401 response
  - Valid tokens allow the request to proceed

**US-004: Password Reset**
- As a user, I want to reset my own password so that I can regain access or change my credentials.
- Acceptance Criteria:
  - Logged-in user can change their password by providing current and new password
  - Password is updated in DynamoDB
  - Existing session remains valid after password change

**US-005: Initial Admin Account**
- As the system, I want to create a default admin account during initial deployment so that the system can be administered from day one.
- Acceptance Criteria:
  - Admin account is created automatically during first deployment
  - Admin can log in immediately after deployment
  - Admin is prompted to change the default password on first login

### Admin — User Management

**US-006: Create User**
- As an admin, I want to create new users with a specified role so that they can access the system.
- Acceptance Criteria:
  - Admin specifies username, password, and role (Uploader, Reader, or Viewer)
  - User is created in DynamoDB
  - Duplicate usernames are rejected with an error message
  - Folder assignments can optionally be set during creation

**US-007: Update User**
- As an admin, I want to update a user's role or reset their password so that I can manage access.
- Acceptance Criteria:
  - Admin can change a user's role
  - Admin can reset a user's password
  - Changes are persisted in DynamoDB immediately

**US-008: Delete User**
- As an admin, I want to delete a user so that they no longer have access to the system.
- Acceptance Criteria:
  - User record is removed from DynamoDB
  - All folder assignments for the user are removed
  - User's active sessions are invalidated
  - Deleted user cannot log in

**US-009: List Users**
- As an admin, I want to view all users so that I can manage them.
- Acceptance Criteria:
  - Admin sees a list of all users with their roles
  - List shows folder assignments per user

### Admin — Folder Management

**US-010: Create Folder**
- As an admin, I want to create folders (including nested folders) so that files can be organized.
- Acceptance Criteria:
  - Admin specifies folder name and optional parent folder
  - Folder metadata is created in DynamoDB
  - Duplicate folder names within the same parent are rejected
  - Nested folder hierarchy is supported

**US-011: Delete Folder**
- As an admin, I want to delete a folder so that unused structures can be removed.
- Acceptance Criteria:
  - Folder metadata is removed from DynamoDB
  - All files in the folder are deleted from S3
  - Child folders are recursively deleted
  - User assignments to the folder are removed

**US-012: List Folders**
- As an admin, I want to view all folders in a hierarchical structure so that I can manage them.
- Acceptance Criteria:
  - Admin sees the full folder tree
  - Each folder shows which users are assigned to it

### Admin — User-Folder Assignment

**US-013: Assign Folders to User (Bulk)**
- As an admin, I want to assign one or more folders to a user so that they can access those folders.
- Acceptance Criteria:
  - Admin selects a user and one or more folders to assign
  - Assignments are created in DynamoDB
  - User can immediately access the newly assigned folders
  - Assigning an already-assigned folder is a no-op (no error)

**US-014: Unassign Folders from User (Bulk)**
- As an admin, I want to remove one or more folder assignments from a user so that they lose access.
- Acceptance Criteria:
  - Admin selects a user and one or more folders to unassign
  - Assignments are removed from DynamoDB
  - User immediately loses access to unassigned folders

### File & Folder Browsing

**US-015: Browse Folders**
- As a user, I want to browse folders I have access to so that I can find files.
- Acceptance Criteria:
  - Non-admin users see only folders they are assigned to
  - Admin sees all folders
  - Nested folders are navigable (drill down and back up)

**US-016: Browse Files in a Folder**
- As a user, I want to see files in a folder so that I can find what I need.
- Acceptance Criteria:
  - User sees a list of files in the current folder
  - Each file shows: name, size, date uploaded, and version number
  - Only files in assigned folders are visible (all folders for admin)

**US-017: Search Files by Name**
- As a user, I want to search files by name so that I can quickly find specific files.
- Acceptance Criteria:
  - User enters a search term
  - Results show files with matching names across all accessible folders
  - Search is case-insensitive
  - Results show which folder each file is in

**US-018: Sort Files**
- As a user, I want to sort the file list so that I can organize my view.
- Acceptance Criteria:
  - User can sort by file name (alphabetical, ascending/descending)
  - User can sort by date uploaded (newest/oldest first)
  - User can sort by file size (largest/smallest first)

### File Upload

**US-019: Upload File**
- As an admin or uploader, I want to upload a file to a folder so that I can share it with others.
- Acceptance Criteria:
  - User selects a file and a target folder
  - System generates an S3 pre-signed URL for upload
  - File is uploaded directly to S3 via the pre-signed URL
  - File metadata (name, size, upload date, uploader, version) is stored in DynamoDB
  - Readers and viewers cannot upload

**US-020: File Size Limit**
- As the system, I want to enforce a 1GB maximum file size so that storage is managed.
- Acceptance Criteria:
  - Files larger than 1GB are rejected before upload begins
  - The pre-signed URL is configured to reject uploads exceeding 1GB
  - User sees a clear error message for oversized files

**US-021: File Versioning**
- As an admin or uploader, I want uploading a file with the same name to create a new version so that history is preserved.
- Acceptance Criteria:
  - Uploading a file with the same name in the same folder creates a new version
  - Previous versions are retained in S3
  - Version history is tracked in DynamoDB
  - Users can see the version list for a file

### File Download

**US-022: Download File**
- As an admin or reader, I want to download a file so that I can use it locally.
- Acceptance Criteria:
  - User clicks download on a file
  - System generates an S3 pre-signed URL for download
  - File downloads via the pre-signed URL
  - Uploaders and viewers cannot download

**US-023: Download Specific Version**
- As an admin or reader, I want to download a specific version of a file so that I can access historical data.
- Acceptance Criteria:
  - User selects a version from the version history
  - System generates a pre-signed URL for that specific version
  - The correct version is downloaded

### View-Only Access

**US-024: View File Metadata (Viewer)**
- As a viewer, I want to see file details in my assigned folders so that I know what files exist.
- Acceptance Criteria:
  - Viewer can see file name, size, upload date, and version in assigned folders
  - Download button is hidden/disabled for the viewer role
  - Upload button is hidden/disabled for the viewer role
  - Direct API requests to download or upload endpoints are rejected with 403 for viewers
