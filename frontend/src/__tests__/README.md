# RAG Frontend Tests

This directory contains all frontend test files for the RAG application.

## Test Files

- `test-api-integration.js` - General API integration tests
- `test-documents-api.js` - Document management API tests
- `test-ingestion-api.js` - Document ingestion API tests
- `test-responsible-api.js` - Responsible AI API tests
- `test-security-api.js` - Security groups API tests

## Running Tests

```bash
# Install test dependencies
npm install

# Run all tests
npm run test:all

# Run specific test
npm run test:documents
npm run test:ingestion
npm run test:responsible
npm run test:security
npm run test:api
```

## Test Configuration

Tests use the backend URL configured in the global config. Make sure the backend server is running before executing tests.

## Requirements

- Node.js 16+
- Backend server running on http://localhost:8000
