@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

@description('OpenAI SKU')
param openaiSku string = 'S0'

@description('Chat deployment name')
param chatDeploymentName string = 'gpt-4o'

@description('Embedding deployment name')
param embeddingDeploymentName string = 'text-embedding-ada-002'

@description('Chat model version')
param chatModelVersion string = '2024-05-13'

@description('Embedding model version')
param embeddingModelVersion string = '2'

// Azure OpenAI Account
resource openaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${appName}-openai'
  location: location
  sku: {
    name: openaiSku
  }
  kind: 'OpenAI'
  properties: {
    networkAcls: {
      defaultAction: 'Allow'
      
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    restore: false
    customSubDomainName: '${appName}-openai'
  }
  tags: {
    azdServiceName: 'openai'
    azdEnvName: 'dev'
    purpose: 'DroitAI OpenAI Service'
  }
}

// Azure OpenAI Deployments
resource gpt4Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openaiAccount
  name: chatDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: chatModelVersion 
    }
    raiPolicyName: 'Microsoft.DefaultV2'
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}


resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openaiAccount
  dependsOn: [
    gpt4Deployment
  ]
  name: embeddingDeploymentName
  sku: {
    name: 'Standard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingDeploymentName
      version: embeddingModelVersion
    }
    raiPolicyName: 'Microsoft.DefaultV2'
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

// Azure Document Intelligence
resource docIntelAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${appName}-docintel'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'FormRecognizer'
  properties: {
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
    name: 'S0'
  }
  kind: 'ContentSafety'
  properties: {
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    restore: false
  }
}

// Outputs
output openaiAccountName string = openaiAccount.name
output openaiAccountId string = openaiAccount.id
output openaiEndpoint string = openaiAccount.properties.endpoint
output openaiKey string = openaiAccount.listKeys().key1
output chatDeploymentName string = gpt4Deployment.name
output embeddingDeploymentName string = embeddingDeployment.name
output docIntelAccountName string = docIntelAccount.name
output docIntelAccountId string = docIntelAccount.id
output docIntelEndpoint string = docIntelAccount.properties.endpoint
output docIntelKey string = docIntelAccount.listKeys().key1
output contentSafetyAccountName string = contentSafetyAccount.name
output contentSafetyAccountId string = contentSafetyAccount.id
output contentSafetyEndpoint string = contentSafetyAccount.properties.endpoint
output contentSafetyKey string = contentSafetyAccount.listKeys().key1
