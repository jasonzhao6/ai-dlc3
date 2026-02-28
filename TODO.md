# Post-Deployment TODO

## Deployment Steps

1. Deploy backend:
   ```
   cd backend
   sam build
   sam deploy --guided --stack-name file-share
   ```

2. Note the API URL from the stack outputs

3. Rebuild frontend with API URL:
   ```
   cd frontend
   REACT_APP_API_URL=<ApiUrl from outputs> npm run build
   ```

4. Upload frontend to S3:
   ```
   aws s3 sync frontend/build/ s3://<stack-name>-frontend/ --delete
   ```

5. Seed admin account:
   ```
   curl -X POST <ApiUrl>/auth/seed-admin
   ```

## Post-Deploy Verification

- [ ] Call POST /auth/seed-admin — create initial admin account
- [ ] Call POST /auth/login with admin/ChangeMe123! — verify login works
- [ ] Call POST /auth/change-password — change admin password
- [ ] Call POST /users — create a test user with each role
- [ ] Call GET /users — verify user list
- [ ] Call POST /folders — create root and nested folders
- [ ] Call GET /folders — verify folder tree
- [ ] Call POST /folders/assignments — assign folders to users
- [ ] Call POST /files/upload-url — get upload URL and upload a file
- [ ] Call GET /files?folderId=... — verify file listing
- [ ] Call GET /files?search=... — verify search
- [ ] Call POST /files/download-url — verify download URL generation
- [ ] Call POST /files/download-url as uploader — verify 403
- [ ] Call POST /files/download-url as viewer — verify 403
- [ ] Call POST /files/upload-url as reader — verify 403
- [ ] Read CloudWatch logs for each Lambda to verify no startup errors
- [ ] Verify CORS headers are returned correctly
- [ ] Access frontend URL and test full UI flow

## Known Issues
(none yet)
