# Component Model — S3 File-Sharing System

## 1. Backend Components

### 1.1 Auth Service

Handles authentication and password management.

**Attributes:**
- sessionTTL: duration (default 24 hours)

**Behaviors:**
- `login(username, password)` → creates a Session, returns session token + role + mustChangePassword flag
- `logout(sessionToken)` → deletes the Session
- `changePassword(sessionToken, currentPassword, newPassword)` → updates User password hash, clears mustChangePassword flag
- `seedAdmin()` → creates the initial admin User on first deployment with mustChangePassword=true

**Collaborators:** Session Manager, User Repository

---

### 1.2 User Manager

Admin-only CRUD operations on users.

**Attributes:** (none — stateless, operates on User entities)

**Behaviors:**
- `createUser(username, password, role, folderIds?)` → creates User entity; optionally creates Assignments
- `updateUser(username, role?, password?)` → updates User role and/or password hash
- `deleteUser(username)` → deletes User entity, all their Assignments, and all their Sessions
- `listUsers()` → returns all Users with their roles and assigned folders

**Collaborators:** User Repository, Assignment Repository, Session Manager

---

### 1.3 Folder Manager

Admin-only CRUD operations on folders.

**Attributes:** (none — stateless)

**Behaviors:**
- `createFolder(folderName, parentFolderId?)` → creates Folder entity; rejects duplicate names within same parent
- `deleteFolder(folderId)` → recursively deletes Folder, child Folders, all Files in S3, and all Assignments for those folders
- `listAllFolders()` → returns full folder tree with assigned users per folder
- `listAccessibleFolders(username, role)` → returns folder tree filtered to user's assignments (admin sees all)
- `getChildFolders(parentFolderId)` → returns immediate children of a folder

**Collaborators:** Folder Repository, Assignment Repository, File Repository, File Storage

---

### 1.4 Assignment Manager

Admin-only bulk assign/unassign of users to folders.

**Attributes:** (none — stateless)

**Behaviors:**
- `assignFolders(username, folderIds[])` → creates Assignment entities; idempotent (no error on re-assign)
- `unassignFolders(username, folderIds[])` → deletes Assignment entities
- `getFoldersForUser(username)` → returns list of folder IDs assigned to a user
- `getUsersForFolder(folderId)` → returns list of usernames assigned to a folder

**Collaborators:** Assignment Repository

---

### 1.5 File Manager

Handles file metadata, browsing, search, sort, upload URL generation, and version tracking.

**Attributes:**
- maxFileSize: 1GB

**Behaviors:**
- `listFiles(folderId, sortBy?, sortOrder?)` → returns file metadata list for a folder (latest versions), sorted as requested
- `searchFiles(searchTerm, accessibleFolderIds[])` → returns files matching name across accessible folders, case-insensitive
- `getVersionHistory(folderId, fileName)` → returns all versions of a file
- `generateUploadUrl(folderId, fileName, fileSize)` → validates size ≤ 1GB, determines next version number, creates file metadata in DB, returns pre-signed PUT URL
- `generateDownloadUrl(folderId, fileName, versionNumber?)` → looks up S3 key (specific or latest version), returns pre-signed GET URL

**Collaborators:** File Repository, File Storage, Assignment Manager (for access checks)

---

### 1.6 File Storage

Abstraction over S3 for file operations.

**Attributes:**
- bucketName: string
- keyPattern: `<folderId>/<fileName>/v<versionNumber>`

**Behaviors:**
- `generatePresignedUploadUrl(s3Key, maxContentLength)` → returns a pre-signed PUT URL with size constraint
- `generatePresignedDownloadUrl(s3Key)` → returns a pre-signed GET URL
- `deleteFile(s3Key)` → deletes a single object from S3
- `deleteFolder(folderPrefix)` → deletes all objects under a folder prefix in S3

**Collaborators:** AWS S3

---

## 2. Frontend Components

### 2.1 Login Page

**Attributes:**
- username: string (input)
- password: string (input)
- errorMessage: string

**Behaviors:**
- `submitLogin()` → calls Auth Service login; on success stores session token and navigates to App Shell; on failure shows error
- `redirectToFileBrowser()` → navigates to folder browser after successful login

