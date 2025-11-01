# Infrastructure Deployment Setup Guide

This guide provides step-by-step instructions for setting up GitHub Actions to deploy the complete infrastructure for the Tech Workshop L300 AI Apps and Agents project.

## 🎯 Overview

The deployment workflow automates:
- ✅ Complete infrastructure provisioning via Bicep templates
- ✅ Resource group lifecycle management (create/delete/recreate)
- ✅ Service authentication and RBAC configuration
- ✅ Sample data deployment (Cosmos DB + AI Search)
- ✅ GitHub secrets management automation
- ✅ Multi-environment support (dev/staging/prod)

## 🔐 Prerequisites - GitHub Secrets Setup

### Required Initial Secrets

Before running the workflow, you need to set up these GitHub secrets manually:

```
# Core Azure Authentication
AZURE_CREDENTIALS       # Service Principal JSON credentials
AZURE_CLIENT_ID         # Service Principal Application ID
GITHUB_TOKEN           # GitHub Personal Access Token (for updating secrets)
```

### 1. Create Azure Service Principal

**For PowerShell (Windows):**
```powershell
# Login to Azure
az login

# Set your subscription (replace with your subscription ID)
az account set --subscription "your-subscription-id"

# Create service principal with Owner role (required for RBAC assignments)
az ad sp create-for-rbac `
  --name "github-actions-techworkshop-l300" `
  --role "Owner" `
  --scopes "/subscriptions/your-subscription-id" `
  --sdk-auth
```

**For Bash (Linux/macOS):**
```bash
# Login to Azure
az login

# Set your subscription (replace with your subscription ID)
az account set --subscription "your-subscription-id"

# Create service principal with Owner role (required for RBAC assignments)
az ad sp create-for-rbac \
  --name "github-actions-techworkshop-l300" \
  --role "Owner" \
  --scopes "/subscriptions/your-subscription-id" \
  --sdk-auth
```

**Copy the entire JSON output** - this goes into `AZURE_CREDENTIALS` secret.

Example output:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### 2. Set GitHub Secrets

#### Option A: Using GitHub CLI

**For PowerShell (Windows):**
```powershell
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Navigate to your repository directory
Set-Location "C:\path\to\TechWorkshop-L300-AI-Apps-and-agents-main"

# Set the secrets
gh secret set AZURE_CREDENTIALS --body "paste-entire-json-from-step-1"
gh secret set AZURE_CLIENT_ID --body "clientId-from-json-above" 
gh secret set GITHUB_TOKEN --body "your-github-personal-access-token"
```

**For Bash (Linux/macOS):**
```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Navigate to your repository directory
cd path/to/TechWorkshop-L300-AI-Apps-and-agents-main

# Set the secrets
gh secret set AZURE_CREDENTIALS --body "paste-entire-json-from-step-1"
gh secret set AZURE_CLIENT_ID --body "clientId-from-json-above"
gh secret set GITHUB_TOKEN --body "your-github-personal-access-token"
```

#### Option B: Using GitHub Web Interface
1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each:
   - **Name**: `AZURE_CREDENTIALS`, **Value**: Entire JSON from service principal creation
   - **Name**: `AZURE_CLIENT_ID`, **Value**: The `clientId` value from the JSON
   - **Name**: `GITHUB_TOKEN`, **Value**: Your GitHub Personal Access Token

### 3. Create GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Set expiration and select these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `admin:repo_hook` (Admin access to repository hooks)
4. Copy the token and use it for `GITHUB_TOKEN` secret

## 🚀 Automated Setup Scripts

We provide automated setup scripts to streamline the secret configuration process:

### PowerShell Script (Windows/Cross-platform)
```powershell
# Run the PowerShell setup script
.\scripts\setup-github-secrets.ps1 -SubscriptionId "your-subscription-id"
```

### Bash Script (Linux/macOS/WSL)
```bash
# Make the script executable
chmod +x scripts/setup-github-secrets.sh

# Run the bash setup script
./scripts/setup-github-secrets.sh --subscription-id "your-subscription-id"
```

Both scripts will:
- ✅ Validate prerequisites (Azure CLI, GitHub CLI)
- ✅ Create or configure the service principal
- ✅ Set all required GitHub secrets automatically
- ✅ Provide detailed feedback and error handling

## 🚀 Deployment Workflow Usage

### Manual Deployment via GitHub Actions

1. **Navigate to Actions tab** in your GitHub repository
2. **Select "Deploy Complete Infrastructure"** workflow
3. **Click "Run workflow"** and configure:

**Parameters:**
- **Environment**: Choose `dev`, `staging`, or `prod`
- **Destroy existing resources first**: ✅ Check for clean deployment
- **Deploy sample data**: ✅ Check to load product catalog and search index

### Deployment Options

#### 🆕 Clean Deployment (Recommended)
```
Environment: dev
Destroy existing resources first: ✅ true
Deploy sample data: ✅ true
```
- Deletes all existing resources
- Creates fresh infrastructure
- Loads sample data

#### 📊 Infrastructure Only
```
Environment: dev  
Destroy existing resources first: ✅ true
Deploy sample data: ❌ false
```
- Deploys infrastructure only
- No sample data loading

