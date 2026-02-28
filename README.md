# S3 File-Sharing System

A web-based file-sharing system backed by S3, with DynamoDB for state management and a React frontend.

## Prerequisites

- Python 3.12
- Node.js 25+
- AWS SAM CLI
- AWS credentials configured

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
