@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the application.')
param appName string = 'droitai${uniqueString(resourceGroup().id)}'

@description('SKU for App Service Plan.')
param appServicePlanSku string = 'P1v2'

@description('Runtime stack for App Service.')
param runtimeStack string = 'PYTHON|3.11'

@description('Always On setting for App Service.')
param alwaysOn bool = true

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${appName}-plan'
  location: location
  sku: {
    name: appServicePlanSku
  }
  kind: 'linux'
  properties: {
    reserved: true
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    zoneRedundant: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
  }
}

// App Service for Backend API
resource appService 'Microsoft.Web/sites@2023-12-01' = {
  name: '${appName}-api'
  location: location
  kind: 'linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: alwaysOn
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      remoteDebuggingEnabled: false
      webSocketsEnabled: true
      linuxFxVersion: runtimeStack
      appCommandLine: 'uvicorn app.main:app --host 0.0.0.0 --port 8080'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot'
        }
        {
          name: 'LOG_LEVEL'
          value: 'INFO'
        }
      ]
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
}

// Application Settings for Backend
resource appSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: appService
  name: 'appsettings'
  properties: {
    // These will be populated by azd from environment variables
    // AZURE_SEARCH_ENDPOINT
    // AZURE_SEARCH_KEY
    // AZURE_OPENAI_ENDPOINT
    // AZURE_OPENAI_KEY
    // AZURE_DOC_INTELLIGENCE_ENDPOINT
    // AZURE_DOC_INTELLIGENCE_KEY
    // AZURE_CONTENT_SAFETY_ENDPOINT
    // AZURE_CONTENT_SAFETY_KEY
    // AZURE_STORAGE_CONNECTION_STRING
  }
}

// CORS Configuration for App Service
resource cors 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: appService
  name: 'web'
  properties: {
    cors: {
      allowedOrigins: [
        '*' // In production, this should be restricted to your frontend URL
      ]
      supportCredentials: false
    }
  }
}

// Output for App Service URL
output BACKEND_URL string = 'https://${appService.properties.defaultHostName}'
