@echo off
echo 🔧 Auto-populating Azure environment variables from Bicep outputs...

REM Get Document Intelligence endpoint
echo 📡 Getting Document Intelligence endpoint...
for /f "tokens=*" %%i in ('az cognitiveservices account show --name droitai-docintel --resource-group rg-droitaienv --query properties.endpoint -o tsv') do set DOC_INTEL_ENDPOINT=%%i

REM Get Document Intelligence key  
echo 🔑 Getting Document Intelligence key...
for /f "tokens=*" %%i in ('az cognitiveservices account keys list --name droitai-docintel --resource-group rg-droitaienv --query "[0].key1" -o tsv') do set DOC_INTEL_KEY=%%i

REM Get Content Safety endpoint
echo 🛡 Getting Content Safety endpoint...
for /f "tokens=*" %%i in ('az cognitiveservices account show --name droitai-contentsafety --resource-group rg-droitaienv --query properties.endpoint -o tsv') do set CONTENT_SAFETY_ENDPOINT=%%i

REM Get Content Safety key
echo 🔐 Getting Content Safety key...
for /f "tokens=*" %%i in ('az cognitiveservices account keys list --name droitai-contentsafety --resource-group rg-droitaienv --query "[0].key1" -o tsv') do set CONTENT_SAFETY_KEY=%%i

REM Get OpenAI endpoint
echo 🤖 Getting OpenAI endpoint...
for /f "tokens=*" %%i in ('az cognitiveservices account show --name droitai-openai --resource-group rg-droitaienv --query properties.endpoint -o tsv') do set OPENAI_ENDPOINT=%%i

REM Get OpenAI key
echo 🔐 Getting OpenAI key...
for /f "tokens=*" %%i in ('az cognitiveservices account keys list --name droitai-openai --resource-group rg-droitaienv --query "[0].key1" -o tsv') do set OPENAI_KEY=%%i

REM Get Search endpoint and key
echo 🔍 Getting Search endpoint...
for /f "tokens=*" %%i in ('az search service show --name droitai-search --resource-group rg-droitaienv --query endpoint -o tsv') do set SEARCH_ENDPOINT=%%i
for /f "tokens=*" %%i in ('az search service keys list --name droitai-search --resource-group rg-droitaienv --query "[0].key1" -o tsv') do set SEARCH_KEY=%%i

REM Get Storage account name
echo 📦 Getting Storage account name...
for /f "tokens=*" %%i in ('az storage account show --name stifuaoussv3quw --resource-group rg-droitaienv --query name -o tsv') do set STORAGE_ACCOUNT_NAME=%%i

REM Set AZD environment variables
echo 🌐 Setting AZD environment variables...
azd env set AZURE_DOC_INTELLIGENCE_ENDPOINT %DOC_INTEL_ENDPOINT%
azd env set AZURE_DOC_INTELLIGENCE_KEY %DOC_INTEL_KEY%
azd env set AZURE_CONTENT_SAFETY_ENDPOINT %CONTENT_SAFETY_ENDPOINT%
azd env set AZURE_CONTENT_SAFETY_KEY %CONTENT_SAFETY_KEY%
azd env set AZURE_OPENAI_ENDPOINT %OPENAI_ENDPOINT%
azd env set AZURE_OPENAI_KEY %OPENAI_KEY%
azd env set AZURE_SEARCH_ENDPOINT %SEARCH_ENDPOINT%
azd env set AZURE_SEARCH_KEY %SEARCH_KEY%
azd env set AZURE_STORAGE_ACCOUNT_NAME %STORAGE_ACCOUNT_NAME%

echo.
echo ✅ Environment variables populated successfully!
echo.
echo 🎉 === ENVIRONMENT VARIABLES SET ===
echo 📡 Document Intelligence Endpoint: %DOC_INTEL_ENDPOINT%
echo 🔑 Document Intelligence Key: [REDACTED]
echo 🛡 Content Safety Endpoint: %CONTENT_SAFETY_ENDPOINT%
echo 🔐 Content Safety Key: [REDACTED]
echo 🤖 OpenAI Endpoint: %OPENAI_ENDPOINT%
echo 🔐 OpenAI Key: [REDACTED]
echo 🔍 Search Endpoint: %SEARCH_ENDPOINT%
echo 🔑 Search Key: [REDACTED]
echo 📦 Storage Account: %STORAGE_ACCOUNT_NAME%
echo.
echo 🚀 AZD environment updated! Ready for deployment.
echo.
pause
