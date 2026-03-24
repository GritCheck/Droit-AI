# RAG Backend Tests

This directory contains all backend test files for the RAG application.

## Test Files

- `test_apis.py` - General API integration tests
- `test_dashboard_api.py` - Dashboard API specific tests
- `test_ingestion.py` - Document ingestion tests

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_apis.py

# Run with coverage
python -m pytest tests/ --cov=app

# Run with verbose output
python -m pytest tests/ -v
```

## Test Configuration

Make sure to set up the test environment variables in a `.env.test` file:

```env
BACKEND_URL=http://localhost:8000
DATABASE_URL=sqlite:///./test.db
```

## Requirements

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```
