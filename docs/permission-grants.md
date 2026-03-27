# Permission Grants & Admin Consent

This guide covers the required API permissions and admin consent workflow for the Droit AI RAG system.

## Overview

Azure AD requires explicit permission grants and admin consent for applications to access Microsoft Graph API and other protected resources. This guide ensures proper permission configuration for both frontend and backend applications.

## Required Permissions

### Frontend Application Permissions

#### Microsoft Graph API
- **User.Read** - Sign in and read user profile
- **User.Read.All** - Read all users' full profiles (for user selection)
- **openid** - Allow sign-in with OpenID Connect
- **profile** - Access user's basic profile
- **email** - Access user's email address

#### Backend API Access
- **access_as_user** - Access backend API on behalf of signed-in user

### Backend Application Permissions

#### Microsoft Graph API
- **User.Read** - Read user profiles for token validation
- **Application.Read.All** - Read application information (for token validation)

#### Azure Storage Permissions
- **Storage Blob Data Reader** - Read access to contract documents
- **Storage Queue Data Contributor** - Queue access for document processing

#### Azure AI Services Permissions
- **Cognitive Services Contributor** - Access to OpenAI, Document Intelligence
- **Cognitive Services User** - Basic AI services access

## Permission Grant Process

### Step 1: Configure Required Resource Access

#### Frontend Manifest (`frontend-manifest.json`)
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
    },
    {
      "id": "64a6c5b8-94d7-40ea-b64c-6cf5eca1f880",
      "type": "Scope",
      "principal": "User"
    },
    {
      "id": "7427e0e7-2c15-4af6-a3b2-3c0fb22611b9",
      "type": "Scope",
      "principal": "User"
    }
  ]
}
```

#### Backend Manifest (`backend-manifest.json`)
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
    },
    {
      "id": "98830695-27d9-4f7c-b5db-9ccdf0131c3d",
      "type": "Role",
      "principal": "Application"
    }
  ]
}
```

### Step 2: Grant Admin Consent

#### Method 1: Using Azure CLI

```bash
# Get application IDs
FRONTEND_APP_ID=$(az ad app list --display-name "Droit AI Frontend" --query "[0].appId" -o tsv)
BACKEND_APP_ID=$(az ad app list --display-name "Droit AI Backend" --query "[0].appId" -o tsv)

# Grant admin consent for frontend
az ad app permission admin-consent --id $FRONTEND_APP_ID

# Grant admin consent for backend
az ad app permission admin-consent --id $BACKEND_APP_ID

# Verify permissions were granted
az ad app show --id $FRONTEND_APP_ID --query "requiredResourceAccess"
az ad app show --id $BACKEND_APP_ID --query "requiredResourceAccess"
```

#### Method 2: Using Azure Portal

1. **Navigate to Azure Portal**
   - Go to Azure Active Directory
   - Select "App registrations"

2. **Frontend App Registration**
   - Find "Droit AI Frontend"
   - Click "API permissions"
   - Click "Grant admin consent for [Your Tenant]"
   - Confirm with "Yes"

3. **Backend App Registration**
   - Find "Droit AI Backend"
   - Click "API permissions"
   - Click "Grant admin consent for [Your Tenant]"
   - Confirm with "Yes"

### Step 3: Verify Permission Grants

#### Check Permission Status

```bash
# Check frontend permissions
az ad app show --id $FRONTEND_APP_ID --query "requiredResourceAccess[0].resourceAccess"

# Check backend permissions  
az ad app show --id $BACKEND_APP_ID --query "requiredResourceAccess[0].resourceAccess"
```

#### Verify in Azure Portal

1. Go to Azure Active Directory > App registrations
2. Select each app registration
3. Click "API permissions"
4. Verify all permissions show "Granted" status with green checkmarks

## Role-Based Access Control (RBAC)

### Storage Account Access

```bash
# Get storage account ID
STORAGE_ACCOUNT_ID=$(az storage account show --name <storage-name> --query id -o tsv)

# Get backend service principal ID
BACKEND_SP_ID=$(az ad sp list --display-name "Droit AI Backend" --query "[0].id" -o tsv)

# Assign Storage Blob Data Reader role
az role assignment create \
  --assignee $BACKEND_SP_ID \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_ACCOUNT_ID

# Assign Storage Queue Data Contributor role
az role assignment create \
  --assignee $BACKEND_SP_ID \
  --role "Storage Queue Data Contributor" \
  --scope $STORAGE_ACCOUNT_ID
```

