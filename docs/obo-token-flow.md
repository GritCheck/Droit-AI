# OBO Token Flow Architecture

This guide explains the On-Behalf-Of (OBO) token flow architecture used in the Droit AI RAG system for secure token exchange between frontend and backend services.

## Overview

The OBO flow allows a backend service to call another service on behalf of the signed-in user, maintaining the user's identity and permissions throughout the request chain.

## Architecture Diagram

```
┌─────────────┐    Auth Code    ┌──────────────┐    Access Token    ┌─────────────┐
│   Frontend  │ ──────────────> │   Azure AD    │ ─────────────────> │   Frontend  │
│   (React)   │                 │               │                   │   (React)   │
└─────────────┘                 └──────────────┘                   └─────────────┘
        │                                │                                │
        │ Access Token                   │                                │
        │ (for Backend)                  │                                │
        ▼                                ▼                                ▼
┌─────────────┐    OBO Request    ┌──────────────┐    New Access Token ┌─────────────┐
│   Backend   │ ────────────────> │   Azure AD    │ ─────────────────> │   Backend  │
│ (FastAPI)   │                   │               │                   │ (FastAPI)   │
└─────────────┘                   └──────────────┘                   └─────────────┘
        │                                │                                │
        │ Backend Token                  │                                │
        │ (for AI Services)              │                                │
        ▼                                ▼                                ▼
┌─────────────┐    API Call       ┌──────────────┐    Response         ┌─────────────┐
│   AI Service │ ◀─────────────── │   Backend    │ ◀───────────────── │   Backend  │
│   (OpenAI)   │                   │ (FastAPI)    │                   │ (FastAPI)   │
└─────────────┘                   └──────────────┘                   └─────────────┘
```

## Token Flow Sequence

### 1. User Authentication (Frontend)

```typescript
// Frontend initiates authentication
const loginUrl = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/authorize?` +
  `client_id=${clientId}&` +
  `response_type=code&` +
  `redirect_uri=${redirectUri}&` +
  `scope=openid profile email User.Read api://${backendAppId}/access_as_user&` +
  `state=${state}`;

window.location.href = loginUrl;
```

### 2. Authorization Code Exchange

```typescript
// Frontend exchanges code for access token
const tokenResponse = await fetch('/api/v1/auth/callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: authCode,
    state: state,
    redirect_uri: redirectUri
  })
});

const { access_token, refresh_token } = await tokenResponse.json();
localStorage.setItem('azure_access_token', access_token);
```

### 3. OBO Token Request (Backend)

```python
# Backend requests OBO token for AI services
async def get_obo_token(user_access_token: str, scope: str) -> str:
    obo_request = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "assertion": user_access_token,
        "scope": scope,
        "requested_token_use": "on_behalf_of"
    }
    
    response = await httpx.post(
        f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token",
        data=obo_request
    )
    
    return response.json()["access_token"]
```

### 4. AI Service Call with OBO Token

```python
# Backend calls AI services with OBO token
async def call_openai_with_user_context(user_access_token: str, query: str):
    # Get OBO token for Microsoft Graph (to access user info)
    graph_token = await get_obo_token(user_access_token, "https://graph.microsoft.com/User.Read")
    
    # Get user context
    user_info = await get_user_info(graph_token)
    
    # Call OpenAI with user context
    openai_token = await get_obo_token(user_access_token, "https://cognitiveservices.azure.com/.default")
    
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are assisting {user_info['displayName']} ({user_info['email']})"},
            {"role": "user", "content": query}
        ],
        user=user_info['id']  # Track usage by user
    )
    
    return response
```

## Implementation Details

### Frontend Token Management

```typescript
// Token management service
class TokenManager {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  
  async getAccessToken(): Promise<string> {
    if (this.isTokenExpired()) {
      await this.refreshToken();
    }
    return this.accessToken!;
  }
  
