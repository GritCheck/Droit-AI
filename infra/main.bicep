@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string = 'droitai'

@description('Environment name')
param environment string = 'dev'

// Deploy modules
module storage 'modules/storage.bicep' = {
  name: 'storageDeployment'
  params: {
    location: location
    appName: appName
    containerName: 'documents'
  }
}

module search 'modules/search.bicep' = {
  name: 'searchDeployment'
  params: {
    location: location
    appName: appName
  }
}

module aiServices 'modules/ai-services.bicep' = {
  name: 'aiServicesDeployment'
  params: {
    location: location
    appName: appName
    chatDeploymentName: 'gpt-4o'
    embeddingDeploymentName: 'text-embedding-ada-002'
  }
}

module host 'modules/host.bicep' = {
  name: 'hostDeployment'
  params: {
    location: location
    appName: appName
    environment: environment
    appCommandLine: './startup.sh'
  }
}

// Role Assignments for Least Privilege Access
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', 'st${uniqueString(appName)}', 'StorageBlobDataContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource storageQueueRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', 'st${uniqueString(appName)}', 'StorageQueueDataContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource searchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', '${appName}-search', 'SearchServiceContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource searchIndexDataRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', '${appName}-search', 'SearchIndexDataReader')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '1407120a-92aa-4202-b7e9-c0e197c71c8f')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource openaiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', '${appName}-openai', 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource docIntelRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', '${appName}-docintel', 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource contentSafetyRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appName}-identity', '${appName}-contentsafety', 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: host.outputs.appServiceIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output storageAccountName string = storage.outputs.storageAccountName
output searchServiceName string = search.outputs.searchServiceName
output searchServiceEndpoint string = search.outputs.searchServiceEndpoint
output openaiEndpoint string = aiServices.outputs.openaiEndpoint
output openaiChatDeploymentName string = aiServices.outputs.chatDeploymentName
output openaiEmbeddingDeploymentName string = aiServices.outputs.embeddingDeploymentName
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storage.outputs.storageAccountName};AccountKey=${storage.outputs.storageAccountKey};EndpointSuffix=core.windows.net'
output storageAccountKey string = storage.outputs.storageAccountKey
output storageContainerName string = storage.outputs.blobContainerName
output appServiceName string = host.outputs.appServiceName
output appServiceEndpoint string = host.outputs.appServiceEndpoint
output appServiceIdentityId string = host.outputs.appServiceIdentityId
output appInsightsInstrumentationKey string = host.outputs.appInsightsInstrumentationKey
