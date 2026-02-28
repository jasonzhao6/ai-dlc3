# Unit 2 — Folder Management & Assignments: Requirements

## User Stories

### US-010: Create Folder
- As an admin, I want to create folders (including nested folders) so that files can be organized.
- Acceptance Criteria:
  - Admin specifies folder name and optional parent folder
  - Folder metadata is created in DynamoDB
  - Duplicate folder names within the same parent are rejected
  - Nested folder hierarchy is supported

### US-011: Delete Folder
- As an admin, I want to delete a folder so that unused structures can be removed.
- Acceptance Criteria:
  - Folder metadata is removed from DynamoDB
  - All files in the folder are deleted from S3
  - Child folders are recursively deleted
  - User assignments to the folder are removed

### US-012: List Folders
- As an admin, I want to view all folders in a hierarchical structure so that I can manage them.
- Acceptance Criteria:
  - Admin sees the full folder tree
  - Each folder shows which users are assigned to it

### US-013: Assign Folders to User (Bulk)
- As an admin, I want to assign one or more folders to a user so that they can access those folders.
- Acceptance Criteria:
  - Admin selects a user and one or more folders to assign
  - Assignments are created in DynamoDB
  - User can immediately access the newly assigned folders
  - Assigning an already-assigned folder is a no-op (no error)

### US-014: Unassign Folders from User (Bulk)
- As an admin, I want to remove one or more folder assignments from a user so that they lose access.
- Acceptance Criteria:
  - Admin selects a user and one or more folders to unassign
  - Assignments are removed from DynamoDB
  - User immediately loses access to unassigned folders

### US-015: Browse Folders
- As a user, I want to browse folders I have access to so that I can find files.
- Acceptance Criteria:
  - Non-admin users see only folders they are assigned to
  - Admin sees all folders
  - Nested folders are navigable (drill down and back up)

## Dependencies
- Unit 1 (Auth & User Management) — users and sessions must exist

## Depends On This
- Unit 3 (File Upload & Browsing)
- Unit 4 (File Download & Viewing)
