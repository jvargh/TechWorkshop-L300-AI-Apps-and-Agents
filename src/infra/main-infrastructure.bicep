@minLength(1)
@description('Primary location for all resources.')
param location string = 'centralus'

@description('AI Studio location (must support AI Studio)')
param aiStudioLocation string = 'eastus2'

@description('Environment suffix for resource naming')
param environmentSuffix string = 'dev'

@description('Service principal object ID for role assignments')
param servicePrincipalObjectId string

@description('GitHub repository name for tagging')
param repositoryName string = 'TechWorkshop-L300-AI-Apps-and-agents'

@description('Deployment timestamp for tagging')
param deploymentTimestamp string = utcNow('yyyy-MM-dd')

// Generate unique suffix for resource names
var uniqueSuffix = uniqueString(resourceGroup().id, environmentSuffix)
var projectPrefix = 'zava'

// ====================================
// CENTRALIZED RESOURCE NAMING
// ====================================
var resourceNames = {
  // Core infrastructure
  logAnalytics: '${uniqueSuffix}-${environmentSuffix}-la'
  appInsights: '${uniqueSuffix}-${environmentSuffix}-ai'
  
  // Data services  
  cosmosDb: '${uniqueSuffix}-${environmentSuffix}-cosmosdb'
  cosmosDatabase: projectPrefix
  cosmosContainer: 'product_catalog'
  
  storageAccount: 'st${uniqueSuffix}${environmentSuffix}'
  storageContainer: projectPrefix
  
  // AI services
  aiServices: 'aif-${uniqueSuffix}-${environmentSuffix}'
  aiSearch: '${uniqueSuffix}-${environmentSuffix}-search'
  aiSearchIndex: '${projectPrefix}-product-catalog'
  
  // Container & Web
  containerRegistry: 'acr${uniqueSuffix}${environmentSuffix}'
  appServicePlan: '${uniqueSuffix}-${environmentSuffix}-asp'
  webApp: '${uniqueSuffix}-${environmentSuffix}-app'
  a2aWebApp: '${projectPrefix}-a2a-${environmentSuffix}-${uniqueSuffix}'
}

// ====================================
// CENTRALIZED RESOURCE TAGS
// ====================================
var commonTags = {
  Environment: environmentSuffix
  Project: 'TechWorkshop-L300-AI-Agents'
  Repository: repositoryName
  ManagedBy: 'GitHubActions'
  CostCenter: 'Engineering'
  Owner: 'TechWorkshop-Team'
  CreatedDate: deploymentTimestamp
}

//==============================================================================
// FOUNDATION LAYER - Monitoring & Logging
//==============================================================================

@description('Creates Azure Log Analytics workspace for monitoring.')
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: resourceNames.logAnalytics
  location: location
  tags: commonTags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 90
    workspaceCapping: {
      dailyQuotaGb: 10
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

@description('Creates Azure Application Insights for application monitoring.')
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: resourceNames.appInsights
  location: location
  tags: commonTags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    RetentionInDays: 90
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

//==============================================================================
// DATA LAYER - Storage & Database
//==============================================================================

@description('Creates Azure Storage account for file storage.')
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: resourceNames.storageAccount
  location: location
  tags: commonTags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    publicNetworkAccess: 'Enabled'
  }
}

@description('Creates blob container for Zava data.')
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/${resourceNames.storageContainer}'
  properties: {
    publicAccess: 'None'
  }
}

@description('Creates Azure Cosmos DB account for product data.')
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: resourceNames.cosmosDb
  location: location
  tags: commonTags
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

@description('Creates Cosmos DB database for Zava.')
resource cosmosDbDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDbAccount
  name: resourceNames.cosmosDatabase
  properties: {
    resource: {
      id: resourceNames.cosmosDatabase
    }
    options: {
      throughput: 400
    }
  }
}

@description('Creates Cosmos DB container for product catalog.')
resource cosmosDbContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: resourceNames.cosmosContainer
  properties: {
    resource: {
      id: resourceNames.cosmosContainer
      partitionKey: {
        paths: ['/category']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
    options: {
      throughput: 400
    }
  }
}

//==============================================================================
// AI SERVICES LAYER - Cognitive Services & Search
//==============================================================================

@description('Creates Azure AI Services (OpenAI) account.')
resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: resourceNames.aiServices
  location: location
  tags: commonTags
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: resourceNames.aiServices
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

@description('Creates Azure AI Search service for product search.')
resource aiSearchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: resourceNames.aiSearch
  location: location
  tags: commonTags
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'enabled'
  }
}

//==============================================================================
// CONTAINER LAYER - Registry & Hosting
//==============================================================================

