#!/bin/bash

# GitHub Secrets Setup Script
# This script helps you set up GitHub secrets for the TechWorkshop L300 project
# Note: You'll need to have GitHub CLI installed and authenticated

echo "🔐 GitHub Secrets Setup for TechWorkshop L300"
echo "=============================================="
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI is not installed. Please install it first:"
    echo "   https://cli.github.com/manual/installation"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ You are not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository information
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "📂 Repository: $REPO"
echo ""

# Azure Credentials (from service principal output)
echo "🔑 Setting up Azure credentials..."
read -p "Enter the complete JSON output from 'az ad sp create-for-rbac' command: " AZURE_CREDENTIALS
gh secret set AZURE_CREDENTIALS --body "$AZURE_CREDENTIALS"
echo "✅ AZURE_CREDENTIALS set"

# Azure AI Foundry / OpenAI secrets
echo ""
echo "🤖 Setting up Azure AI credentials..."
gh secret set AZURE_OPENAI_ENDPOINT --body "https://aif-owrgnenm7wj2y.openai.azure.com/"
gh secret set AZURE_OPENAI_KEY --body "abb062bb3e7440f09595c5217eddaa73"
gh secret set AZURE_OPENAI_API_VERSION --body "2024-12-01-preview"

# Azure AI Agent Service
gh secret set AZURE_AI_AGENT_ENDPOINT --body "https://admin-mh2k31bc-eastus2.services.ai.azure.com/api/projects/admin-mh2k31bc-eastus2_project"
gh secret set AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME --body "gpt-4.1"
gh secret set AZURE_AI_AGENT_API_VERSION --body "2024-12-01-preview"

# Agent IDs
gh secret set INTERIOR_DESIGNER_AGENT_ID --body "asst_2wdhd0DbusytjpbvOTKBfT33"
gh secret set CUSTOMER_LOYALTY_AGENT_ID --body "asst_XZ5zM7JIn830rvuCeTqC5Uj2"
gh secret set INVENTORY_AGENT_ID --body "asst_T6E1gkGKNZJDE8nJvKk6SHwS"
gh secret set CORA_AGENT_ID --body "asst_kFHIDkcsaGMGwFpEOYdxFNlg"

# GPT-4.1 Model
gh secret set GPT_ENDPOINT --body "https://admin-mh2k31bc-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"
gh secret set GPT_DEPLOYMENT --body "gpt-4.1"
gh secret set GPT_API_KEY --body "<your-gpt-api-key>"
gh secret set GPT_API_VERSION --body "2024-12-01-preview"

# Phi-4 Model
gh secret set PHI_4_ENDPOINT --body "https://admin-mh2k31bc-eastus2.services.ai.azure.com/models"
gh secret set PHI_4_DEPLOYMENT --body "Phi-4"
gh secret set PHI_4_API_KEY --body "<your-phi4-api-key>"
gh secret set PHI_4_API_VERSION --body "2024-05-01-preview"

# Storage Account
gh secret set BLOB_CONNECTION_STRING --body "<your-blob-connection-string>"
gh secret set STORAGE_ACCOUNT_NAME --body "stowrgnenm7wj2y"
gh secret set STORAGE_CONTAINER_NAME --body "zava"

# AI Search
gh secret set SEARCH_ENDPOINT --body "https://owrgnenm7wj2y-search.search.windows.net"
gh secret set SEARCH_KEY --body "<your-search-key>"
gh secret set INDEX_NAME --body "zava-product-catalog"

# Cosmos DB
gh secret set COSMOS_ENDPOINT --body "https://owrgnenm7wj2y-cosmosdb.documents.azure.com:443/"
gh secret set COSMOS_KEY --body "<your-cosmos-db-key>"
gh secret set DATABASE_NAME --body "zava"
gh secret set CONTAINER_NAME --body "product_catalog"

# Application Insights
gh secret set APPLICATIONINSIGHTS_CONNECTION_STRING --body "InstrumentationKey=6d8272f1-2ce3-401d-8bcd-e8a948e9b8ad;IngestionEndpoint=https://centralus-2.in.applicationinsights.azure.com/;LiveEndpoint=https://centralus.livediagnostics.monitor.azure.com/;ApplicationId=1818ae96-bbf3-4166-9613-9e08814cd2b1"

echo "✅ All Azure AI credentials set"
echo ""
echo "🎉 All secrets have been configured successfully!"
echo ""
echo "📋 Summary of secrets created:"
echo "   - AZURE_CREDENTIALS (Service Principal)"
echo "   - Azure AI Foundry credentials (4 secrets)"
echo "   - Agent IDs (4 agents)"
echo "   - GPT-4.1 Model credentials (4 secrets)" 
echo "   - Phi-4 Model credentials (4 secrets)"
echo "   - Storage Account credentials (3 secrets)"
echo "   - AI Search credentials (3 secrets)"
echo "   - Cosmos DB credentials (4 secrets)"
echo "   - Application Insights (1 secret)"
echo ""
echo "🚀 You can now run GitHub Actions workflows that use these secrets!"