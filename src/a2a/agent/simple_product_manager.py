"""
Simple Product Manager for testing Semantic Kernel basic functionality
"""

import os
import asyncio
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent, AuthorRole
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleProductManager:
    """Simple Product Manager without function calling for testing"""
    
    def __init__(self):
        self.kernel = None
        self._initialize_kernel()
    
    def _initialize_kernel(self):
        """Initialize the Semantic Kernel with Azure OpenAI"""
        try:
            self.kernel = Kernel()
            
            # Add Azure OpenAI Chat Completion service using the correct GPT-4.1 endpoint
            service_id = "azure_openai_chat"
            
            # Use the correct base endpoint for GPT-4.1 (without the deployment path)
            gpt_endpoint = "https://admin-mh2k31bc-eastus2.cognitiveservices.azure.com"
            
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id=service_id,
                    deployment_name=os.getenv("gpt_deployment", "gpt-4.1"),
                    endpoint=gpt_endpoint,
                    api_key=os.getenv("gpt_api_key"),
                    api_version=os.getenv("gpt_api_version", "2024-12-01-preview")
                )
            )
            
            logger.info("Simple Semantic Kernel initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Semantic Kernel: {e}", exc_info=True)
            raise
    
    async def process_simple_message(self, message: str) -> str:
        """Process a message using basic Semantic Kernel functionality"""
        try:
            logger.info(f"Processing simple message: {message[:50]}...")
            
            # Create chat history
            chat_history = ChatHistory()
            
            # Add system message
            system_message = """You are a helpful Product Management Assistant for Zava, a home improvement store. 
You help customers with product information, recommendations, and general inquiries about home improvement products.
Be friendly, helpful, and knowledgeable about home improvement and furniture products."""
            
            chat_history.add_system_message(system_message)
            chat_history.add_user_message(message)
            
            # Get chat completion service
            chat_completion = self.kernel.get_service(type=AzureChatCompletion)
            
            # Generate response with proper settings
            settings = OpenAIChatPromptExecutionSettings(
                max_completion_tokens=1000,
                temperature=0.7
            )
            
            response = await chat_completion.get_chat_message_content(
                chat_history=chat_history,
                settings=settings
            )
            
            result = str(response.content) if response and response.content else "No response generated"
            logger.info(f"Generated response: {result[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error processing simple message: {e}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."


# Global instance
simple_product_manager = None

def get_simple_product_manager() -> SimpleProductManager:
    """Get or create the global SimpleProductManager instance"""
    global simple_product_manager
    if simple_product_manager is None:
        simple_product_manager = SimpleProductManager()
    return simple_product_manager