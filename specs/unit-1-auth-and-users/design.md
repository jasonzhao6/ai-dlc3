# Unit 1 — Auth & User Management: Design

## Technical Architecture

- **Backend:** Python Lambda behind API Gateway
- **Database:** DynamoDB (single-table design)
- **Frontend:** React JS static site hosted in S3
- **Auth:** Custom session-based auth (no Cognito/Okta)

## DynamoDB Single-Table Design

Table name: `FileShareTable`

Partition key: `PK` (String)
Sort key: `SK` (String)

### Entity Schemas

**User entity**
- PK: `USER#<username>`
- SK: `USER#<username>`
- Attributes: `username`, `passwordHash`, `role` (admin/uploader/reader/viewer), `createdAt`, `mustChangePassword` (boolean)

**Session entity**
- PK: `SESSION#<sessionToken>`
- SK: `SESSION#<sessionToken>`
- Attributes: `username`, `role`, `createdAt`, `ttl` (DynamoDB TTL for auto-expiry)

**GSI-1** (for querying all users)
- GSI1PK: `USERS`
- GSI1SK: `USER#<username>`

### Password Hashing
- Use `bcrypt` for password hashing
- Store only the hash, never plaintext

### Session Management
- Generate session token using `secrets.token_urlsafe(32)`
- Session TTL: 24 hours (configurable)
- DynamoDB TTL attribute for automatic cleanup of expired sessions

## API Design

All endpoints go through API Gateway → single Lambda function (`auth_handler`).

**POST /auth/login**
- Body: `{ "username": "...", "password": "..." }`
- Returns: `{ "sessionToken": "...", "role": "...", "mustChangePassword": true/false }`
- Creates session in DynamoDB

**POST /auth/logout**
- Header: `Authorization: Bearer <sessionToken>`
- Deletes session from DynamoDB

**POST /auth/change-password**
- Header: `Authorization: Bearer <sessionToken>`
- Body: `{ "currentPassword": "...", "newPassword": "..." }`
- Updates password hash, clears `mustChangePassword` flag

**POST /users**
- Header: `Authorization: Bearer <sessionToken>`
- Body: `{ "username": "...", "password": "...", "role": "..." }`
- Admin only. Creates user entity.

**GET /users**
- Header: `Authorization: Bearer <sessionToken>`
- Admin only. Returns list of all users with roles and folder assignments.

**PUT /users/{username}**
- Header: `Authorization: Bearer <sessionToken>`
- Body: `{ "role": "...", "password": "..." }` (both optional)
- Admin only. Updates user.

**DELETE /users/{username}**
- Header: `Authorization: Bearer <sessionToken>`
- Admin only. Deletes user, their assignments, and their sessions.

## Lambda Design

Per vision.md: consolidate CRUD operations into one Lambda function when applicable.

- `auth_handler` Lambda: handles `/auth/*` routes (login, logout, change-password)
- `users_handler` Lambda: handles `/users/*` routes (CRUD)

Both share a common `session_util.py` module for session validation and role checking.

## React Frontend Components

- `LoginPage` — username/password form, calls POST /auth/login
- `ChangePasswordModal` — shown on first login when `mustChangePassword` is true, also accessible from user menu
- `UserManagementPage` — admin-only page to list, create, update, delete users
- `AppLayout` — top-level layout with nav bar, logout button, wraps authenticated routes

## Initial Admin Account

- A separate setup Lambda (or a check within `auth_handler`) runs on first deployment
- Creates admin user with `username: admin`, a generated password, and `mustChangePassword: true`
- The generated password is output via CloudFormation/SAM output or written to a known SSM parameter

## SAM Template Resources (this unit)

- `FileShareTable` — DynamoDB table with PK/SK and GSI-1, TTL enabled
- `AuthFunction` — Lambda for auth routes
- `UsersFunction` — Lambda for user CRUD routes
- `ApiGateway` — API Gateway REST API with routes
- `FrontendBucket` — S3 bucket for React static site hosting
