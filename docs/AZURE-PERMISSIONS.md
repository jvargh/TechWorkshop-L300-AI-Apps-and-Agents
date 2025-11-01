# Azure Permissions and Service Principal Setup

This document outlines the Azure permissions required for the TechWorkshop L300 AI Agents infrastructure deployment.

## 🔐 Required Service Principal Permissions

The GitHub Actions workflows require a service principal with the following permissions at the **subscription level**:

### **1. Contributor Role**
- **Purpose**: Create and manage all Azure resources
- **Scope**: `/subscriptions/{subscription-id}`
- **Permissions**: Full access to create, modify, and delete Azure resources
- **Required for**:
  - Creating resource groups
  - Deploying Bicep templates
  - Managing Azure services (Cosmos DB, Storage, AI Services, etc.)

### **2. User Access Administrator Role**
- **Purpose**: Manage role assignments for deployed resources
- **Scope**: `/subscriptions/{subscription-id}`
- **Permissions**: Can assign roles to other resources and managed identities
- **Required for**:
  - Setting up managed identity permissions
  - Configuring service-to-service authentication
  - Assigning roles to deployed applications

## 🛠️ Setup Commands

If you need to manually assign these roles to your service principal, use these commands:

```bash
# Replace with your service principal object ID and subscription ID
SP_OBJECT_ID="your-service-principal-object-id"
SUBSCRIPTION_ID="your-subscription-id"

# Assign Contributor role
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"

# Assign User Access Administrator role
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "User Access Administrator" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"
```

## 🔍 Permission Validation

The infrastructure workflow now includes automatic permission validation that:

1. **Checks existing roles** for the service principal
2. **Automatically assigns missing roles** if the current user has permission
3. **Fails with clear error messages** if permissions are insufficient
4. **Logs all permission checks** for troubleshooting

### **Validation Steps in Workflow**:
```yaml
- name: Validate service principal permissions
  run: |
    # Check for Contributor role
    # Check for User Access Administrator role  
    # Assign missing roles if possible
    # Report validation results
```

## ⚠️ Common Permission Issues

### **Issue**: `AuthorizationFailed` when creating resource groups
**Cause**: Service principal lacks Contributor role at subscription level  
**Solution**: Assign Contributor role using the commands above

### **Issue**: Failed to assign roles to managed identities
**Cause**: Service principal lacks User Access Administrator role  
**Solution**: Assign User Access Administrator role using the commands above

### **Issue**: Cannot access secrets after deployment
**Cause**: Managed identity permissions not properly configured  
**Solution**: Re-run infrastructure deployment after fixing service principal roles

## 🎯 Best Practices

### **Development Environment**:
- Use the minimum required permissions
- Scope roles to specific resource groups when possible
- Regularly audit role assignments

### **Production Environment**:
- Use dedicated service principals for each environment
- Implement role assignment automation
- Monitor permission usage with Azure AD logs

### **CI/CD Pipeline**:
- Store service principal credentials as GitHub secrets
- Rotate service principal secrets regularly
- Use managed identities where possible instead of service principals

## 🔄 Automatic Permission Management

The workflow includes these automatic permission features:

1. **Pre-deployment Validation**: Checks all required permissions before starting deployment
2. **Auto-assignment**: Attempts to assign missing roles if the workflow has permission
3. **Clear Error Messages**: Provides specific guidance when permissions are missing
4. **Permission Logging**: Records all permission checks for audit trails

## 📋 GitHub Secrets Required

The workflow expects these GitHub secrets to be configured:

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `AZURE_CREDENTIALS` | Service principal authentication JSON | All Azure operations |
| `AZURE_CLIENT_ID` | Service principal application ID | Permission validation and role assignments |
| `GITHUB_TOKEN` | GitHub API access token | Updating repository secrets |

### **AZURE_CREDENTIALS Format**:
```json
{
  "clientId": "your-service-principal-app-id",
  "clientSecret": "your-service-principal-secret", 
  "subscriptionId": "your-azure-subscription-id",
  "tenantId": "your-azure-tenant-id"
}
```

## 🚨 Troubleshooting Permission Issues

### **Step 1: Verify Service Principal**
```bash
# Check if service principal exists and get object ID
az ad sp show --id "your-app-id" --query "{ObjectId:id, AppId:appId}"
```

### **Step 2: Check Current Role Assignments**
```bash
# List current roles for service principal
az role assignment list --assignee "service-principal-object-id" --all
```

### **Step 3: Test Resource Creation**
```bash
# Test if service principal can create resources
az group create --name "test-rg" --location "centralus"
```

### **Step 4: Verify Subscription Access**
```bash
# Confirm subscription access and permissions
az account show --query "{SubscriptionId:id, TenantId:tenantId}"
```

---

**🔒 Security Note**: Always follow the principle of least privilege. The permissions documented here are the minimum required for the infrastructure deployment to work properly.