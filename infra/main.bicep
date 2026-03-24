@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the application.')
param appName string = 'droitai${uniqueString(resourceGroup().id)}'

@description('SKU for Azure AI Search.')
param searchSku string = 'free'

@description('SKU for Azure OpenAI.')
param openaiSku string = 'S0'

@description('SKU for Azure Document Intelligence.')
param docIntelSku string = 'F0'

@description('SKU for Azure Content Safety.')
param contentSafetySku string = 'F0'

@description('SKU for Azure Storage.')
param storageSku string = 'Standard_LRS'

@description('Enable managed identity for App Service')
param enableManagedIdentity bool = true

@description('Frontend URL for CORS configuration')
param frontendUrl string = 'http://localhost:3000'

@description('Enable OBO token flow for user delegation')
param enableOboFlow bool = true

// Resource outputs - Non-sensitive only
output AZURE_SEARCH_ENDPOINT string = 'https://${searchAccount.name}.search.windows.net'
output AZURE_OPENAI_ENDPOINT string = openaiAccount.properties.endpoint
output AZURE_OPENAI_CHAT_DEPLOYMENT_NAME string = gpt4Deployment.name
output AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME string = embeddingDeployment.name
output AZURE_OPENAI_API_VERSION string = '2024-02-15-preview'
output AZURE_DOC_INTELLIGENCE_ENDPOINT string = docIntelAccount.properties.endpoint
output AZURE_CONTENT_SAFETY_ENDPOINT string = contentSafetyAccount.properties.endpoint
output AZURE_STORAGE_CONTAINER_NAME string = 'documents'
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_SEARCH_INDEX_NAME string = 'droitai-index'
output AZURE_AD_TENANT_ID string = tenant().tenantId
output APP_SERVICE_IDENTITY_PRINCIPAL_ID string = appServiceIdentity.properties.principalId
output APP_SERVICE_IDENTITY_CLIENT_ID string = appServiceIdentity.properties.clientId
output APP_SERVICE_ENDPOINT string = 'https://${appService.name}.azurewebsites.net'
output FRONTEND_URL string = frontendUrl
output LOG_LEVEL string = 'INFO'
output ENABLE_LOCAL_PARSING string = 'false'
output ENABLE_OBO_FLOW string = enableOboFlow ? 'true' : 'false'
// Note: Entra ID configuration must be set manually after app creation
output ENTRA_APP_CLIENT_ID string = 'SETUP_REQUIRED'
output ENTRA_APP_CLIENT_SECRET string = 'SETUP_REQUIRED'
output ENTRA_APP_TENANT_ID string = tenant().tenantId
output ENTRA_APP_REDIRECT_URI string = '${frontendUrl}/auth/callback'
output ENTRA_APP_GRAPH_SCOPE string = 'https://graph.microsoft.com/User.Read'
output ENTRA_APP_API_SCOPE string = 'SETUP_AFTER_APP_CREATION'

// Azure AI Search with enhanced security
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
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    publicNetworkAccess: 'enabled'
  }
  tags: {
    purpose: 'droitai-search'
    environment: 'production'
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
  }
}

// Azure OpenAI Deployments
resource gpt4Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openaiAccount
  name: 'gpt-4'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
    sku: {
      name: 'Standard'
      capacity: 1
    }
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
    sku: {
      name: 'Standard'
      capacity: 1
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

// Azure Storage Account with enhanced security
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'st${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowSharedKeyAccess: false // Disable shared key access for security
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Deny' // Deny by default for security
      ipRules: []
      bypass: 'AzureServices' // Allow only Azure services bypass
      virtualNetworkRules: []
    }
    encryption: {
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
  tags: {
    purpose: 'droitai-storage'
    environment: 'production'
  }
}

// Storage Container for Documents
resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/documents'
  properties: {
    publicAccess: 'None'
    metadata: {
      purpose: 'document-processing'
      service: 'droitai'
    }
  }
}

// App Service with Managed Identity and enhanced security
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appName}-app'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      remoteDebuggingEnabled: false
      httpLoggingEnabled: true
      detailedErrorLoggingEnabled: true
      appCommandLine: 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
      cors: {
        allowedOrigins: [
          frontendUrl
        ]
        supportCredentials: true
      }
      ipSecurityRestrictions: [
        {
          ipAddress: '0.0.0.0/0'
          action: 'Allow'
          description: 'Allow all traffic (restrict in production)'
          priority: 1
        }
      ]
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
  identity: {
    type: enableManagedIdentity ? 'UserAssigned' : 'None'
    userAssignedIdentities: enableManagedIdentity ? {
      '${appServiceIdentity.id}': {}
    } : {}
  }
  tags: {
    purpose: 'droitai-backend'
    environment: 'production'
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true // Linux
  }
}

// User Assigned Managed Identity
resource appServiceIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-identity'
  location: location
}

// Role Assignments for Least Privilege Access
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, storageAccount.id, 'StorageBlobDataContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-7d92-4da1-a78d-0a3886b4b3f4') // Storage Blob Data Contributor
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: storageAccount
}

resource storageQueueRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, storageAccount.id, 'StorageQueueDataContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f8bbdddee86') // Storage Queue Data Contributor
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: storageAccount
}

resource searchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, searchAccount.id, 'SearchServiceContributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca33c8a-e09a-4d5a-843b-2f2edfbdcdf5') // Search Service Contributor
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: searchAccount
}

resource searchIndexDataRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, searchAccount.id, 'SearchIndexDataReader')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '1407120a-92aa-4d4c-9233-f9b5a6c8b3b2') // Search Index Data Reader
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: searchAccount
}

resource openaiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, openaiAccount.id, 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b6593-5c8b-4d1b-8e3b-123b2968d2d9') // Cognitive Services User
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: openaiAccount
}

resource docIntelRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, docIntelAccount.id, 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b6593-5c8b-4d1b-8e3b-123b2968d2d9') // Cognitive Services User
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: docIntelAccount
}

resource contentSafetyRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appServiceIdentity.id, contentSafetyAccount.id, 'CognitiveServicesUser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b6593-5c8b-4d1b-8e3b-123b2968d2d9') // Cognitive Services User
    principalId: appServiceIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
  scope: contentSafetyAccount
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