@description('Creates Azure Container Registry for Docker images.')
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: resourceNames.containerRegistry
  location: location
  tags: commonTags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
    policies: {
      retentionPolicy: {
        days: 30
        status: 'enabled'
      }
    }
  }
}

@description('Creates Azure App Service Plan for web hosting.')
resource appServicePlan 'Microsoft.Web/serverFarms@2023-01-01' = {
  name: resourceNames.appServicePlan
  location: location
  tags: commonTags
  sku: {
    name: 'B2'
    tier: 'Basic'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

@description('Creates Azure Web App for legacy application.')
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: resourceNames.webApp
  location: location
  tags: commonTags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistry.name}.azurecr.io/zava-app:latest'
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      acrUseManagedIdentityCreds: true
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistry.name}.azurecr.io'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
  }
}

@description('Creates Azure Web App for A2A (Agent-to-Agent) application.')
resource a2aWebApp 'Microsoft.Web/sites@2023-01-01' = {
  name: resourceNames.a2aWebApp
  location: location
  tags: commonTags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistry.name}.azurecr.io/zava-a2a-app:latest'
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      acrUseManagedIdentityCreds: true
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistry.name}.azurecr.io'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
  }
}

//==============================================================================
// RBAC & PERMISSIONS
//==============================================================================

// Storage Blob Data Contributor role for service principal
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, servicePrincipalObjectId, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// Cosmos DB Account Contributor role for service principal  
resource cosmosRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: cosmosDbAccount
  name: guid(cosmosDbAccount.id, servicePrincipalObjectId, '5bd9cd88-fe45-4216-938b-f97437e15450')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5bd9cd88-fe45-4216-938b-f97437e15450') // DocumentDB Account Contributor
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// Search Service Contributor role for service principal
resource searchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiSearchService
  name: guid(aiSearchService.id, servicePrincipalObjectId, '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0') // Search Service Contributor
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// AcrPush role for service principal
resource acrPushRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, servicePrincipalObjectId, '8311e382-0749-4cb8-b61a-304f252e45ec')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4cb8-b61a-304f252e45ec') // AcrPush
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// AcrPull role for main web app managed identity
resource webAppAcrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, webApp.name, 'acrpull-webapp')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    webApp
  ]
}

// AcrPull role for A2A web app managed identity  
resource a2aWebAppAcrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, a2aWebApp.name, 'acrpull-a2a')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: a2aWebApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    a2aWebApp
  ]
}

//==============================================================================
// OUTPUTS - Values for GitHub Secrets & Configuration
//==============================================================================

@description('Primary resource group name')
output resourceGroupName string = resourceGroup().name

@description('Primary deployment location')
output location string = location

@description('AI Studio deployment location')
output aiStudioLocation string = aiStudioLocation

// Storage outputs
@description('Storage account name')
output storageAccountName string = storageAccount.name

@description('Storage account connection string')
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'

@description('Blob container name')
output blobContainerName string = resourceNames.storageContainer

// Cosmos DB outputs
@description('Cosmos DB endpoint')
output cosmosEndpoint string = cosmosDbAccount.properties.documentEndpoint

@description('Cosmos DB primary key')
output cosmosKey string = cosmosDbAccount.listKeys().primaryMasterKey

@description('Cosmos DB database name')
output cosmosDatabaseName string = resourceNames.cosmosDatabase

@description('Cosmos DB container name')
output cosmosContainerName string = resourceNames.cosmosContainer

// AI Search outputs
@description('AI Search endpoint')
output searchEndpoint string = 'https://${aiSearchService.name}.search.windows.net'

@description('AI Search admin key')
output searchKey string = aiSearchService.listAdminKeys().primaryKey

@description('AI Search index name')
output searchIndexName string = resourceNames.aiSearchIndex

// AI Services outputs
@description('Azure OpenAI endpoint')
output openAiEndpoint string = aiServices.properties.endpoint

@description('Azure OpenAI key')
output openAiKey string = aiServices.listKeys().key1

// Container Registry outputs
@description('Container Registry name')
output containerRegistryName string = containerRegistry.name

@description('Container Registry login server')
output containerRegistryLoginServer string = containerRegistry.properties.loginServer

// Application Insights outputs
@description('Application Insights connection string')
output appInsightsConnectionString string = appInsights.properties.ConnectionString

@description('Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey

// Web App outputs
@description('Primary web app name')
output webAppName string = webApp.name

@description('Primary web app URL')
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'

@description('A2A web app name')
output a2aWebAppName string = a2aWebApp.name

@description('A2A web app URL')
output a2aWebAppUrl string = 'https://${a2aWebApp.properties.defaultHostName}'

// Resource naming for reference
@description('Resource naming convention used')
output resourceNaming object = resourceNames

@description('Common tags applied to resources')
output commonTags object = commonTags
