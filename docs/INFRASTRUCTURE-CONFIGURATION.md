# Infrastructure Configuration Management

This document describes the centralized configuration system for the TechWorkshop L300 AI Agents infrastructure deployment.

## 📁 Configuration Structure

```
src/infra/
├── config/
│   └── infrastructure-variables.yml    # ⭐ Master configuration file
├── parameters/
│   ├── dev.parameters.json            # Development environment parameters
│   ├── staging.parameters.json        # Staging environment parameters  
│   └── prod.parameters.json           # Production environment parameters
├── main-infrastructure.bicep          # Main infrastructure template
├── ai-studio.bicep                    # AI Studio infrastructure template
└── config.bicep                       # Shared configuration module (optional)
```

## 🎯 Centralized Configuration Benefits

### ✅ **What We Achieved**:
1. **Single Source of Truth**: All regions, naming conventions, and settings in one file
2. **Environment Separation**: Clean parameter files per environment (dev/staging/prod)  
3. **Consistent Naming**: Centralized naming patterns following Azure best practices
4. **Easy Maintenance**: Update configurations without editing multiple templates
5. **Better Documentation**: Self-documenting configuration with comprehensive comments

### 🔧 **Configuration Files Overview**:

#### 1. **Master Configuration** (`infrastructure-variables.yml`)
```yaml
# Central configuration for all environments
locations:
  primary: "centralus" 
  ai_studio: "eastus2"

resource_groups:
  primary: "techworkshop-l300-ai-agents"
  ai_studio: "azureai"

naming:
  project_prefix: "zava"
  patterns:
    storage_account: "st{uniqueid}{env}"
    cosmos_db: "{uniqueid}-{env}-cosmosdb"
    # ... more patterns

environments:
  dev:
    cosmos_db:
      throughput: 400
      enable_free_tier: true
  # ... staging/prod configs
```

#### 2. **Environment Parameters** (`parameters/*.json`)
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0", 
  "parameters": {
    "location": { "value": "centralus" },
    "aiStudioLocation": { "value": "eastus2" },
    "environmentSuffix": { "value": "dev" },
    "repositoryName": { "value": "TechWorkshop-L300-AI-Apps-and-agents" }
  }
}
```

#### 3. **Updated Bicep Templates**
- ✅ Centralized resource naming variables
- ✅ Consistent tagging strategy  
- ✅ Environment-specific configurations
- ✅ Standardized parameter structure

## 🚀 Usage Instructions

### **1. Deploying Infrastructure**

The GitHub Actions workflow now uses centralized configuration:

```bash
# Workflow automatically uses:
# - src/infra/config/infrastructure-variables.yml (master config)
# - src/infra/parameters/{environment}.parameters.json (env-specific)
```

### **2. Customizing Configuration**

#### **Change Regions**:
Edit `infrastructure-variables.yml`:
```yaml
locations:
  primary: "eastus"        # Change primary region
  ai_studio: "westeurope"  # Change AI Studio region
```

#### **Modify Resource Names**:
Edit naming patterns in `infrastructure-variables.yml`:
```yaml
naming:
  project_prefix: "myproject"  # Change project identifier
  patterns:
    web_app: "{uniqueid}-{env}-webapp"  # Customize patterns
```

#### **Environment-Specific Settings**:
Edit `parameters/{env}.parameters.json`:
```json
{
  "parameters": {
    "environmentSuffix": { "value": "staging" },
    "location": { "value": "westus3" }
  }
}
```

### **3. Adding New Environments**

1. **Create Parameter File**:
   ```bash
   cp src/infra/parameters/dev.parameters.json src/infra/parameters/test.parameters.json
   ```

2. **Update Environment Suffix**:
   ```json
   {
     "parameters": {
       "environmentSuffix": { "value": "test" }
     }
   }
   ```

3. **Add to Workflow**:
   ```yaml
   # In .github/workflows/deploy-infrastructure.yml
   options:
     - dev
     - staging  
     - prod
     - test  # Add new environment
   ```

## 🔧 Configuration Reference

### **Resource Naming Patterns**

| Resource Type | Pattern | Example |
|---------------|---------|---------|
| Storage Account | `st{uniqueid}{env}` | `st7k2x9dev` |
| Cosmos DB | `{uniqueid}-{env}-cosmosdb` | `7k2x9-dev-cosmosdb` |
| Web App | `{uniqueid}-{env}-app` | `7k2x9-dev-app` |
| Container Registry | `acr{uniqueid}{env}` | `acr7k2x9dev` |
| AI Services | `aif-{uniqueid}-{env}` | `aif-7k2x9-dev` |

### **Environment Configurations**

| Environment | Cosmos Throughput | App Service Plan | AI Search |
|-------------|-------------------|------------------|-----------|
| **dev** | 400 RU/s (Free) | F1 (Free) | Free tier |
| **staging** | 800 RU/s | S1 (Standard) | Basic tier |
| **prod** | 1000 RU/s | P1v3 (Premium) | Standard tier |

### **Security Settings by Environment**

| Environment | Private Endpoints | IP Restrictions | Backup Frequency |
|-------------|-------------------|----------------|------------------|
| **dev** | ❌ Disabled | Open Access | 24 hours |
| **staging** | ❌ Disabled | Restricted | 12 hours |
| **prod** | ✅ Enabled | Highly Restricted | 6 hours |

## 🛠️ Maintenance Tasks

### **Regular Updates**

1. **Review Configuration Monthly**:
   - Check for new Azure regions
   - Update resource SKUs for cost optimization
   - Review security settings

2. **Environment Alignment**:
   - Ensure dev/staging mirrors prod architecture
   - Update test data and configurations

3. **Cost Optimization**:
   - Review `infrastructure-variables.yml` for cost settings
   - Adjust throughput and SKUs based on usage

### **Troubleshooting**

#### **Configuration File Not Found**:
```bash
# Check file exists
ls -la src/infra/config/infrastructure-variables.yml
ls -la src/infra/parameters/dev.parameters.json
```

#### **Invalid Parameter Values**:
```bash
# Validate Bicep templates
az bicep build --file src/infra/main-infrastructure.bicep
az bicep build --file src/infra/ai-studio.bicep
```

#### **Deployment Failures**:
```bash
# Check parameter file syntax
cat src/infra/parameters/dev.parameters.json | jq .
```

## 📋 Migration from Old Configuration

If migrating from the previous hardcoded approach:

1. **✅ COMPLETED**: Extracted all variables to centralized files
2. **✅ COMPLETED**: Updated Bicep templates to use centralized naming
3. **✅ COMPLETED**: Created environment-specific parameter files  
4. **✅ COMPLETED**: Updated GitHub Actions workflow to use new configuration

## 🎯 Next Steps

1. **Test Configuration**: Run deployment with new centralized config
2. **Validate Naming**: Ensure all resources follow consistent naming
3. **Document Changes**: Update team documentation
4. **Monitor Deployments**: Verify configuration works across environments

---

**📝 Note**: This centralized configuration system provides a robust, maintainable approach to infrastructure management while ensuring consistency across all environments and deployments.