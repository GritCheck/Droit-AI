@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the application.')
param appName string = 'droitai${uniqueString(resourceGroup().id)}'

@description('SKU for Azure AI Search.')
param searchSku string = 'basic'

@description('SKU for Azure OpenAI.')
param openaiSku string = 'S0'

@description('SKU for Azure Document Intelligence.')
param docIntelSku string = 'S0'

@description('SKU for Azure Content Safety.')
param contentSafetySku string = 'S0'

@description('SKU for Azure Storage.')
param storageSku string = 'Standard_LRS'

// Resource outputs
output AZURE_SEARCH_ENDPOINT string = searchAccount.properties.endpoint
output AZURE_SEARCH_KEY string = listKeys(searchAccount.id, searchAccount.apiVersion).primaryKey
output AZURE_OPENAI_ENDPOINT string = openaiAccount.properties.endpoint
output AZURE_OPENAI_KEY string = listKeys(openaiAccount.id, openaiAccount.apiVersion).primaryKey
output AZURE_DOC_INTELLIGENCE_ENDPOINT string = docIntelAccount.properties.endpoint
output AZURE_DOC_INTELLIGENCE_KEY string = listKeys(docIntelAccount.id, docIntelAccount.apiVersion).primaryKey
output AZURE_CONTENT_SAFETY_ENDPOINT string = contentSafetyAccount.properties.endpoint
output AZURE_CONTENT_SAFETY_KEY string = listKeys(contentSafetyAccount.id, contentSafetyAccount.apiVersion).primaryKey
output AZURE_STORAGE_CONNECTION_STRING string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value}'

// Azure AI Search
resource searchAccount 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${appName}-search'
  location: location
  sku: {
    name: searchSku
  }
  properties: {
    hostingMode: 'default'
    partitionCount: 1
    replicaCount: 1
    semanticSearch: 'free'
  }
}

// Azure OpenAI
resource openaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${appName}-openai'
  location: location
  sku: {
    name: openaiSku
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: '${appName}-openai'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    restore: false
    encryption: {
      keySource: 'Microsoft.Keyvault'
    }
  }
}

// Azure OpenAI Deployments
resource gpt4Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openaiAccount
  name: 'gpt-4'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4'
      version: 'latest'
    }
    scaleSettings: {
      scaleType: 'Standard'
    }
    raiPolicyName: 'Default'
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openaiAccount
  name: 'text-embedding-ada-002'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    scaleSettings: {
      scaleType: 'Standard'
    }
  }
}

// Azure Document Intelligence
resource docIntelAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${appName}-docintel'
  location: location
  sku: {
    name: docIntelSku
  }
  kind: 'FormRecognizer'
  properties: {
    customSubDomainName: '${appName}-docintel'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    restore: false
  }
}

// Azure Content Safety
resource contentSafetyAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${appName}-contentsafety'
  location: location
  sku: {
    name: contentSafetySku
  }
  kind: 'ContentSafety'
  properties: {
    customSubDomainName: '${appName}-contentsafety'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    restore: false
  }
}

// Azure Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${appName}storage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowSharedKeyAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

// Storage Container for Documents
resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccount
  name: 'default/documents'
  properties: {
    publicAccess: 'None'
    metadata: {
      purpose: 'document-processing'
      service: 'droitai'
    }
  }
}

// Application Insights for Monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}
