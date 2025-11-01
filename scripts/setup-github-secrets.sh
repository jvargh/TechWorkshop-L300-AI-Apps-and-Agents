#!/bin/bash
# setup-github-secrets.sh
# Bash script to automate GitHub secrets setup for infrastructure deployment
# This script works on Linux, macOS, and Windows with WSL/Git Bash

set -e  # Exit on any error

# Color output functions
print_success() { echo -e "\033[32m✅ $1\033[0m"; }
print_info() { echo -e "\033[36mℹ️  $1\033[0m"; }
print_warning() { echo -e "\033[33m⚠️  $1\033[0m"; }
print_error() { echo -e "\033[31m❌ $1\033[0m"; }

# Parse command line arguments
SUBSCRIPTION_ID=""
SERVICE_PRINCIPAL_NAME="github-actions-techworkshop-l300"
GITHUB_TOKEN=""
SKIP_SERVICE_PRINCIPAL=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -s|--subscription-id)
      SUBSCRIPTION_ID="$2"
      shift 2
      ;;
    -n|--service-principal-name)
      SERVICE_PRINCIPAL_NAME="$2"
      shift 2
      ;;
    -t|--github-token)
      GITHUB_TOKEN="$2"
      shift 2
      ;;
    --skip-service-principal)
      SKIP_SERVICE_PRINCIPAL=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 -s SUBSCRIPTION_ID [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -s, --subscription-id           Azure Subscription ID (required)"
      echo "  -n, --service-principal-name    Service Principal Name (default: github-actions-techworkshop-l300)"
      echo "  -t, --github-token             GitHub Personal Access Token"
      echo "      --skip-service-principal   Skip service principal creation"
      echo "  -h, --help                     Show this help message"
      exit 0
      ;;
    *)
      print_error "Unknown option: $1"
      echo "Use -h or --help for usage information"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [[ -z "$SUBSCRIPTION_ID" ]]; then
  print_error "Subscription ID is required. Use -s or --subscription-id"
  echo "Use -h or --help for usage information"
  exit 1
fi

print_info "🚀 GitHub Secrets Setup for Infrastructure Deployment"
print_info "================================================="

# Validate prerequisites
print_info "Checking prerequisites..."

# Check Azure CLI
if command -v az &> /dev/null; then
  AZ_VERSION=$(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo "unknown")
  print_success "Azure CLI version: $AZ_VERSION"
else
  print_error "Azure CLI is not installed or not in PATH"
  print_info "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
  exit 1
fi

# Check GitHub CLI
if command -v gh &> /dev/null; then
  GH_VERSION=$(gh --version | head -n1 | cut -d' ' -f3)
  print_success "GitHub CLI version: $GH_VERSION"
else
  print_error "GitHub CLI is not installed or not in PATH"
  print_info "Install from: https://cli.github.com/"
  exit 1
fi

# Check Azure login status
print_info "Checking Azure authentication..."
CURRENT_ACCOUNT=$(az account show --query "user.name" -o tsv 2>/dev/null || echo "")
if [[ -n "$CURRENT_ACCOUNT" ]]; then
  print_success "Logged in as: $CURRENT_ACCOUNT"
else
  print_error "Please log in to Azure first: az login"
  exit 1
fi

# Set subscription
print_info "Setting Azure subscription..."
if az account set --subscription "$SUBSCRIPTION_ID" 2>/dev/null; then
  CURRENT_SUB=$(az account show --query "{name:name, id:id}" -o json)
  SUB_NAME=$(echo "$CURRENT_SUB" | jq -r '.name')
  SUB_ID=$(echo "$CURRENT_SUB" | jq -r '.id')
  print_success "Active subscription: $SUB_NAME ($SUB_ID)"
else
  print_error "Failed to set subscription: $SUBSCRIPTION_ID"
  exit 1
fi

# Check GitHub authentication
print_info "Checking GitHub authentication..."
if gh auth status &> /dev/null; then
  GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
  print_success "Logged in to GitHub as: $GH_USER"
else
  print_info "Please authenticate with GitHub..."
  gh auth login
  GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
  print_success "Logged in to GitHub as: $GH_USER"
fi