### Cognitive Services Access

```bash
# Get cognitive services account ID
COGNITIVE_SERVICES_ID=$(az cognitiveservices account show --name <cognitive-services-name> --query id -o tsv)

# Assign Cognitive Services User role
az role assignment create \
  --assignee $BACKEND_SP_ID \
  --role "Cognitive Services User" \
  --scope $COGNITIVE_SERVICES_ID
```

## Testing Permissions

### 1. Frontend Permission Test

```bash
# Test user sign-in
curl -X GET "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize" \
  -d "client_id=<frontend-app-id>" \
  -d "response_type=code" \
  -d "redirect_uri=http://localhost:3000/auth/callback" \
  -d "scope=openid profile email User.Read" \
  -d "state=<random-state>"
```

### 2. Backend Permission Test

```bash
# Test Microsoft Graph access
curl -X GET "https://graph.microsoft.com/v1.0/me" \
  -H "Authorization: Bearer <access-token>"
```

### 3. Storage Access Test

```bash
# Test blob storage access
az storage blob list \
  --account-name <storage-name> \
  --container-name contracts \
  --auth-mode login
```

## Common Permission Issues

### Issue: "Consent not provided for application"
**Symptoms**: Users see consent screen or permission denied errors
**Solution**: Grant admin consent using the methods above

### Issue: "Insufficient privileges to complete operation"
**Symptoms**: Backend cannot access storage or AI services
**Solution**: Assign appropriate RBAC roles to the backend service principal

### Issue: "Access token does not have required permissions"
**Symptoms**: Token validation fails or API calls return 403
**Solution**: Verify required scopes are included in token request

## Permission Best Practices

### 1. Principle of Least Privilege
- Request only necessary permissions
- Use delegated permissions instead of application permissions when possible
- Regularly review and remove unused permissions

### 2. Permission Auditing
```bash
# List all permissions for an app
az ad app show --id <app-id> --query "requiredResourceAccess"

# List role assignments
az role assignment list --assignee <sp-id>
```

### 3. Permission Monitoring
- Monitor Azure AD sign-in logs for permission failures
- Set up alerts for suspicious permission usage
- Regular audit of consent grants

## Automated Permission Setup

### PowerShell Script (`setup-permissions.ps1`)

```powershell
# Variables
$FrontendAppName = "Droit AI Frontend"
$BackendAppName = "Droit AI Backend"
$StorageAccountName = "<storage-name>"
$CognitiveServicesName = "<cognitive-services-name>"

# Get application IDs
$FrontendAppId = (az ad app list --display-name $FrontendAppName --query "[0].appId" -o tsv)
$BackendAppId = (az ad app list --display-name $BackendAppName --query "[0].appId" -o tsv)
$BackendSpId = (az ad sp list --display-name $BackendAppName --query "[0].id" -o tsv)

# Grant admin consent
Write-Host "Granting admin consent for frontend..."
az ad app permission admin-consent --id $FrontendAppId

Write-Host "Granting admin consent for backend..."
az ad app permission admin-consent --id $BackendAppId

# Assign RBAC roles
$StorageAccountId = (az storage account show --name $StorageAccountName --query id -o tsv)
$CognitiveServicesId = (az cognitiveservices account show --name $CognitiveServicesName --query id -o tsv)

Write-Host "Assigning storage roles..."
az role assignment create --assignee $BackendSpId --role "Storage Blob Data Reader" --scope $StorageAccountId
az role assignment create --assignee $BackendSpId --role "Storage Queue Data Contributor" --scope $StorageAccountId

Write-Host "Assigning cognitive services role..."
az role assignment create --assignee $BackendSpId --role "Cognitive Services User" --scope $CognitiveServicesId

Write-Host "Permission setup completed!"
```

## Next Steps

1. [OBO Token Flow Architecture](./obo-token-flow.md) - Understanding token exchange
2. [Managed Identity Configuration](./managed-identity.md) - Production authentication
3. [Azure Architecture Overview](./azure-architecture.md) - Complete system overview

## Support

For permission-related issues:
- Check Azure AD sign-in logs
- Review API permissions in app registrations
- Verify RBAC role assignments
- Use Azure AD diagnostic tools
