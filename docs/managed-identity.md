# Managed Identity Configuration

This guide covers the setup and configuration of Azure Managed Identity for production deployment of the Droit AI RAG system, enabling keyless authentication and enhanced security.

## Overview

Azure Managed Identity eliminates the need for storing credentials in your application code or configuration files. The Droit AI system uses both system-assigned and user-assigned managed identities for different components.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure AD Tenant                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │ Frontend    │    │ Backend     │    │ AI Service  │           │
│  │ App Service │    │ App Service │    │ Functions   │           │
│  │ (System)    │    │ (System)    │    │ (User)      │           │
│  └─────────────┘    └─────────────┘    └─────────────┘           │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘                │
│                             │                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           Azure Resource Access (RBAC)                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   Storage   │  │   Key Vault │  │ Cognitive   │        │ │
│  │  │   Account   │  │             │  │ Services    │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Types of Managed Identities

### 1. System-Assigned Managed Identity
- **Created automatically** with Azure resource
- **Lifecycle tied** to the resource
- **Used for**: Frontend App Service, Backend App Service

### 2. User-Assigned Managed Identity
- **Created as standalone** Azure resource
- **Can be assigned** to multiple resources
- **Used for**: AI Functions, shared services

## Implementation Guide

### Step 1: Enable System-Assigned Identity

#### Frontend App Service
```bash
# Enable system-assigned identity for frontend
az webapp identity assign \
  --name <frontend-app-name> \
  --resource-group <resource-group>

# Get identity details
FRONTEND_IDENTITY=$(az webapp identity show \
  --name <frontend-app-name> \
  --resource-group <resource-group> \
  --query principalId -o tsv)

echo "Frontend Identity ID: $FRONTEND_IDENTITY"
```

#### Backend App Service
```bash
# Enable system-assigned identity for backend
az webapp identity assign \
  --name <backend-app-name> \
  --resource-group <resource-group>

# Get identity details
BACKEND_IDENTITY=$(az webapp identity show \
  --name <backend-app-name> \
  --resource-group <resource-group> \
  --query principalId -o tsv)

echo "Backend Identity ID: $BACKEND_IDENTITY"
```

### Step 2: Create User-Assigned Identity

```bash
# Create user-assigned identity for AI services
az identity create \
  --name "droit-ai-identity" \
  --resource-group <resource-group> \
  --location <location>

# Get identity details
AI_IDENTITY=$(az identity show \
  --name "droit-ai-identity" \
  --resource-group <resource-group> \
  --query principalId -o tsv)

AI_IDENTITY_CLIENT_ID=$(az identity show \
  --name "droit-ai-identity" \
  --resource-group <resource-group> \
  --query clientId -o tsv)

echo "AI Identity ID: $AI_IDENTITY"
echo "AI Identity Client ID: $AI_IDENTITY_CLIENT_ID"
```

### Step 3: Assign User-Assigned Identity to Functions

```bash
# Assign user-assigned identity to AI functions
az functionapp identity assign \
  --name <ai-functions-name> \
  --resource-group <resource-group> \
  --identities ["/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/droit-ai-identity"]
```

## RBAC Role Assignments

### Storage Account Access

```bash
# Get storage account ID
STORAGE_ACCOUNT_ID=$(az storage account show \
  --name <storage-name> \
  --query id -o tsv)

# Assign Storage Blob Data Reader to frontend (read access to contracts)
az role assignment create \
  --assignee $FRONTEND_IDENTITY \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_ACCOUNT_ID

# Assign Storage Blob Data Contributor to backend (read/write access)
az role assignment create \
  --assignee $BACKEND_IDENTITY \
  --role "Storage Blob Data Contributor" \
  --scope $STORAGE_ACCOUNT_ID

# Assign Storage Queue Data Contributor to backend (document processing)
az role assignment create \
  --assignee $BACKEND_IDENTITY \
  --role "Storage Queue Data Contributor" \
  --scope $STORAGE_ACCOUNT_ID
```

### Cognitive Services Access

```bash
# Get cognitive services account ID
COGNITIVE_SERVICES_ID=$(az cognitiveservices account show \
  --name <cognitive-services-name> \
  --query id -o tsv)

# Assign Cognitive Services User to backend
az role assignment create \
  --assignee $BACKEND_IDENTITY \
  --role "Cognitive Services User" \
  --scope $COGNITIVE_SERVICES_ID

# Assign Cognitive Services Contributor to AI functions
az role assignment create \
  --assignee $AI_IDENTITY \
  --role "Cognitive Services Contributor" \
  --scope $COGNITIVE_SERVICES_ID
```

