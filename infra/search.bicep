@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

@description('Environment name')
param environment string = 'dev'

@description('Search SKU')
param searchSku string = 'basic' // Note: 'standard' is recommended for high-volume Semantic Ranking

@description('Replica count')
param replicaCount int = 1

@description('Partition count')
param partitionCount int = 1

// Azure AI Search Service
resource searchAccount 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${appName}-search'
  location: location
  sku: {
    name: searchSku
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
    }
  }
  tags: {
    azdServiceName: 'search'
    azdEnvName: environment
    purpose: 'DroitAI Search Service'
  }
}

// Outputs
output searchServiceName string = searchAccount.name
output searchServiceId string = searchAccount.id
output searchServiceEndpoint string = 'https://${searchAccount.name}.search.windows.net/'
