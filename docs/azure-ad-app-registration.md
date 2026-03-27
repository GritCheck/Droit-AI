# Azure AD App Registration Setup

This guide explains how to configure Azure AD app registrations for the Droit AI RAG system.

## Overview

The Droit AI system uses two separate Azure AD app registrations:

1. **Frontend App Registration** - For the React frontend application
2. **Backend App Registration** - For the FastAPI backend service

## Prerequisites

- Azure AD tenant with admin privileges
- Azure subscription with appropriate permissions
- PowerShell or Azure CLI installed

## Frontend App Registration

### 1. Create Frontend App Registration

```bash
# Using Azure CLI
az ad app create \
  --display-name "Droit AI Frontend" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "http://localhost:3000/auth/callback" "https://<frontend-app-name>.azurewebsites.net/auth/callback" \
  --required-resource-accesses @frontend-manifest.json
```

### 2. Frontend Configuration

Create `frontend-manifest.json`:
```json
{
  "resourceAppId": "00000003-0000-0000-c000-000000000000",
  "resourceAccess": [
    {
      "id": "e1fe84dd-3fd4-4c5b-9d3b-6c8c18b5ec2d",
      "type": "Scope",
      "principal": "User"
    },
    {
      "id": "37f7f235-527c-4136-8c7d-55d666d7b1f1", 
      "type": "Scope",
      "principal": "User"
    }
  ]
}
```

### 3. Frontend Environment Variables

```bash
# .env.local (frontend)
NEXT_PUBLIC_AZURE_CLIENT_ID=<frontend-app-id>
NEXT_PUBLIC_AZURE_TENANT_ID=<tenant-id>
NEXT_PUBLIC_AZURE_AUTHORITY=https://login.microsoftonline.com
NEXT_PUBLIC_AZURE_REDIRECT_URI=http://localhost:3000/auth/callback
```

## Backend App Registration

### 1. Create Backend App Registration

```bash
# Using Azure CLI
az ad app create \
  --display-name "Droit AI Backend" \
  --sign-in-audience AzureADMyOrg \
  --identifier-uris "api://<backend-app-name>" \
  --required-resource-accesses @backend-manifest.json
```

### 2. Backend Configuration

Create `backend-manifest.json`:
```json
{
  "resourceAppId": "00000003-0000-0000-c000-000000000000",
  "resourceAccess": [
    {
      "id": "7427e0e7-2c15-4af6-a3b2-3c0fb22611b9",
      "type": "Scope",
      "principal": "Application"
    },
    {
      "id": "e1fe84dd-3fd4-4c5b-9d3b-6c8c18b5ec2d",
      "type": "Scope", 
      "principal": "Application"
    }
  ]
}
```

### 3. Expose API Scopes

```bash
# Get backend app ID
BACKEND_APP_ID=$(az ad app list --display-name "Droit AI Backend" --query "[0].appId" -o tsv)

# Expose API scope
az ad app update \
  --id $BACKEND_APP_ID \
  --identifier-uris "api://$BACKEND_APP_ID" \
  --required-resource-accesses @backend-manifest.json
```

## Permission Grants & Admin Consent

### 1. Grant Admin Consent (Required)

```bash
# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

# Grant admin consent for frontend
az ad app permission admin-consent --id <frontend-app-id>

# Grant admin consent for backend  
az ad app permission admin-consent --id <backend-app-id>
```

### 2. Verify Permissions

```bash
# Check frontend permissions
az ad app show --id <frontend-app-id> --query "requiredResourceAccess"

# Check backend permissions
az ad app show --id <backend-app-id> --query "requiredResourceAccess"
```

## Service Principal Creation

### 1. Create Service Principals

```bash
# Frontend service principal
az ad sp create --id <frontend-app-id>

# Backend service principal
az ad sp create --id <backend-app-id>
```

### 2. Assign Roles (if needed)

```bash
# Assign Reader role to backend for storage access
az role assignment create \
  --assignee <backend-sp-id> \
  --role "Storage Blob Data Reader" \
  --scope <storage-account-id>
```

## Environment Configuration

### Frontend (.env.local)
```bash
NEXT_PUBLIC_AZURE_CLIENT_ID=<frontend-app-id>
NEXT_PUBLIC_AZURE_TENANT_ID=<tenant-id>
NEXT_PUBLIC_AZURE_AUTHORITY=https://login.microsoftonline.com
NEXT_PUBLIC_AZURE_REDIRECT_URI=http://localhost:3000/auth/callback
NEXT_PUBLIC_SERVER_URL=http://localhost:8000
```

### Backend (.env)
```bash
AZURE_CLIENT_ID=<backend-app-id>
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_SECRET=<backend-client-secret>
FRONTEND_APP_ID=<frontend-app-id>
```

## Testing the Setup

### 1. Frontend Authentication Test

```bash
# Start frontend
cd frontend
npm run dev

# Navigate to http://localhost:3000
# Click "Sign In" - should redirect to Azure AD
# After authentication, should return to app with user info
```

### 2. Backend Token Validation Test

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Test token endpoint
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"code": "<auth-code>", "redirect_uri": "http://localhost:3000/auth/callback"}'
```

## Common Issues & Solutions

### Issue: "AADSTS65001: The user or administrator has not consented"
**Solution**: Grant admin consent using the commands in the Permission Grants section.

### Issue: "AADSTS50011: The reply address specified does not match"
**Solution**: Ensure the redirect URI in app registration matches exactly with the frontend configuration.

### Issue: "AADSTS700016: Application with identifier was not found"
**Solution**: Verify the client ID is correct and the app registration exists in the correct tenant.

## Next Steps

1. [Permission Grants & Admin Consent](./permission-grants.md) - Detailed permission setup
2. [OBO Token Flow Architecture](./obo-token-flow.md) - Token exchange between services
3. [Managed Identity Configuration](./managed-identity.md) - Production authentication setup

## Support

For issues with Azure AD configuration:
- Check Azure Portal > Azure Active Directory > App registrations
- Review Azure AD sign-in logs
- Verify all environment variables are correctly set
