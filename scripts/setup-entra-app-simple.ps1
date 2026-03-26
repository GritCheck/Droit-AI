# Entra ID Setup Script for DroitAI - PowerShell Version
Write-Host "Setting up Entra ID Apps for DroitAI..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Host "ERROR: Azure CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if already logged in
try {
    $account = az account show --query tenantId -o tsv
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in"
    }
} catch {
    Write-Host "Logging in to Azure..." -ForegroundColor Blue
    az login
}

# Get tenant info
$tenantId = az account show --query tenantId -o tsv
Write-Host "SUCCESS: Tenant ID: $tenantId" -ForegroundColor Green

# App configuration
$backendAppName = "DroitAI-RAG-Backend-App"
$frontendAppName = "DroitAI-RAG-Frontend-App"
$frontendUrl = "http://localhost:3000"
$backendUrl = "http://localhost:8000"

Write-Host "Setting up Entra ID Apps for DroitAI..." -ForegroundColor Blue
Write-Host "Backend App: $backendAppName" -ForegroundColor Cyan
Write-Host "Frontend App: $frontendAppName" -ForegroundColor Cyan

# Create Backend App Registration
Write-Host "Creating Backend App Registration: $backendAppName" -ForegroundColor Blue
try {
    $backendAppId = az ad app create --display-name "$backendAppName" --sign-in-audience AzureADMyOrg --web-redirect-uris "$frontendUrl/auth/callback" --enable-id-token-issuance true --enable-access-token-issuance true --query appId -o tsv
    
    if ([string]::IsNullOrWhiteSpace($backendAppId)) {
        throw "Failed to create backend app registration"
    }
    
    Write-Host "SUCCESS: Backend App Created!" -ForegroundColor Green
    Write-Host "Backend Client ID: $backendAppId" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Failed to create backend app registration. Please check your Azure permissions." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create Backend Service Principal
Write-Host "Creating Backend Service Principal..." -ForegroundColor Blue
az ad sp create --id $backendAppId --only-show-errors

# Add API Permissions (Microsoft Graph User.Read)
Write-Host "Adding Microsoft Graph permissions to backend..." -ForegroundColor Blue
az ad app permission add --id $backendAppId --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope --only-show-errors

# Expose API for OBO flow
Write-Host "Exposing API for OBO flow..." -ForegroundColor Blue
az ad app update --id $backendAppId --identifier-uris "api://$backendAppId" --only-show-errors

# Create Backend Client Secret
Write-Host "Creating Backend Client Secret..." -ForegroundColor Blue
try {
    $backendClientSecret = az ad app credential reset --id $backendAppId --append --display-name "DroitAI-Backend-Client-Secret" --years 1 --query password -o tsv
    
    if ([string]::IsNullOrWhiteSpace($backendClientSecret)) {
        throw "Failed to create backend client secret"
    }
    
    Write-Host "SUCCESS: Backend Client Secret generated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create backend client secret. Please check your Azure permissions." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Grant admin consent for backend
Write-Host "Granting admin consent for backend..." -ForegroundColor Blue
az ad app permission grant --id $backendAppId --api 00000003-0000-0000-c000-000000000000 --only-show-errors
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Backend admin consent failed. Please grant consent manually in Azure Portal." -ForegroundColor Yellow
}

# Create Frontend App Registration
Write-Host "Creating Frontend App Registration: $frontendAppName" -ForegroundColor Blue
try {
    $frontendAppId = az ad app create --display-name "$frontendAppName" --sign-in-audience AzureADMyOrg --web-redirect-uris "$frontendUrl/auth/callback" --enable-id-token-issuance true --query appId -o tsv
    
    if ([string]::IsNullOrWhiteSpace($frontendAppId)) {
        throw "Failed to create frontend app registration"
    }
    
    Write-Host "SUCCESS: Frontend App Created!" -ForegroundColor Green
    Write-Host "Frontend Client ID: $frontendAppId" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Failed to create frontend app registration. Please check your Azure permissions." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create Frontend Service Principal
Write-Host "Creating Frontend Service Principal..." -ForegroundColor Blue
az ad sp create --id $frontendAppId --only-show-errors

# Add API Permissions (Microsoft Graph User.Read)
Write-Host "Adding Microsoft Graph permissions to frontend..." -ForegroundColor Blue
az ad app permission add --id $frontendAppId --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope --only-show-errors

# Create Frontend Client Secret
Write-Host "Creating Frontend Client Secret..." -ForegroundColor Blue
try {
    $frontendClientSecret = az ad app credential reset --id $frontendAppId --append --display-name "DroitAI-Frontend-Client-Secret" --years 1 --query password -o tsv
    
    if ([string]::IsNullOrWhiteSpace($frontendClientSecret)) {
        throw "Failed to create frontend client secret"
    }
    
    Write-Host "SUCCESS: Frontend Client Secret generated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create frontend client secret. Please check your Azure permissions." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Grant admin consent for frontend
Write-Host "Granting admin consent for frontend..." -ForegroundColor Blue
az ad app permission grant --id $frontendAppId --api 00000003-0000-0000-c000-000000000000 --only-show-errors
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Frontend admin consent failed. Please grant consent manually in Azure Portal." -ForegroundColor Yellow
}

# Output configuration
Write-Host ""
Write-Host "=== ENTRA ID APP CONFIGURATION ===" -ForegroundColor Green
Write-Host "Tenant ID: $tenantId" -ForegroundColor Cyan
Write-Host ""
Write-Host "BACKEND APP:" -ForegroundColor Yellow
Write-Host "Backend Client ID: $backendAppId" -ForegroundColor White
Write-Host "Backend Client Secret: $backendClientSecret" -ForegroundColor White
Write-Host "Backend API Scope: api://$backendAppId/access_as_user" -ForegroundColor White
Write-Host "Backend Graph Scope: https://graph.microsoft.com/User.Read" -ForegroundColor White
Write-Host ""
Write-Host "FRONTEND APP:" -ForegroundColor Yellow
Write-Host "Frontend Client ID: $frontendAppId" -ForegroundColor White
Write-Host "Frontend Client Secret: $frontendClientSecret" -ForegroundColor White
Write-Host "Frontend Redirect URI: $frontendUrl/auth/callback" -ForegroundColor White
Write-Host "Frontend Graph Scope: https://graph.microsoft.com/User.Read" -ForegroundColor White

# Create .env file
Write-Host ""
Write-Host "Creating .env.entra file..." -ForegroundColor Blue
"# Entra ID Configuration" | Out-File -FilePath ".env.entra" -Encoding UTF8
"# Backend Configuration" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"ENTRA_APP_CLIENT_ID=$backendAppId" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"ENTRA_APP_CLIENT_SECRET=$backendClientSecret" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"ENTRA_APP_TENANT_ID=$tenantId" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"ENTRA_APP_API_SCOPE=api://$backendAppId/access_as_user" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"ENTRA_APP_GRAPH_SCOPE=https://graph.microsoft.com/User.Read" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"# Frontend Configuration" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"FRONTEND_ENTRA_CLIENT_ID=$frontendAppId" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"FRONTEND_ENTRA_CLIENT_SECRET=$frontendClientSecret" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append
"FRONTEND_ENTRA_REDIRECT_URI=$frontendUrl/auth/callback" | Out-File -FilePath ".env.entra" -Encoding UTF8 -Append

Write-Host ""
Write-Host "Environment variables saved to .env.entra" -ForegroundColor Green

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Green
Write-Host "1. Update your AZD environment with backend settings:" -ForegroundColor White
Write-Host "   azd env set ENTRA_APP_CLIENT_ID $backendAppId" -ForegroundColor Gray
Write-Host "   azd env set ENTRA_APP_CLIENT_SECRET $backendClientSecret" -ForegroundColor Gray
Write-Host "   azd env set ENTRA_APP_TENANT_ID $tenantId" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update your AZD environment with frontend settings:" -ForegroundColor White
Write-Host "   azd env set FRONTEND_ENTRA_CLIENT_ID $frontendAppId" -ForegroundColor Gray
Write-Host "   azd env set FRONTEND_ENTRA_CLIENT_SECRET $frontendClientSecret" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Deploy your application:" -ForegroundColor White
Write-Host "   azd up" -ForegroundColor Gray
Write-Host ""
Write-Host "Entra ID setup completed successfully!" -ForegroundColor Green

Read-Host "Press Enter to exit"