#### 🔄 Update Deployment
```
Environment: dev
Destroy existing resources first: ❌ false
Deploy sample data: ❌ false  
```
- Updates existing resources
- Preserves data

## 🏗️ Infrastructure Components

### Primary Resource Group (`techworkshop-l300-ai-agents-{env}`)
- **Log Analytics Workspace**: Centralized logging and monitoring
- **Storage Account**: Blob storage for assets and data
- **Cosmos DB**: NoSQL database for product catalog
- **AI Search Service**: Vector and full-text search capabilities
- **AI Services**: OpenAI GPT models and embedding services
- **Application Insights**: Application performance monitoring
- **Container Registry**: Docker image storage
- **App Service Plan**: Hosting platform for web applications
- **Web Apps (2)**: Main chat application and A2A (Agent-to-Agent) app

### AI Studio Resource Group (`azureai-{env}-rg`)
- **AI Studio Hub**: Central hub for AI development
- **AI Studio Project**: Specific project workspace for agents

### Role Assignments
- **AI Developer Role**: Full AI Studio access for service principal
- **Cognitive Services Contributor**: AI services management
- **Storage Blob Data Contributor**: Storage access for applications

## 📋 Post-Deployment

### Automatic Secret Updates
The workflow automatically updates these GitHub secrets with deployment outputs:
- `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_REGISTRY`, `AZURE_APP_SERVICE_NAME`
- `STORAGE_ACCOUNT_NAME`, `COSMOS_ENDPOINT`, `COSMOS_KEY`
- `SEARCH_ENDPOINT`, `SEARCH_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`
- `AZURE_AI_AGENT_ENDPOINT`, `GPT_ENDPOINT`, `GPT_API_KEY`
- `APPLICATIONINSIGHTS_CONNECTION_STRING`, `BLOB_CONNECTION_STRING`

### Manual Verification Steps

1. **Check Resource Groups:**
   ```bash
   # Cross-platform command
   az group list --query "[?contains(name, 'techworkshop-l300') || contains(name, 'azureai')].{Name:name, Location:location, State:properties.provisioningState}"
   ```

2. **Verify AI Studio Setup:**
   ```bash
   # Cross-platform command
   az cognitiveservices account list --resource-group azureai-dev-rg
   ```

3. **Test Cosmos DB Data:**
   ```bash
   # Cross-platform command - Install cosmicworks CLI or use Azure portal
   # Check database: zava, container: product_catalog
   ```

4. **Test AI Search Index:**
   ```bash
   # Cross-platform command - Check index: zava-product-catalog in Azure portal
   ```

## 🔧 Troubleshooting

### Common Issues

**1. Service Principal Permissions**
```bash
# Error: Insufficient privileges to complete the operation
# Solution: Ensure service principal has Owner role on subscription
az role assignment create --assignee "your-client-id" --role "Owner" --scope "/subscriptions/your-subscription-id"
```

**2. Resource Name Conflicts**
```
# Error: Resource name already exists
# Solution: Use destroy_first option or change environment suffix
```

**3. GitHub Secrets Access**
```
# Error: Context access might be invalid
# Solution: Ensure all required secrets are set in repository settings
```

**4. Quota Limitations**
```bash
# Error: Quota exceeded for resource type
# Solution: Check Azure quotas and request increases if needed
az vm list-usage --location centralus --output table
```

### Debug Commands

**Check deployment status:**
```bash
az deployment group list --resource-group techworkshop-l300-ai-agents-dev --output table
```

**View deployment logs:**
```bash
az deployment operation group list --resource-group techworkshop-l300-ai-agents-dev --name main-infrastructure
```

**Test service connectivity:**
```bash
# Test Cosmos DB
az cosmosdb sql database list --account-name your-cosmos-account --resource-group your-rg

# Test AI Search  
az search service show --name your-search-service --resource-group your-rg

# Test OpenAI
az cognitiveservices account show --name your-openai-service --resource-group your-rg
```

## 🔄 Environment Management

### Creating New Environments

1. Run workflow with new environment name (e.g., `staging`, `prod`)
2. Resources will be created with environment-specific naming
3. Separate resource groups ensure isolation

### Switching Environments

Update workflow parameters to target different environments. Each environment maintains:
- Separate Azure resource groups
- Environment-specific GitHub secrets (auto-managed)
- Isolated data and configurations

### Clean Up

To remove an environment completely:
1. Run workflow with `destroy_first: true` and `deploy_sample_data: false`
2. Cancel workflow after destruction phase
3. Resource groups will be fully deleted

## 🎯 Next Steps

After successful infrastructure deployment:

1. **Deploy AI Agents**: Use existing agent deployment workflows
2. **Build Applications**: Deploy containerized chat and A2A applications  
3. **Configure Monitoring**: Set up alerts and dashboards in Application Insights
4. **Security Review**: Validate RBAC assignments and network configurations

## 📚 Additional Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [GitHub Actions for Azure](https://docs.microsoft.com/en-us/azure/developer/github/github-actions)
- [Azure AI Studio Documentation](https://docs.microsoft.com/en-us/azure/ai-studio/)
- [Azure Role-Based Access Control](https://docs.microsoft.com/en-us/azure/role-based-access-control/)