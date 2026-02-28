# User Stories - S3 File-Sharing System

## Personas

### Admin
- Full system access
- Can create, update, delete users
- Can create, update, delete folders
- Can assign/unassign folders to users (bulk supported)
- Can upload, download, and view all files

### Uploader
- Can view and upload files to assigned folders only
- Cannot download files
- Cannot manage users or folders

### Reader
- Can view and download files from assigned folders only
- Cannot upload files
- Cannot manage users or folders

### Viewer
- Can view files in assigned folders only
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

**US-002: User Logout**
- As a user, I want to log out so that my session is terminated securely.
- Acceptance Criteria:
  - Session is removed from DynamoDB
  - User is redirected to login page
  - Subsequent requests with old session token are rejected

**US-003: Password Reset**
- As a user, I want to reset my password so that I can regain access if I forget it.
- Acceptance Criteria:
  - User can request password reset from login page
  - User receives a reset link/token
  - User can set a new password using the token
  - Old password no longer works after reset

### Admin - User Management

**US-004: Create User**
- As an admin, I want to create new users so that they can access the system.
- Acceptance Criteria:
  - Admin specifies username, password, and role (Uploader/Reader/Viewer)
  - User is created in DynamoDB
  - Duplicate usernames are rejected

**US-005: Update User**
- As an admin, I want to update user details so that I can change their role or password.
- Acceptance Criteria:
  - Admin can change user's role
  - Admin can reset user's password
  - Changes are persisted in DynamoDB

**US-006: Delete User**
- As an admin, I want to delete users so that they no longer have access.
- Acceptance Criteria:
  - User is removed from DynamoDB
  - User's folder assignments are removed
  - Deleted user cannot log in

**US-007: List Users**
- As an admin, I want to view all users so that I can manage them.
- Acceptance Criteria:
  - Admin sees list of all users with their roles
  - List shows folder assignments per user

### Admin - Folder Management

**US-008: Create Folder**
- As an admin, I want to create folders so that files can be organized.
- Acceptance Criteria:
  - Admin specifies folder name and optional parent folder (nested folders)
  - Folder is created in DynamoDB
  - Duplicate folder names within same parent are rejected

**US-009: Update Folder**
- As an admin, I want to rename folders so that I can correct naming.
- Acceptance Criteria:
  - Admin can change folder name
  - Folder path is updated in DynamoDB
  - Child folders and files maintain relationship

**US-010: Delete Folder**
- As an admin, I want to delete folders so that I can remove unused structures.
- Acceptance Criteria:
  - Folder is removed from DynamoDB
  - Files in folder are deleted from S3
  - Child folders are recursively deleted
  - User assignments to folder are removed

**US-011: List Folders**
- As an admin, I want to view all folders so that I can manage them.
- Acceptance Criteria:
  - Admin sees hierarchical folder structure
  - Shows which users are assigned to each folder

### Admin - User-Folder Assignment

**US-012: Assign Folders to User (Bulk)**
- As an admin, I want to assign multiple folders to a user so that they can access those folders.
- Acceptance Criteria:
  - Admin selects a user and multiple folders
  - Assignments are created in DynamoDB
  - User can immediately access assigned folders

**US-013: Unassign Folders from User (Bulk)**
- As an admin, I want to remove folder assignments from a user so that they lose access.
- Acceptance Criteria:
  - Admin selects a user and folders to unassign
  - Assignments are removed from DynamoDB
  - User immediately loses access to unassigned folders

### Admin - Initial Setup

**US-014: Initial Admin Account**
- As the system, I want to create a default admin account during initial deployment so that the system can be administered.
- Acceptance Criteria:
  - Admin account is created with predefined credentials
  - Admin can log in immediately after deployment
  - Admin should change password on first login

### File & Folder Browsing

**US-015: Browse Folders**
- As a user, I want to browse folders I have access to so that I can find files.
- Acceptance Criteria:
  - User sees only folders they are assigned to (or all folders for admin)
  - Nested folders are navigable
  - User can navigate up and down the folder hierarchy

**US-016: Browse Files**
- As a user, I want to see files in a folder so that I can find what I need.
- Acceptance Criteria:
  - User sees list of files in current folder
  - File list shows name, size, upload date, and version
  - Only files in assigned folders are visible (all for admin)

**US-017: Search Files by Name**
- As a user, I want to search files by name so that I can quickly find specific files.
- Acceptance Criteria:
  - User enters search term
  - Results show files with matching names across accessible folders
  - Search is case-insensitive

**US-018: Sort Files**
- As a user, I want to sort files so that I can organize my view.
- Acceptance Criteria:
  - User can sort by file name (alphabetical)
  - User can sort by upload date (newest/oldest)
  - User can sort by file size (largest/smallest)
  - Sort preference persists during session

### File Upload

**US-019: Upload File**
- As an admin or uploader, I want to upload files to a folder so that I can share them.
- Acceptance Criteria:
  - User selects a file and target folder
  - System generates S3 pre-signed URL for upload
  - File is uploaded directly to S3 via pre-signed URL
  - File metadata is stored in DynamoDB

**US-020: File Size Limit**
- As the system, I want to enforce a 1GB file size limit so that storage is managed.
- Acceptance Criteria:
  - Files larger than 1GB are rejected before upload
  - User sees clear error message for oversized files

**US-021: File Versioning on Upload**
- As an admin or uploader, I want to upload a new version of an existing file so that history is preserved.
- Acceptance Criteria:
  - Uploading a file with same name creates a new version
  - Previous versions are retained in S3
  - Version history is tracked in DynamoDB
  - User can see version list for a file

### File Download

**US-022: Download File**
- As an admin or reader, I want to download files so that I can use them locally.
- Acceptance Criteria:
  - User clicks download on a file
  - System generates S3 pre-signed URL for download
  - File downloads via pre-signed URL
  - Download is logged for audit

**US-023: Download Specific Version**
- As an admin or reader, I want to download a specific version of a file so that I can access historical data.
- Acceptance Criteria:
  - User selects a version from version history
  - System generates pre-signed URL for that version
  - Correct version is downloaded

### View-Only Access

**US-024: View File (No Download)**
- As a viewer, I want to see file details so that I know what files exist.
- Acceptance Criteria:
  - Viewer can see file name, size, upload date, version in assigned folders
  - Download button is hidden/disabled for viewer role
  - Upload button is hidden/disabled for viewer role
  - Attempting to access download URL directly is rejected

### Audit Logging

**US-025: Log User Actions**
- As an admin, I want user actions logged so that I can audit system usage.
- Acceptance Criteria:
  - Login/logout events are logged
  - File uploads are logged (user, file, folder, timestamp)
  - File downloads are logged (user, file, folder, timestamp)
  - Admin actions are logged (user/folder CRUD, assignments)
  - Logs are stored in DynamoDB

**US-026: View Audit Logs**
- As an admin, I want to view audit logs so that I can investigate activity.
- Acceptance Criteria:
  - Admin can view logs filtered by user
  - Admin can view logs filtered by date range
  - Admin can view logs filtered by action type


