#!/usr/bin/env pwsh
# setup-github-secrets.ps1
# PowerShell script to automate GitHub secrets setup for infrastructure deployment
# This script works on Windows, Linux, and macOS with PowerShell Core installed

param(
    [Parameter(Mandatory = $true, HelpMessage = "Azure Subscription ID")]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $false, HelpMessage = "Service Principal Name")]
    [string]$ServicePrincipalName = "github-actions-techworkshop-l300",
    
    [Parameter(Mandatory = $false, HelpMessage = "GitHub Personal Access Token")]
    [string]$GitHubToken = $null,
    
    [Parameter(Mandatory = $false, HelpMessage = "Skip service principal creation if it already exists")]
    [switch]$SkipServicePrincipal
)

# Color output functions
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Info "🚀 GitHub Secrets Setup for Infrastructure Deployment"
Write-Info "================================================="

# Validate prerequisites
Write-Info "Checking prerequisites..."

# Check Azure CLI
try {
    $azVersion = az version --query '"azure-cli"' -o tsv 2>$null
    if ($azVersion) {
        Write-Success "Azure CLI version: $azVersion"
    } else {
        throw "Azure CLI not found"
    }
} catch {
    Write-Error "Azure CLI is not installed or not in PATH"
    Write-Info "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check GitHub CLI
try {
    $ghVersion = gh --version 2>$null | Select-String "gh version" | ForEach-Object { $_.ToString().Split()[2] }
    if ($ghVersion) {
        Write-Success "GitHub CLI version: $ghVersion"
    } else {
        throw "GitHub CLI not found"
    }
} catch {
    Write-Error "GitHub CLI is not installed or not in PATH"
    Write-Info "Install from: https://cli.github.com/"
    exit 1
}

# Check Azure login status
Write-Info "Checking Azure authentication..."
try {
    $currentAccount = az account show --query "user.name" -o tsv 2>$null
    if ($currentAccount) {
        Write-Success "Logged in as: $currentAccount"
    } else {
        throw "Not logged in"
    }
} catch {
    Write-Error "Please log in to Azure first: az login"
    exit 1
}

# Set subscription
Write-Info "Setting Azure subscription..."
try {
    az account set --subscription $SubscriptionId
    $currentSub = az account show --query "{name:name, id:id}" -o json | ConvertFrom-Json
    Write-Success "Active subscription: $($currentSub.name) ($($currentSub.id))"
} catch {
    Write-Error "Failed to set subscription: $SubscriptionId"
    exit 1
}

# Check GitHub authentication
Write-Info "Checking GitHub authentication..."
try {
    $ghUser = gh auth status 2>&1 | Select-String "Logged in to github.com as" | ForEach-Object { $_.ToString().Split()[-1] }
    if ($ghUser) {
        Write-Success "Logged in to GitHub as: $ghUser"
    } else {
        Write-Info "Please authenticate with GitHub..."
        gh auth login
        $ghUser = gh auth status 2>&1 | Select-String "Logged in to github.com as" | ForEach-Object { $_.ToString().Split()[-1] }
        Write-Success "Logged in to GitHub as: $ghUser"
    }
} catch {
    Write-Error "GitHub authentication failed"
    exit 1
}

# Create or retrieve service principal
if (-not $SkipServicePrincipal) {
    Write-Info "Creating Azure Service Principal..."
    
    try {
        # Check if service principal already exists
        $existingSp = az ad sp list --display-name $ServicePrincipalName --query "[0].{appId:appId, objectId:id}" -o json | ConvertFrom-Json
        
        if ($existingSp -and $existingSp.appId) {
            Write-Warning "Service Principal '$ServicePrincipalName' already exists with App ID: $($existingSp.appId)"
            $useExisting = Read-Host "Use existing service principal? (y/N)"
            
            if ($useExisting -eq 'y' -or $useExisting -eq 'Y') {
                Write-Info "Using existing service principal..."
                
                # Get current role assignments
                $roleAssignments = az role assignment list --assignee $existingSp.appId --scope "/subscriptions/$SubscriptionId" --query "[?roleDefinitionName=='Owner']" -o json | ConvertFrom-Json
                
                if ($roleAssignments.Count -eq 0) {
                    Write-Info "Adding Owner role to existing service principal..."
                    az role assignment create --assignee $existingSp.appId --role "Owner" --scope "/subscriptions/$SubscriptionId"
                    Write-Success "Owner role assigned to service principal"
                }
                
                # Create new credentials for the existing SP
                Write-Info "Creating new credentials for existing service principal..."
                $spCredentials = az ad sp credential reset --id $existingSp.appId --sdk-auth | ConvertFrom-Json
                Write-Success "New credentials created for existing service principal"
            } else {
                Write-Info "Please choose a different service principal name or use --SkipServicePrincipal flag"
                exit 1
            }
        } else {
            # Create new service principal
            Write-Info "Creating new service principal with Owner role..."
            $spOutput = az ad sp create-for-rbac --name $ServicePrincipalName --role "Owner" --scopes "/subscriptions/$SubscriptionId" --sdk-auth
            $spCredentials = $spOutput | ConvertFrom-Json
            Write-Success "Service Principal created: $($spCredentials.clientId)"
        }
        
    } catch {
        Write-Error "Failed to create service principal: $_"
        exit 1
    }
} else {
    Write-Info "Skipping service principal creation as requested"
    Write-Warning "Please ensure you have the service principal credentials available"
    
    # Prompt for credentials
    $clientId = Read-Host "Enter Service Principal Client ID"
    $clientSecret = Read-Host "Enter Service Principal Client Secret" -AsSecureString
    $tenantId = Read-Host "Enter Tenant ID"
    
    # Convert SecureString back to plain text for JSON
    $clientSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret))
    
    # Construct credentials object
    $spCredentials = @{
        clientId = $clientId
        clientSecret = $clientSecretPlain
        subscriptionId = $SubscriptionId
        tenantId = $tenantId
        activeDirectoryEndpointUrl = "https://login.microsoftonline.com"
        resourceManagerEndpointUrl = "https://management.azure.com/"
        activeDirectoryGraphResourceId = "https://graph.windows.net/"
        sqlManagementEndpointUrl = "https://management.core.windows.net:8443/"
        galleryEndpointUrl = "https://gallery.azure.com/"
        managementEndpointUrl = "https://management.core.windows.net/"
    }
}