**Collaborators:** Auth Service

---

### 2.2 Change Password Modal

**Attributes:**
- currentPassword: string (input)
- newPassword: string (input)
- isForced: boolean (true on first login when mustChangePassword)

**Behaviors:**
- `submitChangePassword()` → calls Auth Service changePassword; on success closes modal
- `autoShow()` → shown automatically when session has mustChangePassword=true

**Collaborators:** Auth Service

---

### 2.3 App Shell

Top-level layout wrapping all authenticated pages.

**Attributes:**
- sessionToken: string
- currentUser: { username, role }
- currentRoute: string

**Behaviors:**
- `logout()` → calls Auth Service logout, clears session, redirects to Login Page
- `routeByRole()` → shows/hides nav items based on role (admin sees User Admin + Folder Admin)
- `validateSession()` → on each navigation, checks session validity; redirects to Login Page on 401

**Collaborators:** Auth Service, Session Manager

---

### 2.4 User Admin Page

Admin-only.

**Attributes:**
- userList: array of { username, role, assignedFolders[] }
- selectedUser: object (for edit/delete)

**Behaviors:**
- `loadUsers()` → calls User Manager listUsers
- `createUser(username, password, role)` → calls User Manager createUser
- `updateUser(username, role?, password?)` → calls User Manager updateUser
- `deleteUser(username)` → calls User Manager deleteUser with confirmation prompt

**Collaborators:** User Manager

---

### 2.5 Folder Admin Page

Admin-only. Manages folders and user-folder assignments.

**Attributes:**
- folderTree: hierarchical folder structure
- selectedFolder: object
- assignmentList: array of { username, folderId }

**Behaviors:**
- `loadFolderTree()` → calls Folder Manager listAllFolders
- `createFolder(folderName, parentFolderId?)` → calls Folder Manager createFolder
- `deleteFolder(folderId)` → calls Folder Manager deleteFolder with confirmation prompt
- `assignFolders(username, folderIds[])` → calls Assignment Manager assignFolders
- `unassignFolders(username, folderIds[])` → calls Assignment Manager unassignFolders

**Collaborators:** Folder Manager, Assignment Manager

---

### 2.6 File Browser Page

All authenticated users.

**Attributes:**
- currentFolderId: string
- folderPath: breadcrumb array
- fileList: array of { fileName, fileSize, uploadedAt, versionNumber }
- searchTerm: string
- sortBy: name | uploadedAt | fileSize
- sortOrder: asc | desc
- userRole: string (controls which action buttons are visible)

**Behaviors:**
- `loadFolders()` → calls Folder Manager listAccessibleFolders; displays navigable folder tree
- `navigateToFolder(folderId)` → updates currentFolderId, loads files
- `navigateUp()` → goes to parent folder
- `loadFiles()` → calls File Manager listFiles for currentFolderId with sort params
- `searchFiles(term)` → calls File Manager searchFiles across accessible folders
- `sortFiles(sortBy, sortOrder)` → re-requests or re-sorts file list
- `showVersionHistory(fileName)` → calls File Manager getVersionHistory, opens version panel
- `uploadFile(file)` → (admin/uploader only) validates size ≤ 1GB client-side, calls File Manager generateUploadUrl, uploads directly to S3 via pre-signed URL
- `downloadFile(fileName, versionNumber?)` → (admin/reader only) calls File Manager generateDownloadUrl, triggers browser download via pre-signed URL

**Collaborators:** Folder Manager, File Manager, File Storage (via pre-signed URLs)

---

## 3. Shared / Cross-Cutting Components

### 3.1 Session Manager

**Attributes:**
- session: { sessionToken, username, role, createdAt, ttl }

**Behaviors:**
- `createSession(username, role)` → generates token, stores in DynamoDB with TTL
- `validateSession(sessionToken)` → looks up session in DynamoDB, returns { username, role } or rejects with 401
- `deleteSession(sessionToken)` → removes session from DynamoDB
- `deleteSessionsForUser(username)` → removes all sessions for a user (used on user delete)

**Collaborators:** DynamoDB (FileShareTable)

---

### 3.2 Role-Based Access Control (RBAC)

