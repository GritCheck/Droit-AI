@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the application.')
param appName string = 'droitai${uniqueString(resourceGroup().id)}'

@description('SKU for Static Web App.')
param staticWebAppSku string = 'Free'

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: '${appName}-frontend'
  location: location
  sku: {
    name: staticWebAppSku
  }
  properties: {
    repositoryUrl: '' // This will be set by azd
    branch: 'main'
    buildProperties: {
      appLocation: 'frontend'
      apiLocation: ''
      outputLocation: 'out'
      appBuildCommand: 'npm run build'
    }
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
  }
}

// Output for Frontend URL
output FRONTEND_URL string = staticWebApp.properties.defaultHostname
