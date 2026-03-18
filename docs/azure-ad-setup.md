# Azure AD OBO Flow Setup Guide

## Overview
This guide walks through setting up Azure Active Directory with On-Behalf-Of (OBO) flow for the Sentinel RAG application.

## Prerequisites
- Azure AD tenant with admin privileges
- Two Azure AD app registrations (Frontend & Backend)

## Step 1: Create Backend App Registration
1. Navigate to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `Sentinel-RAG-Backend`
4. Supported account types: "Accounts in this organizational directory only"
5. Redirect URI: (None for backend)
6. Click "Register"

### Backend App Configuration
1. **Expose an API:**
   - Go to "Expose an API" → "Add a scope"
   - Scope name: `access_as_user`
   - Admin consent display name: `Access Sentinel RAG Backend`
   - Description: `Allows the frontend to access the backend API`

2. **Authentication:**
   - Go to "Authentication"
   - Supported account types: "Accounts in any organizational directory"
   - Add platform: "Web"
   - Redirect URI: `http://localhost:8000/auth/callback`

3. **Certificates & secrets:**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: `Backend secret`
   - Duration: 12 months
   - Copy the secret value immediately

## Step 2: Create Frontend App Registration
1. Navigate to App registrations → "New registration"
2. Name: `Sentinel-RAG-Frontend`
3. Supported account types: "Accounts in this organizational directory only"
4. Redirect URI: `http://localhost:3000/api/auth/callback/azure-ad`
5. Click "Register"

### Frontend App Configuration
1. **Authentication:**
   - Go to "Authentication"
   - Add platform: "Web"
   - Redirect URI: `http://localhost:3000/api/auth/callback/azure-ad`
   - Enable ID tokens: Yes
   - Allow access tokens: Yes

2. **API Permissions:**
   - Go to "API permissions" → "Add a permission"
   - Select "My APIs"
   - Choose `Sentinel-RAG-Backend`
   - Select permission: `access_as_user`
   - Click "Add permissions"
   - Grant admin consent

3. **Certificates & secrets:**
   - Create client secret (same as backend)
   - Copy the secret value

## Step 3: Update Environment Variables

### Backend Environment (.env)
```bash
# Azure AD OBO Flow
AZURE_CLIENT_ID=backend-app-client-id
AZURE_CLIENT_SECRET=backend-client-secret-value
AZURE_TENANT_ID=your-tenant-id
AZURE_AUTHORITY=https://login.microsoftonline.com/
AZURE_SCOPES=api://backend-app-client-id/access_as_user
```

### Frontend Environment (.env.local)
```bash
# NextAuth.js Azure AD
AZURE_AD_CLIENT_ID=frontend-app-client-id
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_SECRET=frontend-client-secret-value
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secure-secret
```

## Step 4: Test the OBO Flow

### Frontend Test
1. Start Next.js frontend: `npm run dev`
2. Navigate to `http://localhost:3000`
3. Click "Sign in with Azure AD"
4. Complete Azure AD login
5. Verify you receive an access token

### Backend Test
1. Start FastAPI backend: `uvicorn app.main:app --reload`
2. Use Postman/curl to test protected endpoint:
```bash
curl -H "Authorization: Bearer <access-token>" \
     http://localhost:8000/api/v1/chat
```

## Troubleshooting

### Common Issues
1. **"AADSTS70011: Invalid scope"**
   - Check that the scope matches exactly: `api://backend-client-id/access_as_user`

2. **"AADSTS65001: User consent required"**
   - Grant admin consent in API permissions

3. **"Invalid redirect URI"**
   - Ensure redirect URIs match exactly in Azure AD

4. **"Token validation failed"**
   - Verify the frontend is requesting the correct scope
   - Check that the backend app exposes the correct API scope

### Debug Tools
- Use Azure AD token decoder: `https://jwt.ms/`
- Check Azure AD sign-in logs
- Enable debug logging in both frontend and backend

## Security Best Practices
- Use client certificates in production
- Implement token caching appropriately
- Set appropriate token lifetimes
- Monitor token usage and anomalies
- Use conditional access policies

## Production Considerations
- Use Azure Key Vault for secrets
- Implement proper certificate rotation
- Set up monitoring and alerting
- Use Azure Application Insights
- Configure backup and disaster recovery