  async refreshToken(): Promise<void> {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.refreshToken}`
      }
    });
    
    const tokens = await response.json();
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
  }
  
  private isTokenExpired(): boolean {
    if (!this.accessToken) return true;
    
    const payload = JSON.parse(atob(this.accessToken.split('.')[1]));
    return Date.now() >= payload.exp * 1000;
  }
}
```

### Backend OBO Service

```python
# OBO token service
class OBOService:
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.token_cache = {}
    
    async def get_obo_token(self, user_token: str, scope: str) -> str:
        cache_key = f"{hash(user_token)}_{scope}"
        
        # Check cache first
        if cache_key in self.token_cache:
            cached_token = self.token_cache[cache_key]
            if not self.is_token_expired(cached_token):
                return cached_token["access_token"]
        
        # Request new OBO token
        obo_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "assertion": user_token,
            "scope": scope,
            "requested_token_use": "on_behalf_of"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
                data=obo_data
            )
            
            if response.status_code != 200:
                raise Exception(f"OBO token request failed: {response.text}")
            
            token_data = response.json()
            
            # Cache token
            self.token_cache[cache_key] = token_data
            
            return token_data["access_token"]
    
    def is_token_expired(self, token_data: dict) -> bool:
        expires_on = int(token_data.get("expires_on", 0))
        return time.time() >= expires_on - 300  # 5-minute buffer
```

## Security Considerations

### 1. Token Validation

```python
# Validate incoming user token
async def validate_user_token(token: str) -> dict:
    try:
        # Decode JWT without verification first to get tenant info
        unverified_header = jwt.get_unverified_header(token)
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Verify token with Microsoft's public keys
        jwks = await get_microsoft_jwks()
        public_key = jwks[unverified_header["kid"]]
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=FRONTEND_APP_ID,
            issuer=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
        )
        
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### 2. Scope Validation

```python
# Validate token has required scopes
def validate_scopes(payload: dict, required_scopes: list) -> bool:
    token_scopes = payload.get("scp", "").split(" ")
    return all(scope in token_scopes for scope in required_scopes)
```

### 3. Token Caching Strategy

```python
# Secure token caching with TTL
class SecureTokenCache:
    def __init__(self):
        self.cache = {}
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]:
        async with self.lock:
            entry = self.cache.get(key)
            if entry and time.time() < entry["expires_at"]:
                return entry["token"]
            return None
    
    async def set(self, key: str, token: str, expires_in: int):
        async with self.lock:
            self.cache[key] = {
                "token": token,
                "expires_at": time.time() + expires_in - 300  # 5-min buffer
            }
```

## Error Handling

### Common OBO Flow Errors

```python
class OBOFlowError(Exception):
    def __init__(self, error_code: str, description: str):
        self.error_code = error_code
        self.description = description
        super().__init__(f"{error_code}: {description}")

# Error mapping
OBO_ERRORS = {
    "invalid_grant": "User token is invalid or expired",
    "unauthorized_client": "Backend app not authorized for OBO flow",
    "invalid_scope": "Requested scope not available",
    "interaction_required": "User interaction required (shouldn't happen in OBO)"
}

def handle_obo_error(response_data: dict):
    error_code = response_data.get("error", "unknown")
    description = OBO_ERRORS.get(error_code, response_data.get("error_description", "Unknown error"))
    
    if error_code == "invalid_grant":
        # User needs to re-authenticate
        raise HTTPException(status_code=401, detail="User session expired")
    else:
        raise OBOFlowError(error_code, description)
```

## Testing OBO Flow

### Unit Tests

```python
# Test OBO token generation
@pytest.mark.asyncio
async def test_obo_token_generation():
    obo_service = OBOService()
    
    # Mock user token
    mock_user_token = "mock_jwt_token"
    
    # Mock HTTP response
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "access_token": "obo_token",
            "expires_in": 3600
        }
        
        obo_token = await obo_service.get_obo_token(mock_user_token, "https://graph.microsoft.com/User.Read")
        
        assert obo_token == "obo_token"
        mock_post.assert_called_once()
```

### Integration Tests

```python
# Test full OBO flow
@pytest.mark.asyncio
async def test_full_obo_flow():
    # 1. Get user token (mock authentication)
    user_token = await authenticate_test_user()
    
    # 2. Get OBO token
    obo_token = await obo_service.get_obo_token(user_token, "https://graph.microsoft.com/User.Read")
    
    # 3. Call downstream service
    user_info = await get_user_info(obo_token)
    
    assert user_info["displayName"] == "Test User"
```

## Performance Optimization

### 1. Token Caching
- Cache OBO tokens with appropriate TTL
- Implement token refresh logic
- Use memory-efficient caching strategies

### 2. Batch Token Requests
- Request multiple scopes in single OBO request when possible
- Pre-warm token cache for common operations

### 3. Connection Pooling
```python
# HTTP client with connection pooling
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    timeout=30.0
)
```

## Monitoring & Logging

### 1. Token Flow Metrics
```python
# Track OBO token requests
import time
from prometheus_client import Counter, Histogram

obo_requests = Counter('obo_requests_total', ['scope', 'status'])
obo_duration = Histogram('obo_request_duration_seconds')

async def get_obo_token_with_metrics(user_token: str, scope: str) -> str:
    start_time = time.time()
    
    try:
        token = await get_obo_token(user_token, scope)
        obo_requests.labels(scope=scope, status='success').inc()
        return token
    except Exception as e:
        obo_requests.labels(scope=scope, status='error').inc()
        raise
    finally:
        obo_duration.observe(time.time() - start_time)
```

### 2. Security Logging
```python
# Log security events
import logging

security_logger = logging.getLogger('security')

def log_token_event(event_type: str, user_id: str, scope: str, success: bool):
    security_logger.info(json.dumps({
        "event": event_type,
        "user_id": user_id,
        "scope": scope,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }))
```

## Next Steps

1. [Managed Identity Configuration](./managed-identity.md) - Production authentication setup
2. [Azure Architecture Overview](./azure-architecture.md) - Complete system overview
3. [Microservices Design](./microservices.md) - Service architecture details

## References

- [Microsoft OBO Flow Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow)
- [OAuth 2.0 Token Exchange](https://tools.ietf.org/html/rfc8693)
- [Azure AD Token Reference](https://docs.microsoft.com/en-us/azure/active-directory/develop/access-tokens)
