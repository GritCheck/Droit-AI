@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

@description('Environment name')
param environment string = 'dev'

@description('App Service Plan SKU')
param appServicePlanSku string = 'B1'

@description('App Service Plan capacity')
param appServicePlanCapacity int = 1

@description('Python runtime version')
param pythonRuntimeVersion string = 'PYTHON|3.11'

@description('App startup command')
param appCommandLine string = './startup.sh'

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  sku: {
    name: appServicePlanSku
    capacity: appServicePlanCapacity
  }
  properties: {
    reserved: true // Linux
  }
  tags: {
    azdServiceName: 'appservice'
    azdEnvName: environment
    purpose: 'DroitAI App Service Plan'
  }
}

// User Assigned Managed Identity
resource appServiceIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-identity'
  location: location
  tags: {
    azdServiceName: 'identity'
    azdEnvName: environment
    purpose: 'DroitAI Managed Identity'
  }
}

// Application Insights for Monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
  tags: {
    azdServiceName: 'appinsights'
    azdEnvName: environment
    purpose: 'DroitAI Application Insights'
  }
}

// App Service - DroitAI Backend API
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appName}-app'
  location: location
  tags: {
    azdServiceName: 'app'
    azdEnvName: environment
    purpose: 'DroitAI Backend API'
    runtime: 'Python 3.11 on Linux'
    framework: 'FastAPI with Uvicorn'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appServiceIdentity.id}': {}
    }
  }
  kind: 'linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: pythonRuntimeVersion
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      remoteDebuggingEnabled: false
      appCommandLine: appCommandLine
      use32BitWorkerProcess: true
      webSocketsEnabled: false
      ftpsState: 'FtpsOnly'
      healthCheckPath: null
      detailedErrorLoggingEnabled: false
      httpLoggingEnabled: false
      loadBalancing: 'LeastRequests'
      minimumElasticInstanceCount: 1
      preWarmedInstanceCount: 0
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'true'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot'
        }
      ]
      connectionStrings: []
    }
    httpsOnly: true
    clientAffinityEnabled: false
    reserved: true
  }
}

// Outputs
output appServicePlanName string = appServicePlan.name
output appServicePlanId string = appServicePlan.id
output appServiceIdentityName string = appServiceIdentity.name
output appServiceIdentityId string = appServiceIdentity.id
output appServiceIdentityPrincipalId string = appServiceIdentity.properties.principalId
output appInsightsName string = appInsights.name
output appInsightsId string = appInsights.id
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appServiceName string = appService.name
output appServiceId string = appService.id
output appServiceDefaultHostName string = appService.properties.defaultHostName
output appServiceEndpoint string = 'https://${appService.properties.defaultHostName}'
