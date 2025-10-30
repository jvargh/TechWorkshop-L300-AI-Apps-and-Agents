# Agentic DevOps Implementation - TechWorkshop L300

This repository implements automated CI/CD pipelines for both containerized applications and Azure AI Foundry agents using GitHub Actions.

## 🏗️ Architecture Overview

### Task 05_01: Container Deployment Automation
- **Workflow**: `.github/workflows/deploy-container.yml`
- **Triggers**: Push to `main` branch with changes in `src/` folder
- **Functionality**: 
  - Builds Docker image from `src/Dockerfile`
  - Pushes to Azure Container Registry (`acrowrgnenm7wj2y.azurecr.io`)
  - Updates Azure App Service (`zava-a2a-app`)
  - Handles environment variables securely via GitHub Secrets

### Task 05_02: AI Agent Deployment Automation
Four separate workflows for independent agent deployment:

1. **Customer Loyalty Agent** (`.github/workflows/deploy-customer-loyalty-agent.yml`)
   - Triggers: Changes to `customerLoyaltyAgent_initializer.py`, `CustomerLoyaltyAgentPrompt.txt`, or `discountLogic.py`
   - Tools: Discount calculation logic

2. **Inventory Agent** (`.github/workflows/deploy-inventory-agent.yml`)
   - Triggers: Changes to `inventoryAgent_initializer.py`, `InventoryAgentPrompt.txt`, or `inventoryCheck.py`
   - Tools: Inventory checking functionality

3. **Interior Design Agent** (`.github/workflows/deploy-interior-design-agent.yml`)
   - Triggers: Changes to `interiorDesignAgent_initializer.py`, `InteriorDesignAgentPrompt.txt`, or `imageCreationTool.py`
   - Tools: AI image generation for interior design

4. **Cora Shopping Agent** (`.github/workflows/deploy-cora-agent.yml`)
   - Triggers: Changes to `shopperAgent_initializer.py` or `ShopperAgentPrompt.txt`
   - Tools: Core shopping assistant functionality

## 🔐 Security Implementation

### Service Principals
- **Container Deployment**: `TechWorkshopL300Container` (Contributor role)
- **AI Agent Management**: `TechWorkshopL300AzureAI` (Contributor + Azure AI User roles)

### GitHub Secrets Configuration
See `GITHUB_SECRETS_GUIDE.md` for complete list of required secrets.

Key secrets include:
- `AZURE_CREDENTIALS` - Service principal authentication
- Azure AI Foundry endpoints and keys
- Agent IDs and model deployment configurations
- Storage, Search, and Cosmos DB credentials

## 🤖 Agent Initializer Updates

All agent initializers have been updated to support CI/CD with **upsert pattern**:

```python
# Check if agent already exists
existing_agent = None
agents_list = project_client.agents.list_agents()
for agent in agents_list:
    if agent.name == agent_name:
        existing_agent = agent
        break

if existing_agent:
    # Update existing agent
    agent = project_client.agents.update_agent(...)
else:
    # Create new agent
    agent = project_client.agents.create_agent(...)
```

This prevents duplicate agent creation during automated deployments.

## 🚀 Deployment Process

### Container Deployment
1. Developer pushes code changes to `main` branch
2. GitHub Actions detects changes in `src/` folder
3. Workflow builds Docker image with commit SHA tag
4. Image pushed to Azure Container Registry
5. Azure App Service updated with new image
6. Health check verifies successful deployment

### Agent Deployment
1. Developer modifies agent prompt, initializer, or tool files
2. Relevant workflow triggers based on file paths
3. Python environment set up with required dependencies
4. Environment variables configured from GitHub Secrets
5. Agent initializer executed (creates or updates agent)
6. Deployment verified and logged

## 📊 Observability Integration

The deployed applications include comprehensive observability:
- **Azure Monitor**: Application performance monitoring
- **OpenTelemetry**: Distributed tracing across agents
- **Application Insights**: Real-time metrics and logs
- **Custom Spans**: Agent initialization, message processing, tool execution

## 🔧 Setup Instructions

### 1. Create Service Principals
```bash
# For container deployment
az ad sp create-for-rbac --name "TechWorkshopL300Container" --json-auth --role contributor --scopes /subscriptions/{SUB_ID}/resourceGroups/{RG}

# For agent management
az ad sp create-for-rbac --name "TechWorkshopL300AzureAI" --json-auth --role contributor --scopes /subscriptions/{SUB_ID}/resourceGroups/{RG}
```

### 2. Grant AI Foundry Access
```bash
az role assignment create --assignee "{SERVICE_PRINCIPAL_ID}" --role "Azure AI User" --scope "/subscriptions/{SUB_ID}/resourceGroups/{RG}/providers/Microsoft.CognitiveServices/accounts/{AI_FOUNDRY_NAME}"
```

### 3. Configure GitHub Secrets
Use the provided `setup-github-secrets.sh` script or manually configure secrets in GitHub repository settings.

### 4. Test Deployments
- **Container**: Push changes to `src/` folder
- **Agents**: Modify any prompt or initializer file
- Monitor progress in GitHub Actions tab

## 📁 File Structure

```
.github/workflows/
├── deploy-container.yml              # Container deployment
├── deploy-customer-loyalty-agent.yml # Customer loyalty agent
├── deploy-inventory-agent.yml        # Inventory agent  
├── deploy-interior-design-agent.yml  # Interior design agent
└── deploy-cora-agent.yml            # Cora shopping agent

src/app/agents/
├── customerLoyaltyAgent_initializer.py  # Updated for CI/CD
├── inventoryAgent_initializer.py        # Updated for CI/CD
├── interiorDesignAgent_initializer.py   # Updated for CI/CD
└── shopperAgent_initializer.py         # Updated for CI/CD

GITHUB_SECRETS_GUIDE.md               # Security configuration guide
setup-github-secrets.sh               # Automated secret setup
```

## 🎯 Success Criteria

✅ **Task 05_01 Completed**:
- GitHub Actions workflow automates container deployment
- Environment variables handled securely via secrets
- Azure App Service updates automatically on code changes

✅ **Task 05_02 Completed**:
- Agent initializers support upsert pattern (create/update)
- Service principal configured with proper Azure AI Foundry access
- Individual workflows for each agent with appropriate triggers
- Automated agent deployment on prompt/tool changes

## 🔗 Deployed Services

- **A2A Application**: https://zava-a2a-app.azurewebsites.net/
- **Health Check**: https://zava-a2a-app.azurewebsites.net/health
- **Container Registry**: acrowrgnenm7wj2y.azurecr.io/zava-a2a-app:latest

## 📋 Next Steps

1. Test container deployment by modifying files in `src/`
2. Test agent deployment by updating prompt files
3. Monitor GitHub Actions for successful executions
4. Verify agents are updated in Azure AI Foundry portal
5. Validate observability data in Application Insights