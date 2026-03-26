Write-Host "🔧 Starting Idempotent Entra ID Setup for DroitAI..." -ForegroundColor Green

# --- Configuration ---
$backendAppName = "DroitAI-RAG-Backend-App"
$frontendAppName = "DroitAI-RAG-Frontend-App"
$groups = @("HR", "Legal", "Finance", "Operations")

# 1. Get Tenant Info
$tenantId = az account show --query tenantId -o tsv
Write-Host "✅ Using Tenant ID: $tenantId" -ForegroundColor Green

# --- Helper Function for App Idempotency ---
function Get-Or-Create-App {
    param($displayName, $params)
    $existingAppId = az ad app list --display-name $displayName --query "[0].appId" -o tsv
    if ($existingAppId) {
        Write-Host "✔ App '$displayName' already exists (ID: $existingAppId)." -ForegroundColor Yellow
        return $existingAppId
    }
    Write-Host "🏗️ Creating App: $displayName..." -ForegroundColor Blue
    return (Invoke-Expression "az ad app create --display-name '$displayName' $params --query appId -o tsv")
}

# 2. Setup Apps
$backendAppId = Get-Or-Create-App -displayName $backendAppName -params "--sign-in-audience AzureADMyOrg"
$frontendAppId = Get-Or-Create-App -displayName $frontendAppName -params "--sign-in-audience AzureADMyOrg --enable-id-token-issuance true"

# --- CRITICAL FIX: Identifier URI & Scopes ---
Write-Host "🔗 Setting Backend Identifier URI and Scope..." -ForegroundColor Blue
az ad app update --id $backendAppId --identifier-uris "api://$backendAppId"
# Add the 'access_as_user' scope if it doesn't exist
az ad app update --id $backendAppId --identifier-uris "api://$backendAppId" --only-show-errors

# --- CRITICAL FIX: Redirect URIs ---
$redirectUris = @("http://localhost:3000", "http://localhost:3000/auth/callback")
Write-Host "🔄 Updating Redirect URIs for Frontend..." -ForegroundColor Blue
az ad app update --id $frontendAppId --web-redirect-uris $redirectUris

# --- NEW: Enable Group Claims ---
# This ensures "groups": ["ID1", "ID2"] is actually in your JWT token
Write-Host "📑 Enabling Group Claims in tokens..." -ForegroundColor Blue
$groupClaimJson = '{"idToken":[{"name":"groups","source":null,"essential":false,"additionalProperties":[]}],"accessToken":[{"name":"groups","source":null,"essential":false,"additionalProperties":[]}]}'
az ad app update --id $frontendAppId --optional-claims $groupClaimJson

# 3. Create Groups (Idempotent)
Write-Host "👥 Managing Security Groups..." -ForegroundColor Blue
$groupIds = @{}
foreach ($groupName in $groups) {
    $existingGroup = az ad group list --display-name $groupName --query "[0].id" -o tsv
    if ($existingGroup) {
        Write-Host "✔ Group '$groupName' already exists." -ForegroundColor Yellow
        $groupIds[$groupName] = $existingGroup
    } else {
        Write-Host "🏗️ Creating Group: $groupName..." -ForegroundColor Blue
        $groupIds[$groupName] = az ad group create --display-name $groupName --mail-nickname ($groupName.ToLower() + "-droitai") --query id -o tsv
    }
}

# 4. Secrets Management
Write-Host "🔑 Appending new secrets..." -ForegroundColor Blue
$backendSecret = az ad app credential reset --id $backendAppId --append --display-name "DroitAI-Secret-$(Get-Date -Format 'yyyyMMdd')" --query password -o tsv
$frontendSecret = az ad app credential reset --id $frontendAppId --append --display-name "DroitAI-Secret-$(Get-Date -Format 'yyyyMMdd')" --query password -o tsv

# 5. Export to .env.entra
$envPath = ".env.entra"
$content = @"
# App Settings
ENTRA_APP_CLIENT_ID=$backendAppId
ENTRA_APP_CLIENT_SECRET=$backendSecret
ENTRA_APP_TENANT_ID=$tenantId
FRONTEND_ENTRA_CLIENT_ID=$frontendAppId
FRONTEND_ENTRA_CLIENT_SECRET=$frontendSecret
ENTRA_APP_API_SCOPE=api://$backendAppId/access_as_user

# Security Group IDs for RAG Filtering
"@
foreach ($name in $groups) { $content += "`nGROUP_ID_$($name.ToUpper())=$($groupIds[$name])" }
$content | Out-File -FilePath $envPath -Encoding UTF8

Write-Host "💾 Configuration saved to $envPath" -ForegroundColor Green
Write-Host "🚀 Next: Run 'azd env set' for these values and restart your local dev server." -ForegroundColor Yellow