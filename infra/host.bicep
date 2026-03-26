@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

@description('Environment name')
param environment string = 'dev'

@description('Use unique naming to avoid conflicts with soft-deleted resources')
param useUniqueNaming bool = true

// Generate unique suffix only when needed
var uniqueSuffix = useUniqueNaming ? '-${uniqueString(resourceGroup().id)}' : ''

@description('App Service Plan SKU')
param appServicePlanSku string = 'B1'

@description('App Service Plan capacity')
param appServicePlanCapacity int = 1

@description('Python runtime version')
param pythonRuntimeVersion string = 'PYTHON|3.11'

@description('Node.js runtime version')
param nodeRuntimeVersion string = 'NODE|20-lts'

@description('Backend app startup command')
param appCommandLine string = './startup.sh'

@description('Application Insights Connection String')
param appInsightsConnectionString string = ''

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string = ''

@description('Backend API endpoint for frontend')
param backendApiEndpoint string = ''

@description('Backend client ID for authentication')
@secure()
param backendClientId string = ''

@description('Frontend client ID for authentication')
@secure()
param frontendClientId string = ''

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
  name: '${appName}-backend-insights${uniqueSuffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
  tags: {
    azdServiceName: 'appinsights'
    azdEnvName: environment
    purpose: 'DroitAI Backend Application Insights'
  }
}

// App Service - DroitAI Backend API
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appName}-app'
  location: location
  tags: {
    'azd-service-name': 'app'
    'azd-env-name': environment
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
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'LOG_ANALYTICS_WORKSPACE_ID'
          value: logAnalyticsWorkspaceId
        }
        {
          name: 'BACKEND_CLIENT_ID'
          value: backendClientId
        }
        {
          name: 'FRONTEND_CLIENT_ID'
          value: frontendClientId
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

// Frontend App Service Plan
resource frontendAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-frontend-plan'
  location: location
  sku: {
    name: appServicePlanSku
    capacity: appServicePlanCapacity
  }
  properties: {
    reserved: true // Linux
  }
  tags: {
    azdServiceName: 'frontend-appservice'
    azdEnvName: environment
    purpose: 'DroitAI Frontend App Service Plan'
  }
}

// Frontend User Assigned Managed Identity
resource frontendAppServiceIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-frontend-identity'
  location: location
  tags: {
    azdServiceName: 'frontend-identity'
    azdEnvName: environment
    purpose: 'DroitAI Frontend Managed Identity'
  }
}

// Frontend Application Insights for Monitoring
resource frontendAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-frontend-insights${uniqueSuffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
  tags: {
    azdServiceName: 'frontend-appinsights'
    azdEnvName: environment
    purpose: 'DroitAI Frontend Application Insights'
  }
}

// Frontend App Service - DroitAI Frontend (Next.js)
resource frontendAppService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appName}-frontend'
  location: location
  tags: {
    'azd-service-name': 'frontend'
    'azd-env-name': environment
    purpose: 'DroitAI Frontend (Next.js)'
    runtime: 'Node.js 20 LTS on Linux'
    framework: 'Next.js'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${frontendAppServiceIdentity.id}': {}
    }
  }
  kind: 'linux'
  properties: {
    serverFarmId: frontendAppServicePlan.id
    siteConfig: {
      linuxFxVersion: nodeRuntimeVersion
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      remoteDebuggingEnabled: false
      use32BitWorkerProcess: false
      webSocketsEnabled: true
      ftpsState: 'FtpsOnly'
      healthCheckPath: '/api/health'
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
          name: 'NODE_ENV'
          value: 'production'
        }
        {
          name: 'NEXT_PUBLIC_API_URL'
          value: backendApiEndpoint
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'LOG_ANALYTICS_WORKSPACE_ID'
          value: logAnalyticsWorkspaceId
        }
        {
          name: 'BACKEND_CLIENT_ID'
          value: backendClientId
        }
        {
          name: 'FRONTEND_CLIENT_ID'
          value: frontendClientId
        }
      ]
      connectionStrings: []
    }
    httpsOnly: true
    clientAffinityEnabled: false
    reserved: true
  }
}

// Frontend Outputs
output frontendAppServicePlanName string = frontendAppServicePlan.name
output frontendAppServicePlanId string = frontendAppServicePlan.id
output frontendAppServiceIdentityName string = frontendAppServiceIdentity.name
output frontendAppServiceIdentityId string = frontendAppServiceIdentity.id
output frontendAppServiceIdentityPrincipalId string = frontendAppServiceIdentity.properties.principalId
output frontendAppInsightsName string = frontendAppInsights.name
output frontendAppInsightsId string = frontendAppInsights.id
output frontendAppInsightsInstrumentationKey string = frontendAppInsights.properties.InstrumentationKey
output frontendAppServiceName string = frontendAppService.name
output frontendAppServiceId string = frontendAppService.id
output frontendAppServiceDefaultHostName string = frontendAppService.properties.defaultHostName
output frontendAppServiceEndpoint string = 'https://${frontendAppService.properties.defaultHostName}'
