@echo off
echo 🔧 Setting up Entra ID App for DroitAI...

REM Check if Azure CLI is installed
az --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Azure CLI not found. Please install it first.
    echo Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)

REM Login to Azure
echo 📝 Logging in to Azure...
az login

REM Get tenant info
for /f "tokens=*" %%i in ('az account show --query tenantId -o tsv') do set TENANT_ID=%%i
echo ✅ Tenant ID: %TENANT_ID%

REM App configuration
set APP_NAME=DroitAI-RAG-App
set FRONTEND_URL=http://localhost:3000

REM Create App Registration
echo 🏗️ Creating App Registration: %APP_NAME%
for /f "tokens=*" %%i in ('az ad app create --display-name "%APP_NAME%" --sign-in-audience AzureADMyOrg --web-redirect-uris "%FRONTEND_URL%/auth/callback" --enable-id-token-issuance true --enable-access-token-issuance true --query appId -o tsv 2^>nul') do set APP_ID=%%i

if "%APP_ID%"=="" (
    echo ❌ Failed to create app registration. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ App Created!
echo 🔑 Client ID: %APP_ID%

REM Create Service Principal
echo 🔐 Creating Service Principal...
az ad sp create --id %APP_ID% --only-show-errors

REM Add API Permissions (Microsoft Graph User.Read)
echo 📋 Adding Microsoft Graph permissions...
az ad app permission add --id %APP_ID% --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope --only-show-errors

REM Expose API for OBO flow
echo 🌐 Exposing API for OBO flow...
az ad app update --id %APP_ID% --identifier-uris "api://%APP_ID%" --only-show-errors

REM Create Client Secret
echo 🔑 Creating Client Secret...
for /f "tokens=*" %%i in ('az ad app credential reset --id %APP_ID% --append --display-name "DroitAI-Client-Secret" --years 1 --query password -o tsv 2^>nul') do set CLIENT_SECRET=%%i

if "%CLIENT_SECRET%"=="" (
    echo ❌ Failed to create client secret. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ Client Secret generated

REM Grant admin consent
echo 🎯 Granting admin consent...
az ad app permission grant --id %APP_ID% --api 00000003-0000-0000-c000-000000000000 --only-show-errors || (
    echo ⚠️ Admin consent failed. Please grant consent manually in Azure Portal.
)

REM Output configuration
echo.
echo 🎉 === ENTRA ID APP CONFIGURATION ===
echo 🔑 Client ID: %APP_ID%
echo 🏢 Tenant ID: %TENANT_ID%
echo 🔐 Client Secret: %CLIENT_SECRET%
echo 🔄 Redirect URI: %FRONTEND_URL%/auth/callback
echo 🌐 API Scope: api://%APP_ID%/access_as_user
echo 📊 Graph Scope: https://graph.microsoft.com/User.Read

REM Create .env file
echo # Entra ID Configuration > .env.entra
echo ENTRA_APP_CLIENT_ID=%APP_ID% >> .env.entra
echo ENTRA_APP_TENANT_ID=%TENANT_ID% >> .env.entra
echo ENTRA_APP_CLIENT_SECRET=%CLIENT_SECRET% >> .env.entra
echo ENTRA_APP_REDIRECT_URI=%FRONTEND_URL%/auth/callback >> .env.entra
echo ENTRA_APP_API_SCOPE=api://%APP_ID%/access_as_user >> .env.entra
echo ENTRA_APP_GRAPH_SCOPE=https://graph.microsoft.com/User.Read >> .env.entra

echo.
echo 💾 Environment variables saved to .env.entra

echo.
echo 🚀 === NEXT STEPS ===
echo 1️⃣ Update your AZD environment:
echo    azd env set ENTRA_APP_CLIENT_ID %APP_ID%
echo    azd env set ENTRA_APP_CLIENT_SECRET %CLIENT_SECRET%
echo    azd env set ENTRA_APP_TENANT_ID %TENANT_ID%
echo.
echo 2️⃣ Deploy your application:
echo    azd up
echo.
echo 🎉 Entra ID setup completed successfully!
pause
