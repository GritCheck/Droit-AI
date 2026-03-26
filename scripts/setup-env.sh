#!/bin/bash

echo "Starting Entra ID App Registration for DroitAI..."

# 1. Create the Backend App Registration
BACKEND_NAME="droitai-backend-${AZURE_ENV_NAME}"
BACKEND_APP=$(az ad app create --display-name "$BACKEND_NAME" --sign-in-audience AzureADMyOrg)
BACKEND_CLIENT_ID=$(echo $BACKEND_APP | jq -r .appId)
BACKEND_OBJECT_ID=$(echo $BACKEND_APP | jq -r .id)

# 2. Expose an API Scope (access_as_user)
az ad app update --id $BACKEND_CLIENT_ID --identifier-uris "api://$BACKEND_CLIENT_ID"
az ad app api-permission add --id $BACKEND_CLIENT_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope

# 3. Create the Frontend App Registration
FRONTEND_NAME="droitai-frontend-${AZURE_ENV_NAME}"
FRONTEND_APP=$(az ad app create --display-name "$FRONTEND_NAME" --sign-in-audience AzureADMyOrg)
FRONTEND_CLIENT_ID=$(echo $FRONTEND_APP | jq -r .appId)

# 4. Save these to your azd environment
azd env set BACKEND_CLIENT_ID $BACKEND_CLIENT_ID
azd env set FRONTEND_CLIENT_ID $FRONTEND_CLIENT_ID

echo "Identity setup complete. Backend ID: $BACKEND_CLIENT_ID"