### Key Vault Access

```bash
# Create Key Vault (if not exists)
az keyvault create \
  --name "<keyvault-name>" \
  --resource-group <resource-group> \
  --location <location> \
  --enable-soft-delete true \
  --enable-purge-protection true

# Get Key Vault ID
KEYVAULT_ID=$(az keyvault show \
  --name "<keyvault-name>" \
  --query id -o tsv)

# Assign Key Vault Secrets User to backend
az role assignment create \
  --assignee $BACKEND_IDENTITY \
  --role "Key Vault Secrets User" \
  --scope $KEYVAULT_ID

# Assign Key Vault Secrets Officer to AI functions
az role assignment create \
  --assignee $AI_IDENTITY \
  --role "Key Vault Secrets Officer" \
  --scope $KEYVAULT_ID
```

## Application Configuration

### Frontend Configuration (Azure App Settings)

```bash
# Update frontend app settings to use managed identity
az webapp config appsettings set \
  --name <frontend-app-name> \
  --resource-group <resource-group> \
  --settings \
    AZURE_CLIENT_ID="" \
    AZURE_CLIENT_SECRET="" \
    AZURE_TENANT_ID="" \
    USE_MANAGED_IDENTITY=true
```

### Backend Configuration (Azure App Settings)

```bash
# Update backend app settings to use managed identity
az webapp config appsettings set \
  --name <backend-app-name> \
  --resource-group <resource-group> \
  --settings \
    AZURE_CLIENT_ID="" \
    AZURE_CLIENT_SECRET="" \
    AZURE_TENANT_ID="" \
    USE_MANAGED_IDENTITY=true \
    STORAGE_ACCOUNT_NAME=<storage-name> \
    COGNITIVE_SERVICES_ENDPOINT=<cognitive-services-endpoint>
```

### AI Functions Configuration

```bash
# Update AI functions app settings
az functionapp config appsettings set \
  --name <ai-functions-name> \
  --resource-group <resource-group> \
  --settings \
    AZURE_CLIENT_ID=$AI_IDENTITY_CLIENT_ID \
    USE_MANAGED_IDENTITY=true \
    COGNITIVE_SERVICES_ENDPOINT=<cognitive-services-endpoint>
```

## Code Implementation

### Backend Managed Identity Authentication

```python
# backend/app/auth/managed_identity.py
import asyncio
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient

class ManagedIdentityAuth:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self._blob_client = None
        self._keyvault_client = None
    
    @property
    def blob_client(self) -> BlobServiceClient:
        if not self._blob_client:
            self._blob_client = BlobServiceClient(
                account_url=f"https://{os.getenv('STORAGE_ACCOUNT_NAME')}.blob.core.windows.net",
                credential=self.credential
            )
        return self._blob_client
    
    @property
    def keyvault_client(self) -> SecretClient:
        if not self._keyvault_client:
            keyvault_uri = f"https://{os.getenv('KEYVAULT_NAME')}.vault.azure.net"
            self._keyvault_client = SecretClient(
                vault_uri=keyvault_uri,
                credential=self.credential
            )
        return self._keyvault_client
    
    async def get_access_token(self, scope: str) -> str:
        """Get access token for specified scope using managed identity."""
        try:
            token = await self.credential.get_token(scope)
            return token.token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")

# Usage in application
auth_service = ManagedIdentityAuth()

# Access storage
async def get_contract_documents():
    container_client = auth_service.blob_client.get_container_client("contracts")
    blobs = container_client.list_blobs()
    return [blob.name for blob in blobs]

# Access Key Vault
async def get_secret(secret_name: str):
    secret = await auth_service.keyvault_client.get_secret(secret_name)
    return secret.value
```

### Frontend Managed Identity Usage

```typescript
// frontend/src/services/managed-identity.ts
export class ManagedIdentityService {
  private backendUrl: string;
  
  constructor() {
    this.backendUrl = process.env.NEXT_PUBLIC_SERVER_URL || '';
  }
  
  async getContractDocuments(): Promise<string[]> {
    // Frontend doesn't directly use managed identity
    // It calls backend which uses managed identity
    const response = await fetch(`${this.backendUrl}/api/v1/contracts`, {
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch contracts');
    }
    
    return response.json();
  }
  
  private async getAuthToken(): Promise<string> {
    // Get token from Azure AD (user token, not managed identity)
    return localStorage.getItem('azure_access_token') || '';
  }
}
```

