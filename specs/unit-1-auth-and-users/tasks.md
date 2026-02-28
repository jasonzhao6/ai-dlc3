# Unit 1 — Auth & User Management: Tasks

## Infrastructure

- [x] Create SAM template with DynamoDB table (single-table, PK/SK, GSI-1, TTL enabled)
- [x] Create API Gateway REST API resource in SAM template
- [x] Create S3 bucket for React frontend hosting in SAM template

## Backend — Auth Lambda

- [x] Implement `session_util.py` — shared module for session validation and role-based access control
- [x] Implement POST /auth/login — validate credentials, create session, return token
- [x] Implement POST /auth/logout — delete session from DynamoDB
- [x] Implement POST /auth/change-password — verify current password, update hash, clear mustChangePassword flag
- [x] Implement initial admin account creation on first deployment
- [x] Test: HTTPS call to POST /auth/login with valid and invalid credentials
- [x] Test: HTTPS call to POST /auth/logout and verify session invalidated
- [x] Test: HTTPS call to POST /auth/change-password

## Backend — Users Lambda

- [x] Implement POST /users — admin-only, create user with role
- [x] Implement GET /users — admin-only, list all users with roles and assignments
- [x] Implement PUT /users/{username} — admin-only, update role or password
- [x] Implement DELETE /users/{username} — admin-only, delete user + assignments + sessions
- [x] Test: HTTPS call to POST /users to create a user
- [x] Test: HTTPS call to GET /users to list users
- [x] Test: HTTPS call to PUT /users/{username} to update a user
- [x] Test: HTTPS call to DELETE /users/{username} to delete a user

## Frontend

- [x] Set up React project with routing (React Router)
- [x] Build LoginPage component — login form, call POST /auth/login, store session token
- [x] Build ChangePasswordModal component — shown on mustChangePassword, also accessible from nav
- [x] Build AppLayout component — nav bar with logout, role-based menu items
- [x] Build UserManagementPage component — admin-only, list/create/update/delete users
- [ ] Deploy React build to S3 frontend bucket
