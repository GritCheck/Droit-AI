@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string = 'droitai'

@description('Environment name')
param environment string = 'dev'

@secure()
param backendClientId string = ''

@secure()
param frontendClientId string = ''

// --- 1. CORE INFRASTRUCTURE MODULES ---

module storage 'storage.bicep' = {
  name: 'storageDeployment'
  params: {
    location: location
    appName: appName
    containerName: 'documents'
  }
}

module search 'search.bicep' = {
  name: 'searchDeployment'
  params: {
    location: location
    appName: appName
    searchSku: 'standard' // Recommended for Semantic Ranking in CUAD
  }
}

module aiServices 'ai-services.bicep' = {
  name: 'aiServicesDeployment'
  params: {
    location: location
    appName: appName
    chatDeploymentName: 'gpt-4o'
    embeddingDeploymentName: 'text-embedding-3-small'
  }
}

module host 'host.bicep' = {
  name: 'hostDeployment'
  params: {
    location: location
    appName: appName
    environment: environment
    useUniqueNaming: true
    backendClientId: backendClientId
    frontendClientId: frontendClientId
    // Pass endpoints from other modules
    backendApiEndpoint: 'https://${appName}-app.azurewebsites.net'
  }
}

// --- 2. IDENTITY & LEAST PRIVILEGE RBAC ---
// Note: Using the Principal ID of the Backend App Service Managed Identity

var roles = [
  { name: 'StorageBlobDataContributor', id: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' }
  { name: 'SearchIndexDataReader', id: '1407120a-92aa-4202-b7e9-c0e197c71c8f' }
  { name: 'SearchServiceContributor', id: '7ca78c08-252a-4471-8644-bb5ff32d4ba0' }
  { name: 'CognitiveServicesUser', id: 'a97b65f3-24c7-4388-baec-2e87135dc908' }
]

// Loop through and assign roles to the backend identity
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for role in roles: {
  name: guid(appName, role.name, 'backend-identity')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', role.id)
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}]

// --- 3. OUTPUTS ---
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.storageAccountName
output AZURE_SEARCH_SERVICE_NAME string = search.outputs.searchServiceName
output AZURE_OPENAI_ENDPOINT string = aiServices.outputs.openaiEndpoint
output BACKEND_URI string = host.outputs.appServiceEndpoint
output FRONTEND_URI string = host.outputs.frontendAppServiceEndpoint
