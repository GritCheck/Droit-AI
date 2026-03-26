@description('Enables diagnostic settings for Azure services to send logs to Log Analytics for KQL queries')
param location string = resourceGroup().location
param appName string = 'droit-ai'
param environment string = 'dev'
@description('Use unique naming to avoid conflicts with soft-deleted resources')
param useUniqueNaming bool = true

// Parameters for existing resources
param azureOpenAiAccountName string
param azureSearchServiceName string
param azureStorageAccountName string

// Generate unique suffix only when needed
var uniqueSuffix = useUniqueNaming ? '-${uniqueString(resourceGroup().id)}' : ''

// 1. Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: 'droitai-logs-v3'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
  tags: {
    'azd-env-name': environment
    'azd-service-name': 'loganalytics'
  }
}

// 2. Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'droitai-insights-v3'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
  tags: {
    'azd-env-name': environment
    'azd-service-name': 'appinsights'
  }
}

// Reference existing services to apply diagnostics
resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: azureOpenAiAccountName
}

resource search 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: azureSearchServiceName
}

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: azureStorageAccountName
}

// 3. OpenAI Diagnostics (Crucial for Token Tracking)
resource openAiDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${appName}-openai-logs'
  scope: openAi
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      { category: 'Audit', enabled: true }
      { category: 'RequestResponse', enabled: true }
      { category: 'Trace', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// 4. AI Search Diagnostics (Crucial for Search Trends)
resource searchDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${appName}-search-logs'
  scope: search
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      { category: 'SearchQueryLog', enabled: true }
      { category: 'SearchIndexing', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// 5. Storage Blob Diagnostics (Crucial for Folder/Container sizes)
// Note: Storage diagnostics MUST target the 'blobServices/default' child resource
resource storageBlobDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${appName}-storage-logs'
  scope: storage
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      { category: 'StorageRead', enabled: true }
      { category: 'StorageWrite', enabled: true }
      { category: 'StorageDelete', enabled: true }
    ]
    metrics: [
      { category: 'Transaction', enabled: true }
    ]
  }
}

// Outputs for FastAPI / GovernedSearchService
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output logAnalyticsWorkspaceId string = logAnalytics.id
output logAnalyticsWorkspaceName string = logAnalytics.name
