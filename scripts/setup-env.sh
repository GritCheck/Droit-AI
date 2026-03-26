#!/bin/bash
set -euo pipefail

echo "Starting Entra ID App Registration for DroitAI..."

if [[ -z "${AZURE_ENV_NAME:-}" ]]; then
  echo "ERROR: AZURE_ENV_NAME is not set. Run 'azd env select' first." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Helper — return existing app or create a new one (idempotent)
# ---------------------------------------------------------------------------
get_or_create_app() {
  local display_name="$1"
  local existing
  existing=$(az ad app list --display-name "$display_name" --query "[0]" -o json)

  if [[ "$existing" != "null" && -n "$existing" ]]; then
    echo "  App '$display_name' already exists — reusing." >&2
    echo "$existing"
  else
    echo "  Creating app '$display_name'..." >&2
    az ad app create --display-name "$display_name" --sign-in-audience AzureADMyOrg
  fi
}

# Helper — ensure a service principal exists for a given appId
ensure_service_principal() {
  local app_id="$1"
  local sp
  sp=$(az ad sp list --filter "appId eq '$app_id'" --query "[0]" -o json)
  if [[ "$sp" == "null" || -z "$sp" ]]; then
    echo "  Creating service principal for appId $app_id..." >&2
    az ad sp create --id "$app_id" > /dev/null
  else
    echo "  Service principal for $app_id already exists — skipping." >&2
  fi
}

# ---------------------------------------------------------------------------
# 1. Backend app registration
# ---------------------------------------------------------------------------
BACKEND_NAME="droitai-backend-${AZURE_ENV_NAME}"
BACKEND_APP=$(get_or_create_app "$BACKEND_NAME")
BACKEND_CLIENT_ID=$(echo "$BACKEND_APP" | jq -r .appId)

# Expose API scope — safe to re-run
echo "  Setting identifier URI on backend app..."
az ad app update --id "$BACKEND_CLIENT_ID" --identifier-uris "api://$BACKEND_CLIENT_ID" > /dev/null

# Add User.Read delegated permission only if missing
GRAPH_APP_ID="00000003-0000-0000-c000-000000000000"
USER_READ_ID="e1fe6dd8-ba31-4d61-89e7-88639da4683d"
ALREADY_HAS=$(az ad app show --id "$BACKEND_CLIENT_ID" \
  --query "requiredResourceAccess[?resourceAppId=='$GRAPH_APP_ID'].resourceAccess[?id=='$USER_READ_ID'] | length(@)" \
  -o tsv)

if [[ "$ALREADY_HAS" == "0" || -z "$ALREADY_HAS" ]]; then
  az ad app api-permission add --id "$BACKEND_CLIENT_ID" \
    --api "$GRAPH_APP_ID" \
    --api-permissions "${USER_READ_ID}=Scope" > /dev/null
  echo "  Graph User.Read scope added."
else
  echo "  Graph User.Read scope already present — skipping."
fi

ensure_service_principal "$BACKEND_CLIENT_ID"

# ---------------------------------------------------------------------------
# 2. Frontend app registration
# ---------------------------------------------------------------------------
FRONTEND_NAME="droitai-frontend-${AZURE_ENV_NAME}"
FRONTEND_APP=$(get_or_create_app "$FRONTEND_NAME")
FRONTEND_CLIENT_ID=$(echo "$FRONTEND_APP" | jq -r .appId)

ensure_service_principal "$FRONTEND_CLIENT_ID"

# ---------------------------------------------------------------------------
# 3. Persist to azd environment
# ---------------------------------------------------------------------------
azd env set BACKEND_CLIENT_ID  "$BACKEND_CLIENT_ID"
azd env set FRONTEND_CLIENT_ID "$FRONTEND_CLIENT_ID"

echo ""
echo "Identity setup complete."
echo "  Backend  client ID : $BACKEND_CLIENT_ID"
echo "  Frontend client ID : $FRONTEND_CLIENT_ID"