#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Starting Entra ID App Registration for DroitAI..."

if (-not $env:AZURE_ENV_NAME) {
    Write-Error "AZURE_ENV_NAME is not set. Run 'azd env select' first."
    exit 1
}

# ---------------------------------------------------------------------------
# Helper — find existing app registration by display name or create a new one
# ---------------------------------------------------------------------------
function Get-OrCreateApp {
    param([string]$DisplayName)

    $existing = az ad app list --display-name $DisplayName --query "[0]" -o json | ConvertFrom-Json
    if ($existing) {
        Write-Host "  App '$DisplayName' already exists (appId: $($existing.appId)) — reusing."
        return $existing
    }

    Write-Host "  Creating app '$DisplayName'..."
    $app = az ad app create --display-name $DisplayName --sign-in-audience AzureADMyOrg | ConvertFrom-Json
    if (-not $app) { Write-Error "Failed to create app '$DisplayName'"; exit 1 }
    return $app
}

# Helper — ensure a service principal exists for an app
function Ensure-ServicePrincipal {
    param([string]$AppId)

    $sp = az ad sp list --filter "appId eq '$AppId'" --query "[0]" -o json | ConvertFrom-Json
    if ($sp) { return $sp }

    Write-Host "  Creating service principal for appId $AppId..."
    return (az ad sp create --id $AppId | ConvertFrom-Json)
}

# ---------------------------------------------------------------------------
# 1. Backend app registration
# ---------------------------------------------------------------------------
$backendName = "droitai-backend-$env:AZURE_ENV_NAME"
$backendApp  = Get-OrCreateApp -DisplayName $backendName
$backendClientId   = $backendApp.appId
$backendObjectId   = $backendApp.id

# Expose API scope (access_as_user) — idempotent: update is safe to re-run
Write-Host "  Setting identifier URI and Graph permission on backend app..."
az ad app update --id $backendClientId --identifier-uris "api://$backendClientId" | Out-Null

# Add User.Read delegated permission (Graph) only if not already present
$perms = az ad app show --id $backendClientId --query "requiredResourceAccess" -o json | ConvertFrom-Json
$graphId   = "00000003-0000-0000-c000-000000000000"
$userReadId = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
$alreadyHas = $perms | Where-Object { $_.resourceAppId -eq $graphId } |
              Select-Object -ExpandProperty resourceAccess |
              Where-Object { $_.id -eq $userReadId }

if (-not $alreadyHas) {
    az ad app api-permission add --id $backendClientId `
        --api $graphId `
        --api-permissions "$userReadId=Scope" | Out-Null
    Write-Host "  Graph User.Read scope added."
} else {
    Write-Host "  Graph User.Read scope already present — skipping."
}

Ensure-ServicePrincipal -AppId $backendClientId | Out-Null

# ---------------------------------------------------------------------------
# 2. Frontend app registration
# ---------------------------------------------------------------------------
$frontendName = "droitai-frontend-$env:AZURE_ENV_NAME"
$frontendApp  = Get-OrCreateApp -DisplayName $frontendName
$frontendClientId = $frontendApp.appId

Ensure-ServicePrincipal -AppId $frontendClientId | Out-Null

# ---------------------------------------------------------------------------
# 3. Persist to azd environment
# ---------------------------------------------------------------------------
azd env set BACKEND_CLIENT_ID  $backendClientId
azd env set FRONTEND_CLIENT_ID $frontendClientId

Write-Host ""
Write-Host "Identity setup complete."
Write-Host "  Backend  client ID : $backendClientId"
Write-Host "  Frontend client ID : $frontendClientId"