#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# setup-search-index.ps1
# Creates the DroitAI CUAD-optimised Azure AI Search index.
# Auth: Azure AD bearer token (no API key required — managed identity RBAC).
# Replaces create-index-simple.ps1 and create-search-index.ps1.
# ---------------------------------------------------------------------------

$INDEX_NAME    = "droitai-search-index"
$API_VERSION   = "2023-11-01"
$MAX_RETRIES   = 6
$RETRY_DELAY_S = 30

# ---------------------------------------------------------------------------
# 1. Resolve endpoint from azd environment
# ---------------------------------------------------------------------------
$SEARCH_ENDPOINT = (azd env get-value AZURE_SEARCH_ENDPOINT).TrimEnd('/')
if (-not $SEARCH_ENDPOINT) {
    Write-Error "AZURE_SEARCH_ENDPOINT is not set. Run 'azd provision' first."
    exit 1
}
Write-Host "Setting up CUAD-optimised Search Index at $SEARCH_ENDPOINT ..."

# ---------------------------------------------------------------------------
# 2. Acquire bearer token for Azure Cognitive Search
#    Works for both local (az login) and CI (managed identity / service principal)
# ---------------------------------------------------------------------------
$token = (az account get-access-token --resource "https://search.azure.com" --query accessToken -o tsv)
if (-not $token) {
    Write-Error "Could not obtain access token for Azure AI Search."
    exit 1
}
$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $token"
}

# ---------------------------------------------------------------------------
# 3. Index definition (built via hashtable → ConvertTo-Json — no manual escaping)
# ---------------------------------------------------------------------------
$indexBody = @{
    name   = $INDEX_NAME
    fields = @(
        @{ name = "id";             type = "Edm.String";              key = $true;  filterable = $true;  retrievable = $true }
        @{ name = "content";        type = "Edm.String";              searchable = $true; retrievable = $true; analyzer = "en.microsoft" }
        @{ name = "content_vector"; type = "Collection(Edm.Single)";  searchable = $true; retrievable = $false; dimensions = 1536; vectorSearchProfile = "vector-profile" }
        @{ name = "clause_type";    type = "Edm.String";              filterable = $true; searchable = $true; facetable = $true; retrievable = $true }
        @{ name = "is_red_flag";    type = "Edm.Boolean";             filterable = $true; retrievable = $true }
        @{ name = "document_name";  type = "Edm.String";              searchable = $true; filterable = $true; retrievable = $true }
        @{ name = "page_number";    type = "Edm.Int32";               filterable = $true; retrievable = $true }
    )
    vectorSearch = @{
        algorithms = @(
            @{
                name           = "hnsw-config"
                kind           = "hnsw"
                hnswParameters = @{ m = 4; efConstruction = 400; efSearch = 500 }
            }
        )
        profiles = @(
            @{ name = "vector-profile"; algorithm = "hnsw-config" }
        )
    }
    semantic = @{
        defaultConfiguration = "legal-semantic-config"
        configurations = @(
            @{
                name              = "legal-semantic-config"
                prioritizedFields = @{
                    titleField                = @{ fieldName = "document_name" }
                    prioritizedContentFields  = @( @{ fieldName = "content" } )
                    prioritizedKeywordsFields = @( @{ fieldName = "clause_type" } )
                }
            }
        )
    }
} | ConvertTo-Json -Depth 10

# ---------------------------------------------------------------------------
# 4. Create / update index with retry loop
# ---------------------------------------------------------------------------
$url     = "$SEARCH_ENDPOINT/indexes/$INDEX_NAME`?api-version=$API_VERSION"
$attempt = 0

while ($attempt -lt $MAX_RETRIES) {
    $attempt++
    try {
        # Invoke-RestMethod throws on 4xx/5xx, so any return here is a success
        $null = Invoke-RestMethod -Uri $url -Method PUT -Headers $headers -Body $indexBody
        Write-Host ""
        Write-Host "Search index '$INDEX_NAME' created / updated successfully."
        Write-Host "Index features:"
        Write-Host "  - Full-text search with en.microsoft legal analyser"
        Write-Host "  - Vector search: HNSW, 1536 dimensions (text-embedding-ada-002)"
        Write-Host "  - Semantic search: legal-semantic-config"
        Write-Host "  - Filterable: clause_type (41 CUAD types), is_red_flag, document_name, page_number"
        exit 0
    }
    catch {
        $status = $_.Exception.Response?.StatusCode.value__
        # 4xx errors (except 503/429) are permanent — do not retry
        if ($status -and $status -ge 400 -and $status -lt 500 -and $status -ne 429) {
            $body = $_.ErrorDetails.Message
            Write-Error "Permanent error $status creating search index: $body"
            exit 1
        }
        if ($attempt -lt $MAX_RETRIES) {
            Write-Host "Attempt $attempt/$MAX_RETRIES failed (status: $status). Retrying in ${RETRY_DELAY_S}s..."
            Start-Sleep -Seconds $RETRY_DELAY_S
        } else {
            Write-Error "Failed to create search index after $MAX_RETRIES attempts. Last error: $($_.Exception.Message)"
            exit 1
        }
    }
}