# Create or retrieve service principal
if [[ "$SKIP_SERVICE_PRINCIPAL" != true ]]; then
  print_info "Creating Azure Service Principal..."
  
  # Check if service principal already exists
  EXISTING_SP=$(az ad sp list --display-name "$SERVICE_PRINCIPAL_NAME" --query "[0].{appId:appId, objectId:id}" -o json 2>/dev/null || echo "{}")
  APP_ID=$(echo "$EXISTING_SP" | jq -r '.appId // empty')
  
  if [[ -n "$APP_ID" && "$APP_ID" != "null" ]]; then
    print_warning "Service Principal '$SERVICE_PRINCIPAL_NAME' already exists with App ID: $APP_ID"
    read -p "Use existing service principal? (y/N): " -n 1 -r USE_EXISTING
    echo
    
    if [[ $USE_EXISTING =~ ^[Yy]$ ]]; then
      print_info "Using existing service principal..."
      
      # Check current role assignments
      ROLE_COUNT=$(az role assignment list --assignee "$APP_ID" --scope "/subscriptions/$SUBSCRIPTION_ID" --query "[?roleDefinitionName=='Owner'] | length(@)" -o tsv)
      
      if [[ "$ROLE_COUNT" == "0" ]]; then
        print_info "Adding Owner role to existing service principal..."
        az role assignment create --assignee "$APP_ID" --role "Owner" --scope "/subscriptions/$SUBSCRIPTION_ID"
        print_success "Owner role assigned to service principal"
      fi
      
      # Create new credentials for the existing SP
      print_info "Creating new credentials for existing service principal..."
      SP_CREDENTIALS=$(az ad sp credential reset --id "$APP_ID" --sdk-auth)
      print_success "New credentials created for existing service principal"
    else
      print_info "Please choose a different service principal name or use --skip-service-principal flag"
      exit 1
    fi
  else
    # Create new service principal
    print_info "Creating new service principal with Owner role..."
    SP_CREDENTIALS=$(az ad sp create-for-rbac --name "$SERVICE_PRINCIPAL_NAME" --role "Owner" --scopes "/subscriptions/$SUBSCRIPTION_ID" --sdk-auth)
    CLIENT_ID=$(echo "$SP_CREDENTIALS" | jq -r '.clientId')
    print_success "Service Principal created: $CLIENT_ID"
  fi
else
  print_info "Skipping service principal creation as requested"
  print_warning "Please ensure you have the service principal credentials available"
  
  # Prompt for credentials
  read -p "Enter Service Principal Client ID: " CLIENT_ID
  read -s -p "Enter Service Principal Client Secret: " CLIENT_SECRET
  echo
  read -p "Enter Tenant ID: " TENANT_ID
  
  # Construct credentials JSON
  SP_CREDENTIALS=$(jq -n \
    --arg clientId "$CLIENT_ID" \
    --arg clientSecret "$CLIENT_SECRET" \
    --arg subscriptionId "$SUBSCRIPTION_ID" \
    --arg tenantId "$TENANT_ID" \
    '{
      clientId: $clientId,
      clientSecret: $clientSecret,
      subscriptionId: $subscriptionId,
      tenantId: $tenantId,
      activeDirectoryEndpointUrl: "https://login.microsoftonline.com",
      resourceManagerEndpointUrl: "https://management.azure.com/",
      activeDirectoryGraphResourceId: "https://graph.windows.net/",
      sqlManagementEndpointUrl: "https://management.core.windows.net:8443/",
      galleryEndpointUrl: "https://gallery.azure.com/",
      managementEndpointUrl: "https://management.core.windows.net/"
    }')
fi

# Get GitHub token if not provided
if [[ -z "$GITHUB_TOKEN" ]]; then
  print_info "Getting GitHub Personal Access Token..."
  print_info "The token needs these scopes: repo, workflow, admin:repo_hook"
  
  # Try to get token from gh CLI
  if GITHUB_TOKEN=$(gh auth token 2>/dev/null); then
    print_success "Using GitHub CLI token"
  else
    print_warning "Could not get token from GitHub CLI"
    print_info "Please create a Personal Access Token with required scopes:"
    print_info "1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)"
    print_info "2. Generate new token with scopes: repo, workflow, admin:repo_hook"
    read -s -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
    echo
  fi
fi

# Set GitHub secrets
print_info "Setting GitHub repository secrets..."

# Set AZURE_CREDENTIALS
print_info "Setting AZURE_CREDENTIALS secret..."
echo "$SP_CREDENTIALS" | gh secret set AZURE_CREDENTIALS
print_success "AZURE_CREDENTIALS secret set"

# Set AZURE_CLIENT_ID
print_info "Setting AZURE_CLIENT_ID secret..."
CLIENT_ID=$(echo "$SP_CREDENTIALS" | jq -r '.clientId')
echo "$CLIENT_ID" | gh secret set AZURE_CLIENT_ID
print_success "AZURE_CLIENT_ID secret set"

# Set GITHUB_TOKEN
print_info "Setting GITHUB_TOKEN secret..."
echo "$GITHUB_TOKEN" | gh secret set GITHUB_TOKEN
print_success "GITHUB_TOKEN secret set"

print_success "🎉 All GitHub secrets configured successfully!"

# Display summary
print_info ""
print_info "📋 Setup Summary"
print_info "================"
print_success "Service Principal ID: $CLIENT_ID"
print_success "Subscription ID: $SUBSCRIPTION_ID"
TENANT_ID=$(echo "$SP_CREDENTIALS" | jq -r '.tenantId')
print_success "Tenant ID: $TENANT_ID"
print_info ""
print_info "🚀 Next Steps:"
print_info "1. Go to GitHub → Actions → 'Deploy Complete Infrastructure'"
print_info "2. Click 'Run workflow' and select your deployment options"
print_info "3. Monitor the deployment progress in the Actions tab"
print_info ""
print_info "📚 For detailed instructions, see: DEPLOYMENT-SETUP.md"

print_success "✅ Setup completed successfully!"