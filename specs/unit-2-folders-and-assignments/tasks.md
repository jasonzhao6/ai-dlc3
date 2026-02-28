# Unit 2 — Folder Management & Assignments: Tasks

## Infrastructure

- [x] Add GSI-2 (parent-child folder lookup) and GSI-3 (folder-to-user assignments) to SAM template
- [x] Add FoldersFunction Lambda and API Gateway routes to SAM template

## Backend — Folders Lambda

- [x] Implement POST /folders — admin-only, create folder with optional parent, reject duplicate names in same parent
- [x] Implement GET /folders — return folder tree filtered by user's assignments (admin sees all)
- [x] Implement DELETE /folders/{folderId} — admin-only, recursive delete of folder + children + S3 files + assignments
- [x] Implement POST /folders/assignments — admin-only, bulk assign folders to user
- [x] Implement DELETE /folders/assignments — admin-only, bulk unassign folders from user
- [x] Test: HTTPS call to POST /folders to create a root folder and a nested folder
- [x] Test: HTTPS call to GET /folders as admin (all folders) and as non-admin (assigned only)
- [x] Test: HTTPS call to DELETE /folders/{folderId} and verify cascade
- [x] Test: HTTPS call to POST /folders/assignments and verify user gains access
- [x] Test: HTTPS call to DELETE /folders/assignments and verify user loses access

## Frontend

- [x] Build FolderManagementPage — admin-only, create/delete folders, display folder tree
- [x] Build FolderAssignmentPanel — admin-only, bulk assign/unassign users to folders
- [x] Build FolderBrowser — all users, navigate folder hierarchy with drill-down and back-up
