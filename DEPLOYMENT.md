# DroitAI Deployment Guide

This guide provides step-by-step instructions for deploying the DroitAI full-stack RAG system to Azure using the Azure Developer CLI (azd).

## 🏗️ Architecture Overview

DroitAI now consists of **two separate Azure App Services** with dedicated Entra ID registrations:

### Frontend (Next.js)
- **App Service**: `droitai-frontend`
- **Purpose**: Client-side React application
- **Authentication**: Entra ID SPA registration
- **Runtime**: Node.js 20 LTS on Linux

### Backend (FastAPI)
- **App Service**: `droitai-app` 
- **Purpose**: API server with RAG capabilities
- **Authentication**: Entra ID Web API registration
- **Runtime**: Python 3.11 on Linux
- **OBO Flow**: Exposes API for frontend token exchange

## 📋 Prerequisites

### Required Tools
- **Azure CLI** - [Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure Developer CLI (azd)** - [Install Guide](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
- **Azure Subscription** with Owner permissions

### Required Permissions
- Ability to create Entra ID App Registrations
- Ability to grant admin consent for API permissions
- Ability to deploy Azure resources (App Services, Storage, etc.)

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Local Environment

```bash
# Clone the repository
git clone <repository>
cd droitai

# Verify Azure CLI login
az account show

# Verify azd login
azd auth login
```

### Step 2: Setup Entra ID Applications

This is the **most critical step** - we create separate Entra ID apps for frontend and backend:

#### 2.1 Run the Setup Script

```bash
# Windows Command Prompt
cd scripts
setup-entra-app.cmd

# Linux/Mac Bash (if available)
cd scripts
./setup-entra-app.sh

# Powershell
cd scripts
setup-entra-app.ps1
```

#### 2.2 What the Script Does

The script will:
1. **Create Backend App Registration**: `DroitAI-RAG-Backend-App`
   - Exposes API for OBO flow
   - Generates Client ID and Secret
   - Adds Microsoft Graph permissions
   
2. **Create Frontend App Registration**: `DroitAI-RAG-Frontend-App`
   - SPA registration for Next.js
   - Generates separate Client ID and Secret
   - Sets redirect URI: `http://localhost:3000/auth/callback`

#### 2.3 Save the Output

The script generates a `.env.entra` file with:
```bash
# Backend Configuration
ENTRA_APP_CLIENT_ID=<backend-client-id>
ENTRA_APP_CLIENT_SECRET=<backend-client-secret>
ENTRA_APP_TENANT_ID=<tenant-id>
ENTRA_APP_API_SCOPE=api://<backend-app-id>/access_as_user

# Frontend Configuration  
FRONTEND_ENTRA_CLIENT_ID=<frontend-client-id>
FRONTEND_ENTRA_CLIENT_SECRET=<frontend-client-secret>
FRONTEND_ENTRA_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Step 3: Configure Azure Environment

#### 3.1 Set Backend Environment Variables

```bash
azd env set ENTRA_APP_CLIENT_ID <backend-client-id>
azd env set ENTRA_APP_CLIENT_SECRET <backend-client-secret>
azd env set ENTRA_APP_TENANT_ID <tenant-id>
```

#### 3.2 Set Frontend Environment Variables

```bash
azd env set FRONTEND_ENTRA_CLIENT_ID <frontend-client-id>
azd env set FRONTEND_ENTRA_CLIENT_SECRET <frontend-client-secret>
```

#### 3.3 Optional: Configure Additional Settings

```bash
# Enable OBO flow (recommended for production)
azd env set ENABLE_OBO_FLOW true

# Set log level
azd env set LOG_LEVEL INFO
```

### Step 4: Configure Cross-App Access (Critical!)

This step enables the frontend to request tokens for the backend without prompting users twice.

#### 4.1 Fix Backend App (`DroitAI-RAG-Backend-App`)

**Navigate to Azure Portal:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations**
3. Find and select **DroitAI-RAG-Backend-App**

**Fix Microsoft Graph Permissions:**
1. Click **API permissions** in the left menu
2. If you see **Microsoft Graph (1)** with a warning or broken state:
   - Click the **...** (more options) → **Remove permission**
   - Click **+ Add a permission** → **Microsoft Graph** → **Delegated permissions**
   - Search for `User.Read`, check the box, and click **Add permissions**
3. **Grant Admin Consent:**
   - Click the **Grant admin consent for [Your Org]** button
   - Wait for both permissions to show green checkmarks

**Verify API Exposure:**
1. Click **Expose an API** in the left menu
2. Verify your **Application ID URI** is set (e.g., `api://3428ba19-18dd-4282-9580-82b67b61ff49`)
3. Verify your **Scope** `access_as_user` exists

#### 4.2 Fix Frontend App (`DroitAI-RAG-Frontend-App`)

**Navigate to Frontend App:**
1. Go to **Microsoft Entra ID** → **App registrations**
2. Find and select **DroitAI-RAG-Frontend-App**

**Fix Microsoft Graph Permissions:**
1. Click **API permissions** in the left menu
2. If **Microsoft Graph** appears broken:
   - Click **...** → **Remove permission**
   - Click **+ Add a permission** → **Microsoft Graph** → **Delegated permissions**
   - Search for `User.Read`, check the box, and click **Add permissions**
3. Click **Grant admin consent for [Your Org]**

**Add Backend Permission (Critical for OBO Flow):**
1. Click **+ Add a permission**
2. Select **APIs my organization uses**
3. Search for `DroitAI-RAG-Backend-App` and select it
4. Select **Delegated permissions**
5. Check the box for `access_as_user`
6. Click **Add permissions**
7. Click **Grant admin consent for [Your Org]**

**Final Verification:**
Both Microsoft Graph and Backend permissions should show green checkmarks.

#### 4.3 Verify Cross-App Configuration

1. In **DroitAI-RAG-Backend-App** → **Expose an API**
2. Check that **DroitAI-RAG-Frontend-App** appears in **Authorized client applications**
3. The frontend should have permission to access `access_as_user` scope

#### 4.4 Update Environment Variables (Optional Sync)

To ensure your local environment matches the portal configuration:

```bash
# Update with specific IDs from your portal
azd env set ENTRA_APP_CLIENT_ID 3428ba19-18dd-4282-9580-82b67b61ff49
azd env set FRONTEND_ENTRA_CLIENT_ID 965b3098-bf3c-4eed-9d35-db24584da8b2
azd env set ENTRA_APP_TENANT_ID 76e16f4d-979c-4aed-a37a-0eb730d9b885

# Enable OBO flow in code logic
azd env set ENABLE_OBO_FLOW true
```

### Step 5: Deploy to Azure

#### 5.1 Provision Infrastructure

```bash
# This creates all Azure resources
azd provision
```

This deploys:
- Azure Storage Account
- Azure AI Search
- Azure OpenAI
- Azure Document Intelligence
- Azure Content Safety
- Application Insights
- Log Analytics Workspace
- **Two App Services** (frontend + backend)

#### 5.2 Deploy Applications

```bash
# This builds and deploys both frontend and backend
azd deploy
```

#### 5.3 Or Use Combined Command

```bash
# Provision and deploy in one step
azd up
```

### Step 6: Verify Deployment

#### 6.1 Check Backend Health

```bash
# Get backend URL from azd
azd env get-value APP_SERVICE_ENDPOINT

# Test health endpoint
curl https://<backend-app-name>.azurewebsites.net/health
```

#### 6.2 Check Frontend Health

```bash
# Get frontend URL from azd
azd env get-value FRONTEND_ENDPOINT

# Test health endpoint
curl https://<frontend-app-name>.azurewebsites.net/api/health
```

#### 6.3 Verify Application URLs

```bash
# Get all endpoints
azd env get-values
```

You should see:
- **Frontend URL**: `https://droitai-frontend.azurewebsites.net`
- **Backend URL**: `https://droitai-app.azurewebsites.net`

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "ClientSecretExpired" Error
```bash
# Regenerate secrets
cd scripts
setup-entra-app.cmd

# Update environment variables
azd env set ENTRA_APP_CLIENT_SECRET <new-backend-secret>

**Problem**: Portal shows "confused" state or broken permissions
**Solution**: Follow Step 4 detailed above to remove and re-add permissions correctly.

#### 2. Cross-App Access Issues

**Problem**: Frontend can't access backend API
**Symptoms**: 
- 401 Unauthorized errors when calling backend
- Token exchange failures
- Double authentication prompts

**Solutions**:
1. **Verify Step 4.2** was completed correctly
2. **Check Authorized Client Applications** in backend app
3. **Verify frontend has `access_as_user` permission**
4. **Ensure admin consent was granted** (green checkmarks)

#### 3. Build Failures

```bash
# Check deployment logs
azd logs

# Redeploy specific service
azd deploy --service frontend
azd deploy --service app
```

#### 4. Authentication Failures

```bash
# Check environment variables
azd env get-values

# Verify redirect URIs match
# Frontend: http://localhost:3000/auth/callback (dev)
# Frontend: https://<frontend-url>/auth/callback (prod)
```

#### 5. Backend API Not Accessible

```bash
# Test backend health
curl https://<backend-app-name>.azurewebsites.net/health

# Check backend logs
azd logs --service app
```

#### 6. Frontend Build Issues

```bash
# Test frontend health
curl https://<frontend-app-name>.azurewebsites.net/api/health

# Check frontend logs
azd logs --service frontend
```

### Entra ID Portal Quick Reference

| Issue | Location | Fix |
|--------|----------|------|
| Broken Microsoft Graph permission | API permissions | Remove → Re-add as Delegated |
| Missing admin consent | API permissions | Click "Grant admin consent" |
| OBO flow not working | Backend app | Add frontend as Authorized client |
| Frontend can't call backend | Frontend app | Add backend API permission |
| Double authentication prompts | Both apps | Verify cross-app access setup |

### Debug Commands

```bash
# View all environment variables
azd env get-values

# Check deployment status
azd status

# View infrastructure
azd infra graph

# Get logs for specific service
azd logs --service app
azd logs --service frontend
```

---

## 🌍 Environment-Specific Configurations

### Development
```bash
# Local development URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Production
```bash
# Azure App Service URLs (set automatically)
FRONTEND_URL=https://droitai-frontend.azurewebsites.net
BACKEND_URL=https://droitai-app.azurewebsites.net
```

### Testing/Staging
```bash
# Create separate environment
azd env new testing
azd env set ENV_NAME testing
```

---

## 📊 Monitoring and Observability

### Application Insights
- **Backend**: `droitai-appinsights`
- **Frontend**: `droitai-frontend-insights`
- **Logs**: Available in Azure Portal → Application Insights → Logs

### Key Metrics to Monitor
1. **Response Time**: Backend API performance
2. **Error Rate**: Frontend/backend failures
3. **Authentication**: Entra ID token issues
4. **Resource Usage**: App Service scaling

### Log Queries
```kql
// View backend errors
exceptions 
| where cloud_RoleName == "droitai-app"

// View frontend performance
pageViews 
| where cloud_RoleName == "droitai-frontend"
```

---

## 🔄 CI/CD Integration

### GitHub Actions (Optional)
```yaml
# .github/workflows/azure.yml
name: Deploy to Azure
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Deploy to Azure
        run: |
          azd up --no-prompt
```

---

## 🎯 Next Steps After Deployment

1. **Test Authentication Flow**
   - Navigate to frontend URL
   - Complete Entra ID login
   - Verify API calls work

2. **Upload Test Documents**
   - Use the document upload feature
   - Verify processing in Azure Storage

3. **Test RAG Functionality**
   - Ask questions about uploaded documents
   - Verify responses include citations

4. **Configure Production Settings**
   - Update redirect URIs for production domain
   - Set up custom domains if needed
   - Configure backup and disaster recovery

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review Azure deployment logs: `azd logs`
3. Verify Entra ID configuration in Azure Portal
4. Check resource quotas in Azure subscription

For additional help, refer to:
- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Entra ID Authentication Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
