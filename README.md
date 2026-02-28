# S3 File-Sharing System

A web-based file-sharing system backed by S3, with DynamoDB for state management and a React frontend.

## Prerequisites

- Python 3.12
- Node.js 25+
- AWS SAM CLI
- AWS credentials configured

## Running Locally

**Easiest path (deploy backend, run frontend locally):**

```bash
# 1. Deploy backend to AWS
cd backend
sam build
sam deploy --guided

# 2. Note the ApiUrl from stack outputs

# 3. Seed the admin account
curl -X POST <ApiUrl>/auth/seed-admin

# 4. Run frontend locally
cd frontend
npm install
REACT_APP_API_URL=<ApiUrl> npm start

# 5. Open http://localhost:3000 and login with admin / ChangeMe123!
```

**Fully local (requires Docker for SAM + DynamoDB Local):**

```bash
# 1. Start DynamoDB Local (skip if already running: docker ps | grep dynamodb)
docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local

# 2. Start SAM local API
cd backend
sam build
sam local start-api --env-vars <(echo '{"Parameters": {"TABLE_NAME": "local-table", "FILE_BUCKET": "local-bucket"}}')

# 3. Run frontend pointing to local API
cd frontend
PORT=3001 REACT_APP_API_URL=http://localhost:3000 npm start
```

Note: SAM local start-api uses Docker containers to emulate Lambda. DynamoDB and S3 calls go to real AWS unless you configure local endpoints.

## Running Tests

```bash
# Install test dependencies
pip install pytest moto boto3

# Run all tests (unit + integration)
cd backend
python -m pytest tests/ -v

# Run only unit tests
python -m pytest tests/test_unit_shared.py -v

# Run only integration tests
python -m pytest tests/test_integration_auth.py tests/test_integration_users.py tests/test_integration_folders.py tests/test_integration_files.py -v
```

## Building

```bash
# Backend
cd backend
sam build

# Frontend
cd frontend
npm install
REACT_APP_API_URL=<your-api-url> npm run build
```

## Deployment

See [TODO.md](TODO.md) for full deployment steps and post-deploy verification checklist.
