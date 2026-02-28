# Unit 2 — Folder Management & Assignments: Design

## DynamoDB Entities (added to `FileShareTable`)

**Folder entity**
- PK: `FOLDER#<folderId>`
- SK: `FOLDER#<folderId>`
- Attributes: `folderId` (UUID), `folderName`, `parentFolderId` (null for root), `createdAt`

**Assignment entity** (user ↔ folder mapping)
- PK: `USER#<username>`
- SK: `FOLDER#<folderId>`
- Attributes: `username`, `folderId`, `folderName`, `assignedAt`

### Access Patterns

- List all folders: GSI-1 with GSI1PK=`FOLDERS`, GSI1SK=`FOLDER#<folderId>`
- List child folders of a parent: GSI-2 with GSI2PK=`PARENT#<parentFolderId>`, GSI2SK=`FOLDER#<folderId>`
- List folders assigned to a user: Query PK=`USER#<username>`, SK begins_with `FOLDER#`
- List users assigned to a folder: GSI-3 with GSI3PK=`FOLDER#<folderId>`, GSI3SK begins_with `USER#`

### New GSIs Required

- **GSI-2**: GSI2PK / GSI2SK — for parent-child folder queries
- **GSI-3**: GSI3PK / GSI3SK — for folder-to-user assignment lookups (reverse of PK/SK on assignment entity)

## API Design

All endpoints → single Lambda function (`folders_handler`).

**POST /folders**
- Body: `{ "folderName": "...", "parentFolderId": "..." }` (parentFolderId optional)
- Admin only. Creates folder.

**GET /folders**
- Returns folder tree. Admin sees all; non-admin sees only assigned folders.
- Query param: `parentFolderId` (optional, for navigating into a subfolder)

**DELETE /folders/{folderId}**
- Admin only. Recursively deletes folder, child folders, files in S3, and assignments.

**POST /folders/assignments**
- Body: `{ "username": "...", "folderIds": ["...", "..."] }`
- Admin only. Bulk assign folders to user.

**DELETE /folders/assignments**
- Body: `{ "username": "...", "folderIds": ["...", "..."] }`
- Admin only. Bulk unassign folders from user.

## Lambda Design

- `folders_handler` Lambda: handles `/folders/*` routes (CRUD + assignments)
- Reuses `session_util.py` from Unit 1 for auth and role checks

## React Frontend Components

- `FolderManagementPage` — admin-only, create/delete folders, view tree
- `FolderAssignmentPanel` — admin-only, assign/unassign users to folders (bulk)
- `FolderBrowser` — all users, navigate folder hierarchy, shows only accessible folders

## SAM Template Updates

- Add GSI-2 and GSI-3 to `FileShareTable`
- Add `FoldersFunction` Lambda
- Add API Gateway routes for `/folders/*`
