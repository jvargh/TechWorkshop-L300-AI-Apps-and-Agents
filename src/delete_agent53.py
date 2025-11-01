#!/usr/bin/env python3
"""
Script to delete Agent53 specifically
This removes the extra agent while keeping the 4 main agents
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

def delete_agent53():
    """Delete the specific Agent53 that shouldn't be there"""
    
    try:
        # Initialize the AI Project client
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        
        print("🎯 Deleting Agent53")
        print("=" * 40)
        
        # Target Agent53 specifically
        agent53_id = "asst_2mbh9GFHWaAMxY5gEbW8ZO93"
        agent53_name = "Agent53"
        
        # List all agents first to confirm it exists
        agents = project_client.agents.list_agents()
        found_agent53 = False
        
        for agent in agents:
            if agent.id == agent53_id or agent.name == agent53_name:
                found_agent53 = True
                print(f"🔍 Found target agent: {agent.name} (ID: {agent.id})")
                break
        
        if not found_agent53:
            print(f"✅ Agent53 not found - already deleted or doesn't exist")
            return True
        
        # Delete Agent53
        try:
            print(f"🗑️  Deleting {agent53_name} (ID: {agent53_id})")
            project_client.agents.delete_agent(agent53_id)
            print(f"✅ Successfully deleted {agent53_name}")
            
            # Verify deletion
            print("🔍 Verifying deletion...")
            agents_after = project_client.agents.list_agents()
            still_exists = False
            
            for agent in agents_after:
                if agent.id == agent53_id:
                    still_exists = True
                    break
            
            if still_exists:
                print(f"❌ Agent53 still exists after deletion attempt")
                return False
            else:
                print(f"✅ Confirmed: Agent53 successfully removed")
                
                # Show remaining agents
                print("\n📋 Remaining agents:")
                for agent in agents_after:
                    print(f"   ✓ {agent.name} (ID: {agent.id})")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete Agent53: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Error during Agent53 cleanup: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Agent53 cleanup...")
    success = delete_agent53()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Agent53 cleanup completed successfully!")
        print("✅ Only the 4 main agents remain")
    else:
        print("❌ Agent53 cleanup failed")
        print("🔍 Manual cleanup may be required")