Enforces permissions at both API and UI levels.

**Attributes:**
- Permission matrix:
  - Admin: all operations
  - Uploader: view folders + view files + upload files (assigned folders only)
  - Reader: view folders + view files + download files (assigned folders only)
  - Viewer: view folders + view files (assigned folders only)

**Behaviors:**
- `requireRole(sessionToken, allowedRoles[])` → validates session and checks role is in allowed list; returns 403 if not
- `requireFolderAccess(username, folderId)` → checks user has an assignment to the folder (admin bypasses)
- `getVisibleActions(role)` → returns which UI actions (upload, download) to show for a role

**Collaborators:** Session Manager, Assignment Manager

---

### 3.3 API Router

Maps HTTP requests to the correct backend component. Implemented as API Gateway + Lambda routing.

**Attributes:**
- Route table:
  - `/auth/*` → Auth Service
  - `/users/*` → User Manager
  - `/folders/*` → Folder Manager + Assignment Manager
  - `/files/*` → File Manager

**Behaviors:**
- `route(method, path, body, sessionToken)` → validates session (except /auth/login), enforces RBAC, dispatches to the correct component
- `returnError(statusCode, message)` → standardized error responses (400, 401, 403, 404, 500)

**Collaborators:** RBAC, all backend components

---

### 3.4 Data Repository (DynamoDB Single-Table)

Shared persistence layer. All entities live in one DynamoDB table (`FileShareTable`).

**Attributes:**
- tableName: `FileShareTable`
- PK / SK key schema
- GSI-1: all users lookup
- GSI-2: parent-child folder lookup
- GSI-3: folder-to-user assignment lookup
- GSI-4: cross-folder file search

**Entity types stored:**
- User: `PK=USER#<username>, SK=USER#<username>`
- Session: `PK=SESSION#<token>, SK=SESSION#<token>`
- Folder: `PK=FOLDER#<folderId>, SK=FOLDER#<folderId>`
- Assignment: `PK=USER#<username>, SK=FOLDER#<folderId>`
- File (version): `PK=FOLDER#<folderId>, SK=FILE#<name>#VERSION#<n>`
- File (latest pointer): `PK=FOLDER#<folderId>, SK=FILE#<name>`

**Behaviors:**
- Standard CRUD: `put`, `get`, `query`, `delete`, `batchWrite`
- Handles Decimal → int conversion for JSON serialization

**Collaborators:** AWS DynamoDB

---

## 4. Component Interaction Flows

### US-001: User Login
`Login Page` → `Auth Service.login()` → `Data Repository` (get User, verify password) → `Session Manager.createSession()` → `Data Repository` (put Session) → return token to `Login Page` → navigate to `App Shell`

### US-002: User Logout
`App Shell.logout()` → `Auth Service.logout()` → `Session Manager.deleteSession()` → `Data Repository` (delete Session) → redirect to `Login Page`

### US-003: Session Validation
`API Router.route()` → `RBAC.requireRole()` → `Session Manager.validateSession()` → `Data Repository` (get Session) → allow or reject (401)

### US-004: Password Reset
`Change Password Modal` → `Auth Service.changePassword()` → `Data Repository` (get User, verify current password, update hash, clear mustChangePassword)

### US-005: Initial Admin Account
Deployment trigger → `Auth Service.seedAdmin()` → `Data Repository` (put User with admin role, mustChangePassword=true)

### US-006: Create User
`User Admin Page.createUser()` → `User Manager.createUser()` → `RBAC.requireRole(admin)` → `Data Repository` (put User) → optionally `Assignment Manager.assignFolders()`

### US-007: Update User
`User Admin Page.updateUser()` → `User Manager.updateUser()` → `RBAC.requireRole(admin)` → `Data Repository` (update User)

### US-008: Delete User
`User Admin Page.deleteUser()` → `User Manager.deleteUser()` → `RBAC.requireRole(admin)` → `Data Repository` (delete User) → `Assignment Manager` (delete all assignments) → `Session Manager.deleteSessionsForUser()`

### US-009: List Users
`User Admin Page.loadUsers()` → `User Manager.listUsers()` → `RBAC.requireRole(admin)` → `Data Repository` (query GSI-1 for all users, query assignments per user)

