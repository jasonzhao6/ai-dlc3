# Unit 2 — Folder Management & Assignments: Tasks

## Infrastructure

- [ ] Add GSI-2 (parent-child folder lookup) and GSI-3 (folder-to-user assignments) to SAM template
- [ ] Add FoldersFunction Lambda and API Gateway routes to SAM template

## Backend — Folders Lambda

- [ ] Implement POST /folders — admin-only, create folder with optional parent, reject duplicate names in same parent
- [ ] Implement GET /folders — return folder tree filtered by user's assignments (admin sees all)
- [ ] Implement DELETE /folders/{folderId} — admin-only, recursive delete of folder + children + S3 files + assignments
- [ ] Implement POST /folders/assignments — admin-only, bulk assign folders to user
- [ ] Implement DELETE /folders/assignments — admin-only, bulk unassign folders from user
- [ ] Test: HTTPS call to POST /folders to create a root folder and a nested folder
- [ ] Test: HTTPS call to GET /folders as admin (all folders) and as non-admin (assigned only)
- [ ] Test: HTTPS call to DELETE /folders/{folderId} and verify cascade
- [ ] Test: HTTPS call to POST /folders/assignments and verify user gains access
- [ ] Test: HTTPS call to DELETE /folders/assignments and verify user loses access

## Frontend

- [ ] Build FolderManagementPage — admin-only, create/delete folders, display folder tree
- [ ] Build FolderAssignmentPanel — admin-only, bulk assign/unassign users to folders
- [ ] Build FolderBrowser — all users, navigate folder hierarchy with drill-down and back-up
