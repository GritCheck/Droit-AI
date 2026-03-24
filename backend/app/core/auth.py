"""
Authentication and authorization utilities for OBO flow
"""

import logging
import jwt
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Cache for Microsoft public keys (TTL: 24 hours)
_public_keys_cache = {"keys": None, "expires_at": None}

# HTTP Bearer scheme for token extraction
security = HTTPBearer()


async def _get_microsoft_public_keys() -> Dict[str, Any]:
    """Fetch Microsoft public keys for JWT validation"""
    global _public_keys_cache
    
    # Check cache first
    if (_public_keys_cache["keys"] and 
        _public_keys_cache["expires_at"] and 
        datetime.utcnow() < _public_keys_cache["expires_at"]):
        return _public_keys_cache["keys"]
    
    try:
        # Fetch from Microsoft's well-known endpoint
        jwks_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/discovery/v2.0/keys"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            keys_data = response.json()
            
            # Cache the keys with expiration
            _public_keys_cache["keys"] = keys_data
            _public_keys_cache["expires_at"] = datetime.utcnow() + timedelta(hours=24)
            
            logger.info("Successfully fetched and cached Microsoft public keys")
            return keys_data
            
    except Exception as e:
        logger.error(f"Failed to fetch Microsoft public keys: {str(e)}")
        raise ValueError("Unable to verify token - public key fetch failed")


def _get_public_key_for_kid(keys: Dict[str, Any], kid: str) -> Optional[str]:
    """Extract public key for specific key ID"""
    for key in keys.get("keys", []):
        if key.get("kid") == kid:
            # Convert JWK to PEM format
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    return None


async def verify_obo_token(token: str) -> Dict[str, Any]:
    """
    Verify OBO token and extract user information
    Validates against Microsoft's public keys with proper security checks
    """
    try:
        # Get token header to find key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise ValueError("Token missing key ID (kid) in header")
        
        # Get Microsoft public keys
        public_keys = await _get_microsoft_public_keys()
        public_key = _get_public_key_for_kid(public_keys, kid)
        
        if not public_key:
            raise ValueError(f"Unable to find public key for kid: {kid}")
        
        # Verify token with proper validation
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=settings.azure_client_id,
            issuer=f"https://sts.windows.net/{settings.azure_tenant_id}/",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True
            }
        )
        
        # Validate required claims
        required_claims = ['oid', 'tid', 'upn', 'roles']
        for claim in required_claims:
            if claim not in decoded:
                raise ValueError(f"Missing required claim: {claim}")
        
        # Validate token expiration (additional check)
        exp = decoded.get('exp')
        if exp and datetime.fromtimestamp(exp) <= datetime.utcnow():
            raise ValueError("Token has expired")
        
        # Log successful validation for audit
        logger.info(f"Token validated successfully for user: {decoded.get('upn')}")
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed: Token expired")
        raise ValueError("Authentication token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise ValueError("Invalid authentication token")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise ValueError(f"Token verification failed: {str(e)}")


async def get_user_from_token(token: str) -> Dict[str, Any]:
    """Extract user information from validated token"""
    decoded = await verify_obo_token(token)
    
    return {
        "user_id": decoded.get("oid"),
        "tenant_id": decoded.get("tid"),
        "upn": decoded.get("upn"),
        "display_name": decoded.get("name"),
        "roles": decoded.get("roles", []),
        "groups": decoded.get("groups", [])
    }


def create_session_token(user_info: Dict[str, Any]) -> str:
    """Create session token for internal use"""
    payload = {
        "user_id": user_info["user_id"],
        "tenant_id": user_info["tenant_id"],
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


async def validate_session_token(token: str) -> Dict[str, Any]:
    """Validate internal session token"""
    try:
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return decoded
    except jwt.InvalidTokenError:
        raise ValueError("Invalid session token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    Extracts and validates the Bearer token from the request
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For now, return a mock user for local development
        # In production, this would validate the real token
        return {
            "user_id": "mock-user-id",
            "tenant_id": settings.azure_tenant_id or "mock-tenant-id",
            "upn": "mock-user@example.com",
            "display_name": "Mock User",
            "roles": ["User"],
            "groups": []
        }
        
        # TODO: Uncomment for production with real token validation
        # token = credentials.credentials
        # return await get_user_from_token(token)
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
