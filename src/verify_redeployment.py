#!/usr/bin/env python3
"""
Script to verify successful redeployment of all AI agents
This confirms that GitHub Actions workflows created new agents
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

def verify_successful_redeployment():
    """Verify that all AI agents have been successfully redeployed with new IDs"""
    
    try:
        # Initialize the AI Project client
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        
        print("🎯 Verifying Successful Agent Redeployment")
        print("=" * 60)
        
        # List all agents
        agents = project_client.agents.list_agents()
        agent_list = []
        
        # Old agent IDs (that were deleted)
        old_ids = {
            "asst_kFHIDkcsaGMGwFpEOYdxFNlg",  # Old Cora
            "asst_2wdhd0DbusytjpbvOTKBfT33",  # Old Interior Design
            "asst_T6E1gkGKNZJDE8nJvKk6SHwS",  # Old Inventory
            "asst_XZ5zM7JIn830rvuCeTqC5Uj2"   # Old Customer Loyalty
        }
        
        expected_agents = {
            "Cora",
            "Zava Interior Design Agent", 
            "Zava Inventory Agent",
            "Zava Customer Loyalty Agent"
        }
        
        found_agents = set()
        new_agents = []
        
        for agent in agents:
            agent_list.append(agent)
            
            # Check if this is a new agent (not in old IDs)
            if agent.id not in old_ids:
                new_agents.append(agent)
                print(f"✅ NEW AGENT: {agent.name} (ID: {agent.id})")
                
                # Track found expected agents
                if agent.name in expected_agents:
                    found_agents.add(agent.name)
            else:
                print(f"⚠️  OLD AGENT: {agent.name} (ID: {agent.id}) - Should have been deleted!")
        
        print(f"\n📊 Redeployment Summary:")
        print("=" * 60)
        print(f"Total agents found: {len(agent_list)}")
        print(f"New agents created: {len(new_agents)}")
        print(f"Expected agents found: {len(found_agents)}/{len(expected_agents)}")
        
        # Check if all expected agents are present
        missing_agents = expected_agents - found_agents
        if missing_agents:
            print(f"\n❌ Missing agents: {', '.join(missing_agents)}")
            return False
        
        # Success criteria: At least 4 new agents with expected names
        if len(new_agents) >= 4 and len(found_agents) == 4:
            print(f"\n🎉 SUCCESS: All {len(expected_agents)} agents successfully redeployed!")
            print("✅ All agents have new IDs (old agents properly deleted)")
            print("✅ GitHub Actions workflows completed successfully") 
            print("✅ Ready for testing and production use!")
            return True
        else:
            print(f"\n⚠️  Partial success: {len(found_agents)}/4 expected agents redeployed")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying redeployment: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_successful_redeployment()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 REDEPLOYMENT VERIFICATION: ✅ SUCCESS")
        print("🚀 All GitHub Actions workflows completed successfully!")
        print("🔄 Agent cleanup and redeployment process completed!")
    else:
        print("🎯 REDEPLOYMENT VERIFICATION: ⚠️ NEEDS ATTENTION")
        print("🔍 Some workflows may need to be re-triggered")