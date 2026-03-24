# Entra ID Setup for DroitAI RAG Application

## 🎯 Overview

This guide shows how to set up Entra ID authentication for your RAG application using the automated setup scripts.

## 📋 Prerequisites

- Azure CLI installed and logged in
- PowerShell (Windows) or Bash (Linux/Mac)
- Appropriate permissions to create app registrations

## 🚀 Quick Setup (Recommended)

### Option 1: Windows PowerShell
```powershell
cd scripts
.\setup-entra-app.ps1
```

### Option 2: Linux/Mac Bash
```bash
cd scripts
./setup-entra-app.sh
```

### Option 3: Custom Parameters
```powershell
# Windows
.\setup-entra-app.ps1 -AppName "My-RAG-App" -FrontendUrl "https://myapp.com"

# Linux/Mac
./setup-entra-app.sh --app-name "My-RAG-App" --frontend-url "https://myapp.com"
```

## 📝 What the Script Does

1. **Creates Entra ID App Registration**
   - Single app for both frontend and backend
   - Configures redirect URIs
   - Enables ID and access token issuance

2. **Sets Up API Permissions**
   - Microsoft Graph → User.Read
   - Exposes `access_as_user` scope for OBO flow

3. **Creates Service Principal**
   - Enables the app to act as a service principal

4. **Generates Client Secret**
   - 1-year expiration
   - Securely generated and stored

5. **Grants Admin Consent**
   - Auto-consents to required permissions
   - Falls back to manual consent if needed

## 🔧 Manual Configuration (Alternative)

If you prefer manual setup:

### 1. Create App Registration
```bash
az ad app create \
    --display-name "DroitAI-RAG-App" \
    --sign-in-audience AzureADMyOrg \
    --web-redirect-uris "http://localhost:3000/auth/callback"
```

### 2. Add API Permissions
```bash
az ad app permission add \
    --id <APP_ID> \
    --api 00000003-0000-0000-c000-000000000000 \
    --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope
```

### 3. Expose API
```bash
az ad app update \
    --id <APP_ID> \
    --identifier-uris "api://<APP_ID>" \
    --set oauth2Permissions=[{"id":"$(uuidgen)","value":"access_as_user","userConsentDescription":"Access the DroitAI RAG API as you","adminConsentDescription":"Access the DroitAI RAG API as the signed-in user","isEnabled":true,"type":"User"}]
```

### 4. Create Client Secret
```bash
az ad app credential reset \
    --id <APP_ID> \
    --display-name "DroitAI-Client-Secret" \
    --years 1
```

## 🔄 Update AZD Environment

After running the setup script, update your AZD environment:

```bash
# Get values from .env.entra file or script output
azd env set ENTRA_APP_CLIENT_ID <CLIENT_ID>
azd env set ENTRA_APP_CLIENT_SECRET <CLIENT_SECRET>
azd env set ENTRA_APP_TENANT_ID <TENANT_ID>
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js App   │───▶│   FastAPI App    │───▶│  Azure Services │
│   (Frontend)    │    │   (Backend)      │    │  (Search, etc.) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   User Token              OBO Token              Service Calls
```

## 🔐 Security Features

- **Single App Registration**: Simplified management
- **OBO Token Flow**: Secure delegation
- **Least Privilege**: Minimal required permissions
- **Token Validation**: Both frontend and backend validate tokens
- **HTTPS Only**: All communications encrypted

## 🌍 Environment Variables

The setup creates these environment variables:

```bash
# Entra ID Configuration
ENTRA_APP_CLIENT_ID=<CLIENT_ID>
ENTRA_APP_TENANT_ID=<TENANT_ID>
ENTRA_APP_CLIENT_SECRET=<CLIENT_SECRET>
ENTRA_APP_REDIRECT_URI=http://localhost:3000/auth/callback
ENTRA_APP_API_SCOPE=api://<CLIENT_ID>/access_as_user
ENTRA_APP_GRAPH_SCOPE=https://graph.microsoft.com/User.Read
```

## 🚀 Next Steps

1. Run the setup script
2. Update AZD environment variables
3. Deploy your application: `azd up`
4. Test authentication flow
5. Configure your frontend to use MSAL
6. Configure your backend for OBO token exchange

## 🐛 Troubleshooting

### Admin Consent Failed
If admin consent fails automatically:
1. Go to Azure Portal → Entra ID → App registrations
2. Find your app → API permissions
3. Click "Grant admin consent for [Tenant Name]"

### Invalid Redirect URI
Ensure the redirect URI matches exactly:
- Frontend: `http://localhost:3000/auth/callback`
- Production: `https://yourdomain.com/auth/callback`

### Token Exchange Fails
Check that:
- Backend has the correct API scope configured
- Frontend requests the right scope
- Admin consent is granted

## 📚 Additional Resources

- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/azure/active-directory/develop/)
- [OBO Flow Documentation](https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow)
- [MSAL.js for Frontend](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [MSAL Python for Backend](https://github.com/AzureAD/microsoft-authentication-library-for-python)