## Testing Managed Identity

### 1. Local Development Setup

```bash
# Use Azure CLI for local development
az login

# Set environment variables for local testing
export AZURE_CLIENT_ID=""
export AZURE_CLIENT_SECRET=""
export AZURE_TENANT_ID="<tenant-id>"
export USE_MANAGED_IDENTITY=false
```

### 2. Production Testing

```python
# Test managed identity access
import pytest
from azure.identity import DefaultAzureCredential

@pytest.mark.asyncio
async def test_managed_identity_storage_access():
    credential = DefaultAzureCredential()
    
    # Test storage access
    blob_client = BlobServiceClient(
        account_url=f"https://{storage_name}.blob.core.windows.net",
        credential=credential
    )
    
    container_client = blob_client.get_container_client("contracts")
    blobs = list(container_client.list_blobs())
    
    assert len(blobs) > 0, "Should access storage contracts"

@pytest.mark.asyncio
async def test_managed_identity_keyvault_access():
    credential = DefaultAzureCredential()
    
    # Test Key Vault access
    secret_client = SecretClient(
        vault_uri=f"https://{keyvault_name}.vault.azure.net",
        credential=credential
    )
    
    # Try to access a test secret
    secret = await secret_client.get_secret("test-secret")
    assert secret.value is not None
```

## Monitoring & Troubleshooting

### 1. Managed Identity Logs

```bash
# Check managed identity status
az webapp identity show \
  --name <app-name> \
  --resource-group <resource-group>

# Check role assignments
az role assignment list \
  --assignee <identity-principal-id> \
  --output table
```

### 2. Common Issues

#### Issue: "Managed Identity not found"
**Solution**: Verify managed identity is enabled and role assignments are correct

```bash
# Check if identity exists
az identity show \
  --name "droit-ai-identity" \
  --resource-group <resource-group>
```

#### Issue: "Access denied to storage"
**Solution**: Verify RBAC role assignments

```bash
# Check storage role assignments
az role assignment list \
  --assignee <identity-id> \
  --scope <storage-account-id>
```

#### Issue: "Key Vault access denied"
**Solution**: Check Key Vault access policies and RBAC

```bash
# Check Key Vault access policies
az keyvault show \
  --name <keyvault-name> \
  --query properties.accessPolicies
```

## Security Best Practices

### 1. Least Privilege Access
- Assign minimum required permissions
- Use specific roles instead of owner/contributor
- Regularly review and remove unnecessary permissions

### 2. Monitoring and Auditing
```bash
# Enable diagnostic logging
az monitor diagnostic-settings create \
  --name <diagnostic-name> \
  --resource <resource-id> \
  --logs '[{"category": "AuditLog", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```

### 3. Network Security
- Use private endpoints for storage and Key Vault
- Implement VNet integration for App Services
- Configure firewall rules for Key Vault

## Migration from Secrets to Managed Identity

### Migration Script

```python
# scripts/migrate_to_managed_identity.py
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

async def migrate_secrets():
    """Migrate secrets from environment variables to Key Vault."""
    credential = DefaultAzureCredential()
    
    # Connect to Key Vault
    keyvault_client = SecretClient(
        vault_uri=f"https://{os.getenv('KEYVAULT_NAME')}.vault.azure.net",
        credential=credential
    )
    
    # Migrate secrets
    secrets_to_migrate = [
        'OPENAI_API_KEY',
        'DOCUMENT_INTELLIGENCE_KEY',
        'CONTENT_SAFETY_KEY'
    ]
    
    for secret_name in secrets_to_migrate:
        secret_value = os.getenv(secret_name)
        if secret_value:
            await keyvault_client.set_secret(secret_name, secret_value)
            print(f"Migrated {secret_name} to Key Vault")
    
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate_secrets())
```

## Next Steps

1. [Azure Architecture Overview](./azure-architecture.md) - Complete system overview
2. [Network Security Configuration](./network-security.md) - VNet and private endpoints
3. [Monitoring & Observability](./monitoring.md) - Application Insights setup

## References

- [Azure Managed Identity Documentation](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
- [DefaultAzureCredential Best Practices](https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate-hosted-applications)
- [Azure RBAC Documentation](https://docs.microsoft.com/en-us/azure/role-based-access-control/overview)
