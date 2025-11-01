#!/usr/bin/env python3
"""
Script to delete all AI agents from Azure AI Studio
This will clean up existing agents before redeploying via GitHub Actions
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

def delete_all_agents():
    """Delete all existing AI agents from the Azure AI Studio project"""
    
    try:
        # Initialize the AI Project client
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        
        print("🔍 Listing all existing AI agents...")
        
        # List all agents
        agents = project_client.agents.list_agents()
        agent_list = []
        
        for agent in agents:
            agent_list.append(agent)
            print(f"Found agent: {agent.name} (ID: {agent.id})")
        
        if not agent_list:
            print("✅ No agents found to delete.")
            return
        
        print(f"\n🗑️  Deleting {len(agent_list)} agents...")
        
        # Delete each agent
        for agent in agent_list:
            try:
                print(f"Deleting agent: {agent.name} (ID: {agent.id})")
                project_client.agents.delete_agent(agent.id)
                print(f"✅ Successfully deleted agent: {agent.name}")
            except Exception as e:
                print(f"❌ Failed to delete agent {agent.name}: {str(e)}")
        
        print("\n🎉 Agent cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error during agent cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    print("🚀 Starting AI Agent cleanup process...")
    delete_all_agents()