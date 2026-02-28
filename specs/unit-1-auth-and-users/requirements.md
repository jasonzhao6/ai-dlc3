# Unit 1 — Auth & User Management: Requirements

## User Stories

### US-001: User Login
- As a user, I want to log in with my username and password so that I can access the system.
- Acceptance Criteria:
  - User enters valid credentials and is redirected to the file browser
  - Invalid credentials show an error message
  - Session is created and stored in DynamoDB
  - Session token is returned to the client for subsequent requests

### US-002: User Logout
- As a user, I want to log out so that my session is terminated securely.
- Acceptance Criteria:
  - Session is removed from DynamoDB
  - User is redirected to the login page
  - Subsequent requests with the old session token are rejected

### US-003: Session Validation
- As the system, I want to validate session tokens on every request so that only authenticated users can access resources.
- Acceptance Criteria:
  - Every API request (except login) includes a session token
  - Invalid or expired tokens return a 401 response
  - Valid tokens allow the request to proceed

### US-004: Password Reset
- As a user, I want to reset my own password so that I can regain access or change my credentials.
- Acceptance Criteria:
  - Logged-in user can change their password by providing current and new password
  - Password is updated in DynamoDB
  - Existing session remains valid after password change

### US-005: Initial Admin Account
- As the system, I want to create a default admin account during initial deployment so that the system can be administered from day one.
- Acceptance Criteria:
  - Admin account is created automatically during first deployment
  - Admin can log in immediately after deployment
  - Admin is prompted to change the default password on first login

### US-006: Create User
- As an admin, I want to create new users with a specified role so that they can access the system.
- Acceptance Criteria:
  - Admin specifies username, password, and role (Uploader, Reader, or Viewer)
  - User is created in DynamoDB
  - Duplicate usernames are rejected with an error message
  - Folder assignments can optionally be set during creation

### US-007: Update User
- As an admin, I want to update a user's role or reset their password so that I can manage access.
- Acceptance Criteria:
  - Admin can change a user's role
  - Admin can reset a user's password
  - Changes are persisted in DynamoDB immediately

### US-008: Delete User
- As an admin, I want to delete a user so that they no longer have access to the system.
- Acceptance Criteria:
  - User record is removed from DynamoDB
  - All folder assignments for the user are removed
  - User's active sessions are invalidated
  - Deleted user cannot log in

### US-009: List Users
- As an admin, I want to view all users so that I can manage them.
- Acceptance Criteria:
  - Admin sees a list of all users with their roles
  - List shows folder assignments per user

## Dependencies
- None (this is the foundation unit)

## Depends On This
- Unit 2 (Folder Management & Assignments)
- Unit 3 (File Upload & Browsing)
- Unit 4 (File Download & Viewing)
