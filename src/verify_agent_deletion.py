#!/usr/bin/env python3
"""
Script to verify that all AI agents have been deleted from Azure AI Studio
This confirms the cleanup was successful before redeploying via GitHub Actions
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

def verify_agent_deletion():
    """Verify that all AI agents have been successfully deleted"""
    
    try:
        # Initialize the AI Project client
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        
        print("🔍 Checking current AI agents in Azure AI Studio...")
        print("=" * 60)
        
        # List all agents
        agents = project_client.agents.list_agents()
        agent_list = []
        
        for agent in agents:
            agent_list.append(agent)
            print(f"❌ STILL EXISTS: {agent.name} (ID: {agent.id})")
        
        if not agent_list:
            print("✅ SUCCESS: No agents found - All agents have been deleted!")
            print("\n📋 Previously deleted agents:")
            print("   • Cora Shopping Agent")
            print("   • Zava Interior Design Agent") 
            print("   • Zava Inventory Agent")
            print("   • Zava Customer Loyalty Agent")
            print("\n🚀 Ready to redeploy agents via GitHub Actions!")
            return True
        else:
            print(f"\n⚠️  WARNING: {len(agent_list)} agent(s) still exist!")
            print("   These agents were not deleted and may cause conflicts.")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying agent deletion: {str(e)}")
        return False

def check_github_secrets():
    """Display the agent IDs stored in GitHub secrets for reference"""
    print("\n📋 GitHub Secret Agent IDs (will be updated after redeployment):")
    print("=" * 60)
    
    # These are the agent ID secrets that exist in GitHub
    secrets = [
        "CORA_AGENT_ID",
        "INTERIOR_DESIGNER_AGENT_ID", 
        "INVENTORY_AGENT_ID",
        "CUSTOMER_LOYALTY_AGENT_ID"
    ]
    
    for secret in secrets:
        print(f"   🔑 {secret}")
    
    print("\n💡 These secrets will be automatically updated when workflows run.")

if __name__ == "__main__":
    print("🔍 AI Agent Deletion Verification")
    print("=" * 60)
    
    # Verify deletion
    deletion_successful = verify_agent_deletion()
    
    # Show GitHub secrets info
    check_github_secrets()
    
    print("\n" + "=" * 60)
    if deletion_successful:
        print("✅ VERIFICATION COMPLETE: Ready to trigger GitHub Actions!")
        print("🎯 Next step: Run 'gh workflow run' commands for all 4 agent workflows")
    else:
        print("⚠️  VERIFICATION FAILED: Some agents still exist")
        print("🔄 Consider running the deletion script again")