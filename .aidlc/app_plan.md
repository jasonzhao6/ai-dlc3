# Application Build Plan

## Environment
- Python 3.12, SAM CLI 1.154.0, Node 25.6.1, npm 11.9.0
- No containers — use local Python runtime for SAM

## Deliverables
- `backend/template.yaml` — SAM template (DynamoDB, API Gateway, Lambdas, S3 buckets)
- `backend/layers/shared/` — Lambda layer with shared modules (session_util, db_util, response_util)
- `backend/functions/auth/` — Auth Lambda (login, logout, change-password, seed admin)
- `backend/functions/users/` — Users Lambda (CRUD)
- `backend/functions/folders/` — Folders Lambda (CRUD + assignments)
- `backend/functions/files/` — Files Lambda (list, search, upload-url, download-url, versions)
- `backend/scripts/verify_layer.sh` — Layer structure verification script
- `frontend/` — React app with Bootstrap styling
- `TODO.md` — Post-deployment tasks tracker

## Plan

### Phase 1: Project Scaffolding & Infrastructure

- [x] **Step 1:** Create project structure, SAM template with all resources (DynamoDB table + 4 GSIs, API Gateway, 4 Lambdas, S3 buckets, Lambda layer), and layer verification script

### Phase 2: Backend — Unit 1 (Auth & Users)

- [x] **Step 2:** Build shared Lambda layer (session_util, db_util, response_util)
- [x] **Step 3:** Build Auth Lambda (login, logout, change-password, seed-admin) and test with SAM local
- [x] **Step 4:** Build Users Lambda (create, list, update, delete) and test with SAM local

### Phase 3: Backend — Unit 2 (Folders & Assignments)

- [x] **Step 5:** Build Folders Lambda (create, list, delete, assign, unassign) and test with SAM local

### Phase 4: Backend — Unit 3 (File Upload & Browsing)

- [x] **Step 6:** Build Files Lambda — list, search, versions, upload-url — and test with SAM local

### Phase 5: Backend — Unit 4 (File Download)

- [x] **Step 7:** Extend Files Lambda — download-url with role enforcement — and test with SAM local

### Phase 6: Frontend

- [x] **Step 8:** Scaffold React app with Bootstrap, routing, auth context, and App Shell
- [x] **Step 9:** Build LoginPage and ChangePasswordModal components
- [x] **Step 10:** Build UserManagementPage (admin-only)
- [x] **Step 11:** Build FolderManagementPage with assignment panel (admin-only)
- [x] **Step 12:** Build FileBrowserPage — folder navigation, file list, search, sort, upload, download, version history
- [x] **Step 13:** Run `npm run build` and finalize TODO.md with post-deployment tasks
