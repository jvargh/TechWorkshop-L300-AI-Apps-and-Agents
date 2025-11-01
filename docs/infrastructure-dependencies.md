# Infrastructure Dependencies Analysis

## Current Infrastructure Components

### Resource Groups
1. **techworkshop-l300-ai-agents-centralus** (Primary)
   - Location: Central US
   - Contains: Core application infrastructure
   
2. **azureai-rg** (AI Studio)
   - Location: East US 2  
   - Contains: AI Studio project and cognitive services

### Core Resources in techworkshop-l300-ai-agents-centralus

| Resource Name | Type | Purpose | Dependencies |
|---------------|------|---------|--------------|
| `owrgnenm7wj2y-cosu-la` | Log Analytics Workspace | Monitoring & logging | None |
| `owrgnenm7wj2y-search` | AI Search Service | Product catalog search | None |
| `aif-owrgnenm7wj2y` | Cognitive Services (AI Services) | OpenAI endpoints | None |
| `acrowrgnenm7wj2y` | Container Registry | Docker image storage | None |
| `owrgnenm7wj2y-cosmosdb` | Cosmos DB Account | Product data storage | None |
| `stowrgnenm7wj2y` | Storage Account | Blob storage for files | None |
| `owrgnenm7wj2y-cosu-asp` | App Service Plan | Web app hosting | None |
| `owrgnenm7wj2y-cosu-ai` | Application Insights | Application monitoring | Log Analytics |
| `owrgnenm7wj2y-app` | Web App (Legacy) | Original web app | App Service Plan, App Insights |
| `zava-a2a-app` | Web App (A2A) | Agent-to-Agent app | App Service Plan, Container Registry |

### AI Studio Resources in azureai-rg

| Resource Name | Type | Purpose | Dependencies |
|---------------|------|---------|--------------|
| `admin-mh2k31bc-eastus2` | Cognitive Services Account | AI Studio Hub | None |
| `admin-mh2k31bc-eastus2_project` | AI Studio Project | Agent deployment | AI Studio Hub |

### Service Principal & Permissions

#### Required Roles for Service Principal:
1. **Subscription Level:**
   - `Contributor` - Resource creation/management
   
2. **Resource Group Level (techworkshop-l300-ai-agents-centralus):**
   - `Owner` or `Contributor` - Full resource management
   
3. **Resource Group Level (azureai-rg):**
   - `Cognitive Services OpenAI Contributor` - AI Studio access
   - `Data Contributor` - Agent management
   
4. **Specific Resource Permissions:**
   - Container Registry: `AcrPush`, `AcrPull` 
   - Storage Account: `Storage Blob Data Contributor`
   - Cosmos DB: `DocumentDB Account Contributor`
   - AI Search: `Search Service Contributor`

### GitHub Secrets Required

#### Azure Authentication
- `AZURE_CREDENTIALS` - Service principal credentials JSON
- `AZURE_SUBSCRIPTION_ID` - Subscription ID
- `AZURE_TENANT_ID` - Tenant ID  
- `AZURE_CLIENT_ID` - Service principal client ID

#### Resource Names & Endpoints
- `AZURE_RESOURCE_GROUP` - Primary resource group name
- `AZURE_AI_AGENT_ENDPOINT` - AI Studio project endpoint
- `AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME` - Model deployment name
- `AZURE_AI_AGENT_API_VERSION` - API version
- `AZURE_CONTAINER_REGISTRY` - ACR name
- `AZURE_APP_SERVICE_NAME` - App service name

#### Service Credentials (Auto-generated)
- `AZURE_OPENAI_ENDPOINT` - OpenAI service endpoint
- `AZURE_OPENAI_KEY` - OpenAI API key  
- `COSMOS_ENDPOINT` - Cosmos DB endpoint
- `COSMOS_KEY` - Cosmos DB primary key
- `BLOB_CONNECTION_STRING` - Storage connection string
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - App Insights connection
- `SEARCH_ENDPOINT` - AI Search endpoint
- `SEARCH_KEY` - AI Search admin key

#### Agent IDs (Auto-updated by workflows)
- `CORA_AGENT_ID` - Cora shopping agent ID
- `INTERIOR_DESIGNER_AGENT_ID` - Interior design agent ID
- `INVENTORY_AGENT_ID` - Inventory agent ID  
- `CUSTOMER_LOYALTY_AGENT_ID` - Customer loyalty agent ID

### Deployment Dependencies & Order

1. **Foundation Layer**
   - Resource Groups
   - Log Analytics Workspace
   
2. **Storage & Data Layer**
   - Storage Account
   - Cosmos DB Account
   - Container Registry
   
3. **AI Services Layer**  
   - Cognitive Services (AI Services)
   - AI Search Service
   - AI Studio Hub (separate RG)
   - AI Studio Project
   
4. **Application Layer**
   - Application Insights
   - App Service Plan
   - Web Applications
   
5. **Configuration Layer**
   - Role assignments
   - GitHub secrets update
   
6. **Agent Deployment**
   - Deploy AI agents to AI Studio
   - Update agent IDs in secrets

### Critical Configuration Notes

1. **AI Studio Project Endpoint Format:**
   ```
   https://{hub-name}.services.ai.azure.com/api/projects/{project-name}
   ```

2. **Required Model Deployments:**
   - `gpt-4.1` - Primary chat model
   - `gpt-4o-mini` - Backup model
   - `Phi-4` - Alternative model

3. **Container Image Naming:**
   - Registry: `{uniqueString}-acr.azurecr.io`
   - Image: `zava-a2a-app:latest`

4. **Database Configuration:**
   - Cosmos DB Database: `zava`
   - Container: `product_catalog`
   - Search Index: `zava-product-catalog`