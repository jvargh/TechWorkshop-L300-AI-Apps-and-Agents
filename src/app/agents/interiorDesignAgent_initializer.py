import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool, ToolSet

# Interior Design Agent - Updated with CI/CD automation
from typing import Callable, Set, Any
from tools.imageCreationTool import create_image

# Load the prompt instructions for the interior design agent from a file
# path = r'prompts\InteriorDesignAgentPrompt.txt'
ID_PROMPT_TARGET = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'prompts', 'InteriorDesignAgentPrompt.txt')
with open(ID_PROMPT_TARGET, 'r', encoding='utf-8') as file:
    ID_PROMPT = file.read()

project_endpoint = os.environ["AZURE_AI_AGENT_ENDPOINT"]

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

# Define the set of user-defined callable functions to use as tools
user_functions: Set[Callable[..., Any]] = {
    create_image
}

# Initialize toolset and enable auto function calling with the tools
functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
project_client.agents.enable_auto_function_calls(tools=functions)

 # Create or update the agent using a specific deployment, name, instructions, and toolset
with project_client:
    # Check if agent already exists
    agent_name = "Zava Interior Design Agent"
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
            instructions=ID_PROMPT,
            toolset=toolset,
        )
        print(f"Updated agent, ID: {agent.id}")
    else:
        # Create new agent
        agent = project_client.agents.create_agent(
            model=os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"],  # Model deployment name
            name=agent_name,  # Name of the agent
            instructions=ID_PROMPT,  # Instructions for the agent
            toolset=toolset)
        print(f"Created new agent, ID: {agent.id}")