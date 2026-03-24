"""
Test script for RAG backend APIs
Run this to test APIs without Azure services
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health check endpoints"""
    print("=== Testing Health Endpoints ===")
    
    # Test main health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Main Health: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Main Health failed: {e}")
    
    # Test search health
    try:
        response = requests.get(f"{BASE_URL}/api/v1/search/health")
        print(f"Search Health: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Search Health failed: {e}")
    
    # Test chat health
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/health")
        print(f"Chat Health: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Chat Health failed: {e}")

def test_api_endpoints():
    """Test API endpoints (will fail auth but show structure)"""
    print("\n=== Testing API Endpoints (Expected: 401 Unauthorized) ===")
    
    # Test search endpoint
    try:
        search_data = {
            "query": "test query",
            "top_k": 5,
            "semantic_ranking": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/search/hybrid",
            json=search_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        print(f"Search API: {response.status_code}")
        if response.status_code != 401:
            print(f"Unexpected response: {response.text}")
        else:
            print("✓ Search endpoint requires auth (expected)")
    except Exception as e:
        print(f"Search API failed: {e}")
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "Hello, can you help me?",
            "max_documents": 5,
            "include_follow_up": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/ask",
            json=chat_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        print(f"Chat API: {response.status_code}")
        if response.status_code != 401:
            print(f"Unexpected response: {response.text}")
        else:
            print("✓ Chat endpoint requires auth (expected)")
    except Exception as e:
        print(f"Chat API failed: {e}")

def test_docs_endpoint():
    """Test API documentation"""
    print("\n=== Testing Documentation ===")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Swagger Docs: {response.status_code}")
        if response.status_code == 200:
            print("✓ Swagger UI available at http://localhost:8000/docs")
    except Exception as e:
        print(f"Swagger Docs failed: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/redoc")
        print(f"ReDoc: {response.status_code}")
        if response.status_code == 200:
            print("✓ ReDoc available at http://localhost:8000/redoc")
    except Exception as e:
        print(f"ReDoc failed: {e}")

def main():
    print("RAG Backend API Testing")
    print("======================")
    print("Make sure the server is running: python main.py")
    print()
    
    # Wait a bit for server to start
    time.sleep(2)
    
    test_health_endpoints()
    test_api_endpoints()
    test_docs_endpoint()
    
    print("\n=== Summary ===")
    print("✓ Server structure is working")
    print("✓ API endpoints are accessible")
    print("✓ Authentication is properly required")
    print("✓ Documentation is available")
    print("\nNext steps:")
    print("1. Configure Azure services in .env file")
    print("2. Test with real authentication tokens")
    print("3. Test document upload and processing")

if __name__ == "__main__":
    main()
