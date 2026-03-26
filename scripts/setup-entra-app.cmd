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
set BACKEND_APP_NAME=DroitAI-RAG-Backend-App
set FRONTEND_APP_NAME=DroitAI-RAG-Frontend-App
set FRONTEND_URL=http://localhost:3000
set BACKEND_URL=http://localhost:8000

echo 🏗️ Setting up Entra ID Apps for DroitAI...
echo 📦 Backend App: %BACKEND_APP_NAME%
echo 📦 Frontend App: %FRONTEND_APP_NAME%

REM Create Backend App Registration
echo 🏗️ Creating Backend App Registration: %BACKEND_APP_NAME%
for /f "tokens=*" %%i in ('az ad app create --display-name "%BACKEND_APP_NAME%" --sign-in-audience AzureADMyOrg --web-redirect-uris "%FRONTEND_URL%/auth/callback" --enable-id-token-issuance true --enable-access-token-issuance true --query appId -o tsv 2^>nul') do set BACKEND_APP_ID=%%i

if "%BACKEND_APP_ID%"=="" (
    echo ❌ Failed to create backend app registration. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ Backend App Created!
echo 🔑 Backend Client ID: %BACKEND_APP_ID%

REM Create Backend Service Principal
echo 🔐 Creating Backend Service Principal...
az ad sp create --id %BACKEND_APP_ID% --only-show-errors

REM Add API Permissions (Microsoft Graph User.Read)
echo 📋 Adding Microsoft Graph permissions to backend...
az ad app permission add --id %BACKEND_APP_ID% --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope --only-show-errors

REM Expose API for OBO flow
echo 🌐 Exposing API for OBO flow...
az ad app update --id %BACKEND_APP_ID% --identifier-uris "api://%BACKEND_APP_ID%" --only-show-errors

REM Create Backend Client Secret
echo 🔑 Creating Backend Client Secret...
for /f "tokens=*" %%i in ('az ad app credential reset --id %BACKEND_APP_ID% --append --display-name "DroitAI-Backend-Client-Secret" --years 1 --query password -o tsv 2^>nul') do set BACKEND_CLIENT_SECRET=%%i

if "%BACKEND_CLIENT_SECRET%"=="" (
    echo ❌ Failed to create backend client secret. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ Backend Client Secret generated

REM Grant admin consent for backend
echo 🎯 Granting admin consent for backend...
az ad app permission grant --id %BACKEND_APP_ID% --api 00000003-0000-0000-c000-000000000000 --only-show-errors || (
    echo ⚠️ Backend admin consent failed. Please grant consent manually in Azure Portal.
)

REM Create Frontend App Registration
echo 🏗️ Creating Frontend App Registration: %FRONTEND_APP_NAME%
for /f "tokens=*" %%i in ('az ad app create --display-name "%FRONTEND_APP_NAME%" --sign-in-audience AzureADMyOrg --web-redirect-uris "%FRONTEND_URL%/auth/callback" --enable-id-token-issuance true --query appId -o tsv 2^>nul') do set FRONTEND_APP_ID=%%i

if "%FRONTEND_APP_ID%"=="" (
    echo ❌ Failed to create frontend app registration. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ Frontend App Created!
echo 🔑 Frontend Client ID: %FRONTEND_APP_ID%

REM Create Frontend Service Principal
echo 🔐 Creating Frontend Service Principal...
az ad sp create --id %FRONTEND_APP_ID% --only-show-errors

REM Add API Permissions (Microsoft Graph User.Read)
echo 📋 Adding Microsoft Graph permissions to frontend...
az ad app permission add --id %FRONTEND_APP_ID% --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89b7-286741c1f4e6=Scope --only-show-errors

REM Create Frontend Client Secret
echo 🔑 Creating Frontend Client Secret...
for /f "tokens=*" %%i in ('az ad app credential reset --id %FRONTEND_APP_ID% --append --display-name "DroitAI-Frontend-Client-Secret" --years 1 --query password -o tsv 2^>nul') do set FRONTEND_CLIENT_SECRET=%%i

if "%FRONTEND_CLIENT_SECRET%"=="" (
    echo ❌ Failed to create frontend client secret. Please check your Azure permissions.
    pause
    exit /b 1
)

echo ✅ Frontend Client Secret generated

REM Grant admin consent for frontend
echo 🎯 Granting admin consent for frontend...
az ad app permission grant --id %FRONTEND_APP_ID% --api 00000003-0000-0000-c000-000000000000 --only-show-errors || (
    echo ⚠️ Frontend admin consent failed. Please grant consent manually in Azure Portal.
)

REM Output configuration
echo.
echo 🎉 === ENTRA ID APP CONFIGURATION ===
echo 🏢 Tenant ID: %TENANT_ID%
echo.
echo � BACKEND APP:
echo �🔑 Backend Client ID: %BACKEND_APP_ID%
echo 🔐 Backend Client Secret: %BACKEND_CLIENT_SECRET%
echo � Backend API Scope: api://%BACKEND_APP_ID%/access_as_user
echo 📊 Backend Graph Scope: https://graph.microsoft.com/User.Read
echo.
echo 📦 FRONTEND APP:
echo 🔑 Frontend Client ID: %FRONTEND_APP_ID%
echo 🔐 Frontend Client Secret: %FRONTEND_CLIENT_SECRET%
echo 🔄 Frontend Redirect URI: %FRONTEND_URL%/auth/callback
echo 📊 Frontend Graph Scope: https://graph.microsoft.com/User.Read

REM Create .env file
echo # Entra ID Configuration > .env.entra
echo # Backend Configuration >> .env.entra
echo ENTRA_APP_CLIENT_ID=%BACKEND_APP_ID% >> .env.entra
echo ENTRA_APP_CLIENT_SECRET=%BACKEND_CLIENT_SECRET% >> .env.entra
echo ENTRA_APP_TENANT_ID=%TENANT_ID% >> .env.entra
echo ENTRA_APP_API_SCOPE=api://%BACKEND_APP_ID%/access_as_user >> .env.entra
echo ENTRA_APP_GRAPH_SCOPE=https://graph.microsoft.com/User.Read >> .env.entra
echo.
echo # Frontend Configuration >> .env.entra
echo FRONTEND_ENTRA_CLIENT_ID=%FRONTEND_APP_ID% >> .env.entra
echo FRONTEND_ENTRA_CLIENT_SECRET=%FRONTEND_CLIENT_SECRET% >> .env.entra
echo FRONTEND_ENTRA_REDIRECT_URI=%FRONTEND_URL%/auth/callback >> .env.entra

echo.
echo 💾 Environment variables saved to .env.entra

echo.
echo 🚀 === NEXT STEPS ===
echo 1️⃣ Update your AZD environment with backend settings:
echo    azd env set ENTRA_APP_CLIENT_ID %BACKEND_APP_ID%
echo    azd env set ENTRA_APP_CLIENT_SECRET %BACKEND_CLIENT_SECRET%
echo    azd env set ENTRA_APP_TENANT_ID %TENANT_ID%
echo.
echo 2️⃣ Update your AZD environment with frontend settings:
echo    azd env set FRONTEND_ENTRA_CLIENT_ID %FRONTEND_APP_ID%
echo    azd env set FRONTEND_ENTRA_CLIENT_SECRET %FRONTEND_CLIENT_SECRET%
echo.
echo 3️⃣ Deploy your application:
echo    azd up
echo.
echo 🎉 Entra ID setup completed successfully!
pause
