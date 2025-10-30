import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import CodeInterpreterTool,FunctionTool, ToolSet
from typing import Callable, Set, Any
import json
from dotenv import load_dotenv
load_dotenv()

CORA_PROMPT_TARGET = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'prompts', 'ShopperAgentPrompt.txt')
with open(CORA_PROMPT_TARGET, 'r', encoding='utf-8') as file:
    CORA_PROMPT = file.read()

project_endpoint = os.environ["AZURE_AI_AGENT_ENDPOINT"]

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)


with project_client:
    # Check if agent already exists
    agent_name = "Cora"
    existing_agent = None
    
    try:
        # List existing agents and find by name
        agents_list = project_client.agents.list_agents()
        for agent in agents_list:
            if agent.name == agent_name:
                existing_agent = agent
                break
    except Exception as e:
        print(f"Error listing agents: {e}")
    
    if existing_agent:
        # Update existing agent
        print(f"Found existing agent: {existing_agent.id}")
        agent = project_client.agents.update_agent(
            assistant_id=existing_agent.id,
            model=os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"],
            name=agent_name,
            instructions=CORA_PROMPT,
        )
        print(f"Updated agent, ID: {agent.id}")
    else:
        # Create new agent
        agent = project_client.agents.create_agent(
            model=os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"],  # Model deployment name
            name=agent_name,  # Name of the agent
            instructions=CORA_PROMPT,  # Instructions for the agent
            # toolset=toolset
        )
        print(f"Created new agent, ID: {agent.id}")