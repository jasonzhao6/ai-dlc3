# Unit 1 — Auth & User Management: Tasks

## Infrastructure

- [ ] Create SAM template with DynamoDB table (single-table, PK/SK, GSI-1, TTL enabled)
- [ ] Create API Gateway REST API resource in SAM template
- [ ] Create S3 bucket for React frontend hosting in SAM template

## Backend — Auth Lambda

- [ ] Implement `session_util.py` — shared module for session validation and role-based access control
- [ ] Implement POST /auth/login — validate credentials, create session, return token
- [ ] Implement POST /auth/logout — delete session from DynamoDB
- [ ] Implement POST /auth/change-password — verify current password, update hash, clear mustChangePassword flag
- [ ] Implement initial admin account creation on first deployment
- [ ] Test: HTTPS call to POST /auth/login with valid and invalid credentials
- [ ] Test: HTTPS call to POST /auth/logout and verify session invalidated
- [ ] Test: HTTPS call to POST /auth/change-password

## Backend — Users Lambda

- [ ] Implement POST /users — admin-only, create user with role
- [ ] Implement GET /users — admin-only, list all users with roles and assignments
- [ ] Implement PUT /users/{username} — admin-only, update role or password
- [ ] Implement DELETE /users/{username} — admin-only, delete user + assignments + sessions
- [ ] Test: HTTPS call to POST /users to create a user
- [ ] Test: HTTPS call to GET /users to list users
- [ ] Test: HTTPS call to PUT /users/{username} to update a user
- [ ] Test: HTTPS call to DELETE /users/{username} to delete a user

## Frontend

- [ ] Set up React project with routing (React Router)
- [ ] Build LoginPage component — login form, call POST /auth/login, store session token
- [ ] Build ChangePasswordModal component — shown on mustChangePassword, also accessible from nav
- [ ] Build AppLayout component — nav bar with logout, role-based menu items
- [ ] Build UserManagementPage component — admin-only, list/create/update/delete users
- [ ] Deploy React build to S3 frontend bucket
