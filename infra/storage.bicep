@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

@description('Environment name')
param environment string = 'dev'

@description('Storage SKU')
param storageSku string = 'Standard_LRS'

@description('Container name')
param containerName string = 'documents'

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'st${uniqueString(appName)}'
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    supportsHttpsTrafficOnly: true
  }
  tags: {
    'azd-service-name': 'storage'
    'azd-env-name': environment
    purpose: 'DroitAI Document Storage'
  }
}

// Blob Service
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// Blob Container
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: containerName
  properties: {
    publicAccess: 'None'
  }
}

// Outputs
output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
output storageAccountPrimaryEndpoint string = storageAccount.properties.primaryEndpoints.web
output blobContainerName string = blobContainer.name
output blobContainerId string = blobContainer.id