# Get GitHub token if not provided
if (-not $GitHubToken) {
    Write-Info "Getting GitHub Personal Access Token..."
    Write-Info "The token needs these scopes: repo, workflow, admin:repo_hook"
    
    try {
        # Try to get token from gh CLI
        $GitHubToken = gh auth token 2>$null
        if ($GitHubToken) {
            Write-Success "Using GitHub CLI token"
        } else {
            throw "No token from CLI"
        }
    } catch {
        Write-Warning "Could not get token from GitHub CLI"
        Write-Info "Please create a Personal Access Token with required scopes:"
        Write-Info "1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)"
        Write-Info "2. Generate new token with scopes: repo, workflow, admin:repo_hook"
        $GitHubToken = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
        $GitHubToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubToken))
    }
}

# Set GitHub secrets
Write-Info "Setting GitHub repository secrets..."

try {
    # Convert credentials to JSON string
    $azureCredentialsJson = $spCredentials | ConvertTo-Json -Depth 10 -Compress
    
    # Set AZURE_CREDENTIALS
    Write-Info "Setting AZURE_CREDENTIALS secret..."
    $azureCredentialsJson | gh secret set AZURE_CREDENTIALS
    Write-Success "AZURE_CREDENTIALS secret set"
    
    # Set AZURE_CLIENT_ID
    Write-Info "Setting AZURE_CLIENT_ID secret..."
    $spCredentials.clientId | gh secret set AZURE_CLIENT_ID
    Write-Success "AZURE_CLIENT_ID secret set"
    
    # Set GITHUB_TOKEN
    Write-Info "Setting GITHUB_TOKEN secret..."
    $GitHubToken | gh secret set GITHUB_TOKEN
    Write-Success "GITHUB_TOKEN secret set"
    
    Write-Success "🎉 All GitHub secrets configured successfully!"
    
} catch {
    Write-Error "Failed to set GitHub secrets: $_"
    Write-Info "You may need to set them manually in GitHub repository settings"
    exit 1
}

# Display summary
Write-Info ""
Write-Info "📋 Setup Summary"
Write-Info "================"
Write-Success "Service Principal ID: $($spCredentials.clientId)"
Write-Success "Subscription ID: $($spCredentials.subscriptionId)"
Write-Success "Tenant ID: $($spCredentials.tenantId)"
Write-Info ""
Write-Info "🚀 Next Steps:"
Write-Info "1. Go to GitHub → Actions → 'Deploy Complete Infrastructure'"
Write-Info "2. Click 'Run workflow' and select your deployment options"
Write-Info "3. Monitor the deployment progress in the Actions tab"
Write-Info ""
Write-Info "📚 For detailed instructions, see: DEPLOYMENT-SETUP.md"

Write-Success "✅ Setup completed successfully!"