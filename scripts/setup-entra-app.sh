#!/bin/bash

# Entra ID App Registration Setup Script (Linux/Mac)
set -e

# Default values
APP_NAME="DroitAI-RAG-App"
FRONTEND_URL="http://localhost:3000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --app-name)
            APP_NAME="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--app-name NAME] [--frontend-url URL]"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'

# Get tenant info
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "✅ Tenant ID: $TENANT_ID"

# App configuration
APP_NAME="DroitAI-RAG-App"
FRONTEND_URL="http://localhost:3000"

# Create App Registration
echo "🏗️ Creating App Registration: $APP_NAME"
APP_ID=$(az ad app create \
    --display-name "$APP_NAME" \
    --sign-in-audience AzureADMyOrg \
    --web-redirect-uris "${FRONTEND_URL}/auth/callback" \
    --enable-id-token-issuance true \
    --enable-access-token-issuance true \
    --query appId -o tsv 2>/dev/null)

if [ -z "$APP_ID" ]; then
    echo "❌ Failed to create app registration. Please check your Azure permissions."
    exit 1
fi

echo "✅ App Created!"
echo "🔑 Client ID: $APP_ID"

# Create Service Principal
echo "🔐 Creating Service Principal..."
az ad sp create --id $APP_ID --only-show-errors

# Add API Permissions (Microsoft Graph User.Read)
echo "📋 Adding Microsoft Graph permissions..."
az ad app permission add \
    --id $APP_ID \
    --api 00000003-0000-0000-c000-000000000000 \
    --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope \
    --only-show-errors

# Expose API for OBO flow
echo "🌐 Exposing API for OBO flow..."
az ad app update \
    --id $APP_ID \
    --identifier-uris "api://${APP_ID}" \
    --only-show-errors

# Create Client Secret
echo "🔑 Creating Client Secret..."
CLIENT_SECRET=$(az ad app credential reset \
    --id $APP_ID \
    --append \
    --display-name "DroitAI-Client-Secret" \
    --years 1 \
    --query password -o tsv 2>/dev/null)

if [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Failed to create client secret. Please check your Azure permissions."
    exit 1
fi

echo "✅ Client Secret generated"

# Grant admin consent
echo "🎯 Granting admin consent..."
az ad app permission grant --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --only-show-errors || {
    echo "⚠️ Admin consent failed. Please grant consent manually in Azure Portal."
}

# Output configuration
echo ""
echo "🎉 === ENTRA ID APP CONFIGURATION ==="
echo "🔑 Client ID: $APP_ID"
echo "🏢 Tenant ID: $TENANT_ID"
echo "🔐 Client Secret: $CLIENT_SECRET"
echo "🔄 Redirect URI: ${FRONTEND_URL}/auth/callback"
echo "🌐 API Scope: api://${APP_ID}/access_as_user"
echo "📊 Graph Scope: https://graph.microsoft.com/User.Read"

# Create .env file
cat > .env.entra << EOF
# Entra ID Configuration
ENTRA_APP_CLIENT_ID=$APP_ID
ENTRA_APP_TENANT_ID=$TENANT_ID
ENTRA_APP_CLIENT_SECRET=$CLIENT_SECRET
ENTRA_APP_REDIRECT_URI=${FRONTEND_URL}/auth/callback
ENTRA_APP_API_SCOPE=api://${APP_ID}/access_as_user
ENTRA_APP_GRAPH_SCOPE=https://graph.microsoft.com/User.Read
EOF

echo ""
echo "💾 Environment variables saved to .env.entra"

echo ""
echo "🚀 === NEXT STEPS ==="
echo "1️⃣ Update your AZD environment:"
echo "   azd env set ENTRA_APP_CLIENT_ID $APP_ID"
echo "   azd env set ENTRA_APP_CLIENT_SECRET $CLIENT_SECRET"
echo "   azd env set ENTRA_APP_TENANT_ID $TENANT_ID"
echo ""
echo "2️⃣ Deploy your application:"
echo "   azd up"
echo ""
echo "🎉 Entra ID setup completed successfully!" 🎉
