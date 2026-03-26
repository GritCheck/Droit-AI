#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# setup-search-index.sh
# Creates the DroitAI CUAD-optimised Azure AI Search index.
# Auth: Azure AD bearer token (no API key — managed identity RBAC).
# ---------------------------------------------------------------------------

INDEX_NAME="droitai-search-index"
API_VERSION="2023-11-01"
MAX_RETRIES=6
RETRY_DELAY_S=30

# ---------------------------------------------------------------------------
# 1. Resolve endpoint
# ---------------------------------------------------------------------------
SEARCH_ENDPOINT=$(azd env get-value AZURE_SEARCH_ENDPOINT)
SEARCH_ENDPOINT="${SEARCH_ENDPOINT%/}"   # strip trailing slash

if [[ -z "$SEARCH_ENDPOINT" ]]; then
  echo "ERROR: AZURE_SEARCH_ENDPOINT is not set. Run 'azd provision' first." >&2
  exit 1
fi
echo "Setting up CUAD-optimised Search Index at $SEARCH_ENDPOINT ..."

# ---------------------------------------------------------------------------
# 2. Acquire bearer token (works for az login, managed identity, and CI/CD)
# ---------------------------------------------------------------------------
TOKEN=$(az account get-access-token --resource "https://search.azure.com" --query accessToken -o tsv)
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: Could not obtain access token for Azure AI Search." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# 3. Index JSON payload
# ---------------------------------------------------------------------------
INDEX_BODY=$(cat <<'EOF'
{
  "name": "droitai-search-index",
  "fields": [
    { "name": "id",             "type": "Edm.String",             "key": true,  "filterable": true,  "retrievable": true },
    { "name": "content",        "type": "Edm.String",             "searchable": true, "retrievable": true, "analyzer": "en.microsoft" },
    { "name": "content_vector", "type": "Collection(Edm.Single)", "searchable": true, "retrievable": false, "dimensions": 1536, "vectorSearchProfile": "vector-profile" },
    { "name": "clause_type",    "type": "Edm.String",             "filterable": true, "searchable": true, "facetable": true, "retrievable": true },
    { "name": "is_red_flag",    "type": "Edm.Boolean",            "filterable": true, "retrievable": true },
    { "name": "document_name",  "type": "Edm.String",             "searchable": true, "filterable": true, "retrievable": true },
    { "name": "page_number",    "type": "Edm.Int32",              "filterable": true, "retrievable": true }
  ],
  "vectorSearch": {
    "algorithms": [
      {
        "name": "hnsw-config",
        "kind": "hnsw",
        "hnswParameters": { "m": 4, "efConstruction": 400, "efSearch": 500 }
      }
    ],
    "profiles": [
      { "name": "vector-profile", "algorithm": "hnsw-config" }
    ]
  },
  "semanticSearch": {
    "defaultConfiguration": "legal-semantic-config",
    "configurations": [
      {
        "name": "legal-semantic-config",
        "prioritizedFields": {
          "titleField":    { "fieldName": "document_name" },
          "contentFields": [ { "fieldName": "content" } ],
          "keywordFields": [ { "fieldName": "clause_type" } ]
        }
      }
    ]
  }
}
EOF
)

# ---------------------------------------------------------------------------
# 4. Create / update index with retry loop (poll instead of fixed sleep)
# ---------------------------------------------------------------------------
URL="${SEARCH_ENDPOINT}/indexes/${INDEX_NAME}?api-version=${API_VERSION}"
attempt=0

until [[ $attempt -ge $MAX_RETRIES ]]; do
  attempt=$((attempt + 1))

  HTTP_STATUS=$(curl -s -o /tmp/search_response.json -w "%{http_code}" \
    -X PUT "$URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$INDEX_BODY")

  if [[ "$HTTP_STATUS" == "200" || "$HTTP_STATUS" == "201" ]]; then
    echo ""
    echo "Search index '$INDEX_NAME' created / updated successfully."
    echo "Index features:"
    echo "  - Full-text search with en.microsoft legal analyser"
    echo "  - Vector search: HNSW, 1536 dimensions (text-embedding-ada-002)"
    echo "  - Semantic search: legal-semantic-config"
    echo "  - Filterable: clause_type (41 CUAD types), is_red_flag, document_name, page_number"
    exit 0
  fi

  # Permanent client errors — do not retry
  if [[ "$HTTP_STATUS" -ge 400 && "$HTTP_STATUS" -lt 500 && "$HTTP_STATUS" != "429" ]]; then
    echo "ERROR: Permanent error $HTTP_STATUS creating search index:" >&2
    cat /tmp/search_response.json >&2
    exit 1
  fi

  if [[ $attempt -lt $MAX_RETRIES ]]; then
    echo "Attempt $attempt/$MAX_RETRIES failed (HTTP $HTTP_STATUS). Retrying in ${RETRY_DELAY_S}s..."
    sleep "$RETRY_DELAY_S"
  fi
done

echo "ERROR: Failed to create search index after $MAX_RETRIES attempts." >&2
cat /tmp/search_response.json >&2
exit 1