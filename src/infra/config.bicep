// ====================================
// CENTRALIZED INFRASTRUCTURE CONFIG
// ====================================
// This file contains all configurable variables for the infrastructure
// deployment including regions, naming conventions, and resource settings.

@description('Primary Azure region for most resources')
param primaryLocation string = 'centralus'

@description('Azure region for AI Studio (must support AI Studio services)')
param aiStudioLocation string = 'eastus2'

@description('Environment suffix (dev/staging/prod)')
param environmentSuffix string = 'dev'

@description('Service principal object ID for role assignments')
param servicePrincipalObjectId string

@description('GitHub repository name for tagging')
param repositoryName string = 'TechWorkshop-L300-AI-Apps-and-agents'

@description('Deployment timestamp for tagging')
param deploymentTimestamp string = utcNow('yyyy-MM-dd')

// ====================================
// RESOURCE GROUP NAMING
// ====================================
var resourceGroupConfig = {
  primary: 'techworkshop-l300-ai-agents-${environmentSuffix}'
  aiStudio: 'azureai-${environmentSuffix}-rg'
}

// ====================================
// NAMING CONVENTION SETTINGS
// ====================================
var namingConfig = {
  // Base naming elements
  projectPrefix: 'zava'
  uniqueSuffix: uniqueString(resourceGroup().id, environmentSuffix)
  
  // Naming patterns (using Azure naming best practices)
  patterns: {
    storage: 'st{uniqueid}{env}'           // Storage accounts: max 24 chars, lowercase
    cosmosDb: '{uniqueid}-{env}-cosmosdb'  // Cosmos DB: descriptive naming
    webApp: '{uniqueid}-{env}-app'         // Web apps: environment separation
    registry: 'acr{uniqueid}{env}'         // Container registry: no hyphens
    aiServices: 'aif-{uniqueid}-{env}'     // AI services: descriptive prefix
    search: '{uniqueid}-{env}-search'      // Search services: clear purpose
    analytics: '{uniqueid}-{env}-la'       // Log Analytics: standard suffix
    insights: '{uniqueid}-{env}-ai'        // App Insights: standard suffix
    servicePlan: '{uniqueid}-{env}-asp'    // App Service Plan: standard suffix
  }
}

// ====================================
// COMPUTED RESOURCE NAMES
// ====================================
var resourceNames = {
  // Core infrastructure
  logAnalytics: '${namingConfig.uniqueSuffix}-${environmentSuffix}-la'
  appInsights: '${namingConfig.uniqueSuffix}-${environmentSuffix}-ai'
  
  // Data services
  cosmosDb: '${namingConfig.uniqueSuffix}-${environmentSuffix}-cosmosdb'
  cosmosDatabase: namingConfig.projectPrefix
  cosmosContainer: 'product_catalog'
  
  storageAccount: 'st${namingConfig.uniqueSuffix}${environmentSuffix}'
  storageContainer: namingConfig.projectPrefix
  
  // AI services  
  aiServices: 'aif-${namingConfig.uniqueSuffix}-${environmentSuffix}'
  aiSearch: '${namingConfig.uniqueSuffix}-${environmentSuffix}-search'
  aiSearchIndex: '${namingConfig.projectPrefix}-product-catalog'
  aiStudioHub: 'admin-${namingConfig.uniqueSuffix}-${aiStudioLocation}'
  aiStudioProject: 'admin-${namingConfig.uniqueSuffix}-${aiStudioLocation}_project'
  
  // Container & Web services
  containerRegistry: 'acr${namingConfig.uniqueSuffix}${environmentSuffix}'
  appServicePlan: '${namingConfig.uniqueSuffix}-${environmentSuffix}-asp'
  webApp: '${namingConfig.uniqueSuffix}-${environmentSuffix}-app'
  a2aWebApp: '${namingConfig.projectPrefix}-a2a-${environmentSuffix}-${namingConfig.uniqueSuffix}'
}

// ====================================
// ENVIRONMENT-SPECIFIC SETTINGS
// ====================================
var environmentSettings = {
  dev: {
    cosmosDb: {
      throughput: 400
      enableFreeTier: true
    }
    appServicePlan: {
      sku: 'F1'  // Free tier for development
      capacity: 1
    }
    aiServices: {
      sku: 'S0'  // Standard tier
    }
    aiSearch: {
      sku: 'free'  // Free tier for development
      capacity: 1
      replicas: 1
    }
  }
  staging: {
    cosmosDb: {
      throughput: 800
      enableFreeTier: false
    }
    appServicePlan: {
      sku: 'S1'  // Standard tier for staging
      capacity: 1
    }
    aiServices: {
      sku: 'S0'
    }
    aiSearch: {
      sku: 'basic'
      capacity: 1
      replicas: 1
    }
  }
  prod: {
    cosmosDb: {
      throughput: 1000
      enableFreeTier: false
    }
    appServicePlan: {
      sku: 'P1v3'  // Premium tier for production
      capacity: 2
    }
    aiServices: {
      sku: 'S0'
    }
    aiSearch: {
      sku: 'standard'
      capacity: 2
      replicas: 2
    }
  }
}

// ====================================
// COMMON RESOURCE TAGS
// ====================================
var resourceTags = {
  Environment: environmentSuffix
  Project: 'TechWorkshop-L300-AI-Agents'
  Repository: repositoryName
  ManagedBy: 'GitHubActions'
  CostCenter: 'Engineering'
  Owner: 'TechWorkshop-Team'
  CreatedDate: deploymentTimestamp
}

// ====================================
// SECURITY & COMPLIANCE SETTINGS
// ====================================
var securitySettings = {
  // Enable diagnostic logs for all resources
  enableDiagnostics: true
  
  // Network security settings
  network: {
    enablePrivateEndpoints: environmentSuffix == 'prod'
    allowedIpRanges: environmentSuffix == 'dev' ? ['*'] : [] // Restrict in non-dev
  }
  
  // Backup and retention settings
  backup: {
    cosmosDb: {
      backupIntervalInMinutes: environmentSuffix == 'prod' ? 60 : 240
      backupRetentionIntervalInHours: environmentSuffix == 'prod' ? 720 : 168
    }
  }
  
  // Key rotation settings
  keyRotation: {
    storageAccountKeys: environmentSuffix == 'prod' ? 90 : 365 // days
  }
}

// ====================================
// OUTPUTS
// ====================================
output locations object = {
  primary: primaryLocation
  aiStudio: aiStudioLocation
}

output resourceGroupNames object = resourceGroupConfig

output resourceNames object = resourceNames

output environmentConfig object = environmentSettings[environmentSuffix]

output commonTags object = resourceTags

output securitySettings object = securitySettings

output namingConventions object = namingConfig

// Export individual values for backward compatibility
output primaryLocation string = primaryLocation
output aiStudioLocation string = aiStudioLocation 
output environmentSuffix string = environmentSuffix
output servicePrincipalObjectId string = servicePrincipalObjectId
output repositoryName string = repositoryName
