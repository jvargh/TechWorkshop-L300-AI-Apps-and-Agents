@description('Location for AI Studio resources (must support AI Studio)')
param location string = 'eastus2'

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

// ====================================
// CENTRALIZED AI STUDIO NAMING
// ====================================
var aiStudioHubName = 'admin-${uniqueSuffix}-${location}'
var aiStudioProjectName = '${aiStudioHubName}_project'

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
  Component: 'AIStudio'
}

//==============================================================================
// AI STUDIO HUB & PROJECT
//==============================================================================

@description('Creates Azure AI Studio Hub (Cognitive Services Account)')
resource aiStudioHub 'Microsoft.CognitiveServices/accounts@2025-09-01' = {
  name: aiStudioHubName
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
    customSubDomainName: aiStudioHubName
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

// NOTE: AI Studio Project creation is handled separately
// Projects can be created via Azure AI Studio portal or REST API after hub deployment
// Commented out due to API version compatibility issues with Bicep deployment
/*
@description('Creates Azure AI Studio Project')
resource aiStudioProject 'Microsoft.CognitiveServices/accounts/projects@2025-09-01' = {
  parent: aiStudioHub
  name: aiStudioProjectName
  location: location
  tags: commonTags
  properties: {
    // Project-specific properties
  }
}
*/

//==============================================================================
// RBAC & PERMISSIONS FOR AI STUDIO
//==============================================================================

// Cognitive Services OpenAI Contributor role for service principal
resource cognitiveServicesContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiStudioHub
  name: guid(aiStudioHub.id, servicePrincipalObjectId, 'a001fd3d-188f-4b5d-821b-7da978bf7442')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a001fd3d-188f-4b5d-821b-7da978bf7442') // Cognitive Services OpenAI Contributor
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// Cognitive Services Contributor role for service principal (broader access)
resource cognitiveServicesGeneralRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiStudioHub  
  name: guid(aiStudioHub.id, servicePrincipalObjectId, '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68') // Cognitive Services Contributor
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

// AI Developer role for service principal (comprehensive AI Studio access)
resource aiDeveloperRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiStudioHub
  name: guid(aiStudioHub.id, servicePrincipalObjectId, '64702f94-c441-49e6-a78b-ef80e0188fee')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '64702f94-c441-49e6-a78b-ef80e0188fee') // AI Developer
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

//==============================================================================
// OUTPUTS - AI Studio Configuration
//==============================================================================

@description('AI Studio Hub name')
output aiStudioHubName string = aiStudioHub.name

@description('AI Studio Project name - will be created separately') 
output aiStudioProjectName string = aiStudioProjectName

@description('AI Studio Hub endpoint')
output aiStudioHubEndpoint string = aiStudioHub.properties.endpoint

@description('AI Studio Project endpoint - placeholder for manual project creation')
output aiStudioProjectEndpoint string = '${aiStudioHub.properties.endpoint}api/projects/${aiStudioProjectName}'

@description('AI Studio Hub resource ID')
output aiStudioHubResourceId string = aiStudioHub.id

@description('AI Studio Project resource ID - placeholder for manual project creation')
output aiStudioProjectResourceId string = 'Manual_Creation_Required'

@description('Location where AI Studio is deployed')
output aiStudioLocation string = location
