# User Stories Plan

## Overview
Create user stories for the S3 File-Sharing System based on `vision.md` requirements.

## Deliverables
- `.aidlc/user_stories.md` — Complete user stories document covering all personas, features, and acceptance criteria

## Plan

- [x] **Step 1: Define Personas & Permissions Matrix**
  - Document the 4 personas (Admin, Uploader, Reader, Viewer) and their exact capabilities
  - Derive permissions from vision.md: who can do what with folders, files, users

- [x] **Step 2: Write Authentication & Session Management Stories**
  - Login, logout, session handling via DynamoDB
  - Initial admin account creation during deployment
  - ✅ **Clarified:** Users can reset their own passwords

- [x] **Step 3: Write Admin — User Management Stories**
  - Create, update, delete users
  - Assign roles (Uploader, Reader, Viewer) during creation or update
  - List all users

- [x] **Step 4: Write Admin — Folder Management Stories**
  - Create, delete folders
  - ✅ **Clarified:** Nested/hierarchical folders supported

- [x] **Step 5: Write Admin — User-Folder Assignment Stories**
  - Assign/unassign users to folders
  - Folder assignment during user creation or update (per vision.md)
  - ✅ **Clarified:** Bulk assignment supported

- [x] **Step 6: Write File Browsing & Search Stories**
  - Browse files in assigned folders
  - Search by file name
  - Sort by name (alphabetical), date uploaded, file size

- [x] **Step 7: Write File Upload Stories**
  - Upload via S3 pre-signed URLs (Admin, Uploader only)
  - 1GB max file size enforcement
  - ✅ **Clarified:** Uploading same name creates a new version (versioning, not overwrite)

- [x] **Step 8: Write File Download Stories**
  - Download via S3 pre-signed URLs (Admin, Reader only)

- [x] **Step 9: Write View-Only Stories**
  - Viewer can see file metadata but cannot download or upload

- [x] **Step 10: Review & Finalize**
  - Review all stories for completeness against vision.md
  - Ensure acceptance criteria are testable
  - Get Jason's final approval
