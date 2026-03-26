#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Starting data synchronisation for DroitAI..."

# ---------------------------------------------------------------------------
# Resolve storage account from azd environment
# allowSharedKeyAccess is disabled on the storage account, so we use
# --auth-mode login (Azure AD / managed identity) throughout.
# ---------------------------------------------------------------------------
$STORAGE_ACCOUNT_NAME  = (azd env get-value AZURE_STORAGE_ACCOUNT_NAME).Trim()
$STORAGE_CONTAINER_NAME = "documents"

if (-not $STORAGE_ACCOUNT_NAME) {
    Write-Error "AZURE_STORAGE_ACCOUNT_NAME is not set. Run 'azd provision' first."
    exit 1
}
Write-Host "Storage account : $STORAGE_ACCOUNT_NAME"
Write-Host "Container       : $STORAGE_CONTAINER_NAME"

# ---------------------------------------------------------------------------
# Ensure the container exists (idempotent)
# ---------------------------------------------------------------------------
$containerExists = az storage container exists `
    --name $STORAGE_CONTAINER_NAME `
    --account-name $STORAGE_ACCOUNT_NAME `
    --auth-mode login `
    --query exists -o tsv

if ($containerExists -eq "false") {
    Write-Host "Creating storage container '$STORAGE_CONTAINER_NAME'..."
    az storage container create `
        --name $STORAGE_CONTAINER_NAME `
        --account-name $STORAGE_ACCOUNT_NAME `
        --auth-mode login | Out-Null
    Write-Host "Container created."
} else {
    Write-Host "Container '$STORAGE_CONTAINER_NAME' already exists."
}

# ---------------------------------------------------------------------------
# Upload CUAD contract PDFs if the data directory is present
# ---------------------------------------------------------------------------
$DATA_DIR = Join-Path $PSScriptRoot "../data/cuad-contracts"

if (Test-Path $DATA_DIR) {
    Write-Host "Uploading CUAD contract PDFs from $DATA_DIR ..."
    az storage blob upload-batch `
        --destination $STORAGE_CONTAINER_NAME `
        --source $DATA_DIR `
        --account-name $STORAGE_ACCOUNT_NAME `
        --auth-mode login `
        --pattern "*.pdf" `
        --overwrite $false | Out-Null
    Write-Host "CUAD contracts uploaded."
} else {
    Write-Host "WARNING: No CUAD contract data found at $DATA_DIR — skipping upload."
    Write-Host "         Place contract PDFs there before re-running this script."
}

Write-Host "Data synchronisation complete."