### US-010: Create Folder
`Folder Admin Page.createFolder()` → `Folder Manager.createFolder()` → `RBAC.requireRole(admin)` → `Data Repository` (check duplicate name in parent via GSI-2, put Folder)

### US-011: Delete Folder
`Folder Admin Page.deleteFolder()` → `Folder Manager.deleteFolder()` → `RBAC.requireRole(admin)` → `Data Repository` (query children via GSI-2, recursively delete Folders + Files + Assignments) → `File Storage.deleteFolder()` (delete S3 objects)

### US-012: List Folders
`Folder Admin Page.loadFolderTree()` → `Folder Manager.listAllFolders()` → `RBAC.requireRole(admin)` → `Data Repository` (query GSI-1 for all folders, query GSI-3 for users per folder)

### US-013: Assign Folders to User (Bulk)
`Folder Admin Page.assignFolders()` → `Assignment Manager.assignFolders()` → `RBAC.requireRole(admin)` → `Data Repository` (batchWrite Assignment entities)

### US-014: Unassign Folders from User (Bulk)
`Folder Admin Page.unassignFolders()` → `Assignment Manager.unassignFolders()` → `RBAC.requireRole(admin)` → `Data Repository` (batchWrite delete Assignment entities)

### US-015: Browse Folders
`File Browser Page.loadFolders()` → `Folder Manager.listAccessibleFolders()` → `RBAC.requireFolderAccess()` → `Data Repository` (query assignments for user, then query folder details) → display navigable tree

### US-016: Browse Files in a Folder
`File Browser Page.loadFiles()` → `File Manager.listFiles(folderId)` → `RBAC.requireFolderAccess()` → `Data Repository` (query PK=FOLDER#folderId, SK begins_with FILE#, filter to latest pointers) → return sorted list

### US-017: Search Files by Name
`File Browser Page.searchFiles()` → `File Manager.searchFiles(term, accessibleFolderIds)` → `Data Repository` (query GSI-4, filter by accessible folders) → return matching files

### US-018: Sort Files
`File Browser Page.sortFiles()` → `File Manager.listFiles(folderId, sortBy, sortOrder)` → `Data Repository` (query files) → sort in Lambda → return sorted list

### US-019: Upload File
`File Browser Page.uploadFile()` → client-side size check → `File Manager.generateUploadUrl()` → `RBAC.requireRole(admin|uploader)` + `RBAC.requireFolderAccess()` → `Data Repository` (get latest version, increment, put File version + update latest pointer) → `File Storage.generatePresignedUploadUrl()` → return URL → `File Browser Page` uploads directly to S3

### US-020: File Size Limit
`File Browser Page.uploadFile()` → client-side check (fileSize ≤ 1GB, reject with error if over) → `File Manager.generateUploadUrl()` → server-side check (reject if fileSize > 1GB) → pre-signed URL includes content-length condition

### US-021: File Versioning
`File Manager.generateUploadUrl()` → `Data Repository` (query latest pointer for file, increment version) → `Data Repository` (put new File version entity, update latest pointer) → return new version number with upload URL

### US-022: Download File
`File Browser Page.downloadFile()` → `File Manager.generateDownloadUrl()` → `RBAC.requireRole(admin|reader)` + `RBAC.requireFolderAccess()` → `Data Repository` (get latest pointer, resolve S3 key) → `File Storage.generatePresignedDownloadUrl()` → return URL → browser downloads

### US-023: Download Specific Version
`File Browser Page.downloadFile(versionNumber)` → `File Manager.generateDownloadUrl(folderId, fileName, versionNumber)` → `RBAC.requireRole(admin|reader)` → `Data Repository` (get specific version entity, resolve S3 key) → `File Storage.generatePresignedDownloadUrl()` → return URL

### US-024: View File Metadata (Viewer)
`File Browser Page.loadFiles()` → `File Manager.listFiles()` → `RBAC.requireFolderAccess()` → returns file metadata → `File Browser Page` renders file list → `RBAC.getVisibleActions(viewer)` → hides upload and download buttons → API returns 403 if viewer attempts upload/download directly
