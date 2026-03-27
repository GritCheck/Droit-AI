#!/usr/bin/env python3
"""
Generate a test JWT token for local development
"""

import jwt
from datetime import datetime, timedelta

# Use the same secret from .env file
JWT_SECRET = "dev-secret-key-change-in-production"

def create_test_token():
    """Create a test JWT token for local development"""
    payload = {
        "user_id": "test-user-123",
        "tenant_id": "test-tenant-456", 
        "upn": "testuser@example.com",
        "display_name": "Test User",
        "roles": ["User"],
        "groups": [],
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

if __name__ == "__main__":
    token = create_test_token()
    print("Test JWT Token:")
    print(token)
    print(f"\nUse this token in the 'Bearer' field at http://localhost:8000/docs")
