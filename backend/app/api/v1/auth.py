"""
Azure AD Authentication API endpoints
"""

import logging
import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

settings = get_settings()

# ----------------------------------------------------------------------

class TokenRequest(BaseModel):
    code: str
    state: str
    session_state: Optional[str] = None
    redirect_uri: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: Optional[Dict[str, Any]] = None

class UserInfo(BaseModel):
    id: str
    displayName: str
    email: str
    role: str
    photoURL: Optional[str] = None

# ----------------------------------------------------------------------

@router.post("/callback", response_model=TokenResponse)
async def azure_callback(token_request: TokenRequest):
    try:
        # 1. Exchange code for token
        token_data = {
            "client_id": settings.azure_client_id, 
            "client_secret": settings.azure_client_secret, 
            "code": token_request.code,
            "redirect_uri": token_request.redirect_uri,
            "grant_type": "authorization_code",
            # Requesting the backend scope + openid info
            "scope": f"openid profile email api://{settings.azure_client_id}/access_as_user"
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Token exchange failed")

            token_info = token_response.json()
            access_token = token_info.get("access_token")
            id_token = token_info.get("id_token") # Contains user profile info

            # 2. Decode token locally (No more 'Invalid Audience' Graph errors!)
            # We use verify_signature=False here because we trust the HTTPS response from Azure
            decoded_id = jwt.decode(id_token, options={"verify_signature": False})
            decoded_access = jwt.decode(access_token, options={"verify_signature": False})

            # 3. Extract Security Groups for RAG
            # These are the IDs for HR, Legal, etc. that you created in PowerShell
            user_groups = decoded_access.get("groups", [])
            logger.info(f"User authenticated with groups: {user_groups}")

            user_data = {
                "id": decoded_id.get("oid") or decoded_id.get("sub"),
                "displayName": decoded_id.get("name"),
                "email": decoded_id.get("preferred_username") or decoded_id.get("email"),
                "role": "user",
                "groups": user_groups  # Pass this to the frontend/state
            }

            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=token_info.get("expires_in", 3600),
                user=user_data
            )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")
# ----------------------------------------------------------------------

@router.get("/me", response_model=UserInfo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user information from access token
    """
    try:
        token = credentials.credentials

        # Decode token locally (same approach as callback)
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return UserInfo(
            id=decoded.get("oid") or decoded.get("sub", ""),
            displayName=decoded.get("name", ""),
            email=decoded.get("preferred_username") or decoded.get("email", ""),
            role="user",  # Default role
            photoURL=None
        )

    except Exception as e:
        logger.error(f"Unexpected error during user info fetch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

# ----------------------------------------------------------------------

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token (simplified implementation)
    """
    try:
        # In a real implementation, you would use the refresh token
        # For now, we'll just validate the current token and return it
        token = credentials.credentials

        # Validate token with Azure AD (simplified)
        async with httpx.AsyncClient() as client:
            user_info_response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired access token"
                )

            # Return the same token (in production, implement proper refresh)
            return {"access_token": token}

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

# ----------------------------------------------------------------------

@router.get("/health")
async def auth_health():
    """Auth service health check"""
    return {
        "status": "healthy",
        "service": "DroitAI Auth Service",
        "provider": "Azure AD",
        "tenant_id": settings.azure_tenant_id
    }
