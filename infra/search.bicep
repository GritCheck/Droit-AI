@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name for naming resources')
param appName string

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
    azdEnvName: 'dev'
    purpose: 'DroitAI Search Service'
  }
}

// Azure AI Search Index: Tuned for CUAD Legal Audit
resource searchIndex 'Microsoft.Search/searchServices/indexes@2023-11-01' = {
  name: '${appName}-search-index'
  parent: searchAccount
  properties: {
    fields: [
      {
        name: 'id'
        type: 'Edm.String'
        key: true
        filterable: true
        retrievable: true
      }
      {
        name: 'content'
        type: 'Edm.String'
        searchable: true
        retrievable: true
        analyzer: 'en.microsoft' // Better for legal terminology
      }
      {
        name: 'content_vector'
        type: 'Collection(Edm.Single)'
        searchable: true
        retrievable: false
        dimensions: 1536 // Matching text-embedding-3-small/ada-002
        vectorSearchProfile: 'vector-profile'
      }
      // --- CUAD STRATEGY FIELDS ---
      {
        name: 'clause_type'
        type: 'Edm.String'
        filterable: true
        searchable: true
        facetable: true // Allows frontend sidebar filtering by the 41 CUAD types
        retrievable: true
      }
      {
        name: 'is_red_flag'
        type: 'Edm.Boolean'
        filterable: true
        retrievable: true
      }
      {
        name: 'document_name'
        type: 'Edm.String'
        searchable: true
        filterable: true
        retrievable: true
      }
      {
        name: 'page_number'
        type: 'Edm.Int32'
        filterable: true
        retrievable: true
      }
    ]
    vectorSearch: {
      algorithms: [
        {
          name: 'hnsw-config'
          kind: 'hnsw'
        }
      ]
      profiles: [
        {
          name: 'vector-profile'
          algorithm: 'hnsw-config'
        }
      ]
    }
    semanticSearch: {
      configurations: [
        {
          name: 'legal-semantic-config'
          prioritizedFields: {
            titleField: {
              fieldName: 'document_name'
            }
            contentFields: [
              {
                fieldName: 'content'
              }
            ]
            keywordFields: [
              {
                fieldName: 'clause_type' // Prioritize CUAD labels in semantic reranking
              }
            ]
          }
        }
      ]
      defaultConfiguration: 'legal-semantic-config'
    }
  }
}

// Outputs
output searchServiceName string = searchAccount.name
output searchServiceId string = searchAccount.id
output searchServiceEndpoint string = 'https://${searchAccount.name}.search.windows.net/'
output searchServiceKey string = listKeys(searchAccount.id, searchAccount.apiVersion).primaryKey
output searchIndexName string = searchIndex.name
