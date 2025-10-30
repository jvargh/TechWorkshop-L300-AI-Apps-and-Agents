"""
Enhanced Product Management Agent using A2A Protocol with Multiple Specialized Agents
This implementation follows the TechWorkshop requirements for multi-agent architecture
"""

import os
import logging
import time
from typing import Any, Annotated
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent, AuthorRole
from opentelemetry import trace

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry tracer for agent monitoring
tracer = trace.get_tracer(__name__)

# Constants for span attributes
PROCESSING_STATUS_ATTR = "processing.status"


class ProductManagementAgent:
    """
    Enhanced Product Management Agent with multiple specialized agents
    using the Agent2Agent (A2A) Protocol architecture
    """
    
    def __init__(self):
        self.kernel = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the enhanced product management agent with multiple specialized agents"""
        try:
            # region Kernel Configuration
            self.kernel = Kernel()
            
            # region Chat Service Configuration
            service_id = "azure_openai_chat"
            chat_service = AzureChatCompletion(
                service_id=service_id,
                deployment_name="gpt-4.1",
                endpoint="https://admin-mh2k31bc-eastus2.cognitiveservices.azure.com",
                api_key=os.getenv("gpt_api_key"),
                api_version="2024-12-01-preview"
            )
            
            self.kernel.add_service(chat_service)
            # endregion
            
            # region Plugin
            
            class ProductPlugin:
                """Retrieve data from Zava's product catalog.

                The Plugin is used by the `product_agent`.
                """

                @kernel_function(
                    description='Retrieves a set of products based on a natural language user query.'
                )
                def get_products(
                    self,
                    question: Annotated[
                        str, 'Natural language query to retrieve products, e.g. "What kinds of paint rollers do you have in stock?"'
                    ],
                ) -> list[dict[str, Any]]:
                    try:
                        # Simulate product retrieval based on the question
                        # In a real implementation, this would query a database or external service
                        product_dict = [
                            {
                                "id": "1",
                                "name": "Eco-Friendly Paint Roller",
                                "type": "Paint Roller",
                                "description": "A high-quality, eco-friendly paint roller for smooth finishes.",
                                "punchLine": "Roll with the best, paint with the rest!",
                                "price": 15.99
                            },
                            {
                                "id": "2",
                                "name": "Premium Paint Brush Set",
                                "type": "Paint Brush",
                                "description": "A set of premium paint brushes for detailed work and fine finishes.",
                                "punchLine": "Brush up your skills with our premium set!",
                                "price": 25.49
                            },
                            {
                                "id": "3",
                                "name": "All-Purpose Paint Tray",
                                "type": "Paint Tray",
                                "description": "A durable paint tray suitable for all types of rollers and brushes.",
                                "punchLine": "Tray it, paint it, love it!",
                                "price": 9.99
                            },
                            {
                                "id": "4",
                                "name": "Standard Paint Roller",
                                "type": "Paint Roller", 
                                "description": "A reliable paint roller for smooth and even paint application.",
                                "punchLine": "Standard quality, extraordinary results!",
                                "price": 12.99
                            },
                            {
                                "id": "5",
                                "name": "Professional Paint Sprayer",
                                "type": "Paint Sprayer",
                                "description": "Professional-grade paint sprayer for large projects and smooth finishes.",
                                "punchLine": "Spray your way to perfection!",
                                "price": 89.99
                            }
                        ]
                        return product_dict
                    except Exception as e:
                        return f'Product recommendation failed: {e!s}'

            # endregion
            
            # Define specialized agents
            
            # Define a MarketingAgent to handle marketing-related tasks
            marketing_agent = ChatCompletionAgent(
                service=chat_service,
                name='MarketingAgent',
                instructions=(
                    'You specialize in planning and recommending marketing strategies for products. '
                    'This includes identifying target audiences, making product descriptions better, and suggesting promotional tactics. '
                    'Your goal is to help businesses effectively market their products and reach their desired customers.'
                ),
            )

            # Define a RankerAgent to handle ranking-related tasks
            ranker_agent = ChatCompletionAgent(
                service=chat_service,
                name='RankerAgent',
                instructions=(
                    'You specialize in ranking and recommending products based on various criteria. '
                    'This includes analyzing product features, customer reviews, and market trends to provide tailored suggestions. '
                    'Your goal is to help customers find the best products for their needs.'
                ),
            )
            
            # Define a ProductAgent that uses the ProductPlugin
            product_agent = ChatCompletionAgent(
                service=chat_service,
                name='ProductAgent',
                instructions=(
                    'You specialize in handling product-related requests from customers and employees. '
                    'This includes providing a list of products, identifying available quantities, '
                    'providing product prices, and giving product descriptions as they exist in the product catalog. '
                    'Your goal is to assist customers promptly and accurately with all product-related inquiries.'
                ),
                plugins=[ProductPlugin()],
            )
            

            
            # Create the main Product Manager Agent that coordinates with all specialized agents
            self.agent = ChatCompletionAgent(
                service=chat_service,
                name='ProductManagerAgent',
                instructions=(
                    'You are the Zava Product Manager Agent, a central coordinator for all product-related inquiries. '
                    'You have access to specialized agents that can help with different aspects of product management:\n\n'
                    '1. ProductAgent: Use for product lookups, inventory checks, pricing, and catalog information\n'
                    '2. MarketingAgent: Use for creating better product descriptions, marketing strategies, and promotional content\n'
                    '3. RankerAgent: Use for product comparisons, recommendations, and ranking products based on criteria\n\n'
                    'When a customer asks a question, analyze their request and delegate to the appropriate agent:\n'
                    '- Product information queries → ProductAgent\n'
                    '- Improving descriptions or marketing → MarketingAgent\n'
                    '- Product comparisons or recommendations → RankerAgent\n\n'
                    'Always provide helpful, accurate, and friendly responses. If multiple agents could help, choose the most appropriate one or combine their expertise.'
                ),
                plugins=[product_agent, marketing_agent, ranker_agent]
            )
            
            logger.info("Enhanced Product Management Agent initialized successfully with multiple specialized agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced product management agent: {e}")
            raise
    
    async def process_message(self, message: str, conversation_history: list = None) -> str:
        """Process a user message using the enhanced multi-agent system with comprehensive observability"""
        with tracer.start_as_current_span("process_user_message") as span:
            try:
                # Set span attributes for observability
                span.set_attribute("message.length", len(message))
                span.set_attribute("message.content", message[:100])  # First 100 chars for debugging
                span.set_attribute("conversation.history_length", len(conversation_history) if conversation_history else 0)
                start_time = time.time()
                
                # Create chat history with tracing
                with tracer.start_as_current_span("create_chat_history") as history_span:
                    chat_history = ChatHistory()
                    
                    # Add conversation history if provided
                    if conversation_history:
                        history_span.set_attribute("history.entries_processed", len(conversation_history))
                        for entry in conversation_history:
                            if entry.get("role") == "user":
                                chat_history.add_user_message(entry.get("content", ""))
                            elif entry.get("role") == "assistant":
                                chat_history.add_assistant_message(entry.get("content", ""))
                    
                    # Add current user message
                    chat_history.add_user_message(message)
                
                # Process message with agent delegation tracing
                with tracer.start_as_current_span("agent_delegation") as delegation_span:
                    delegation_span.set_attribute("agent.type", "ProductManagerAgent")
                    delegation_span.set_attribute("agent.delegation_mode", "automatic")
                    
                    # Use the main agent to process the message
                    # The agent will automatically delegate to appropriate specialized agents
                    response_messages = []
                    message_count = 0
                    
                    async for response_msg in self.agent.invoke(chat_history):
                        response_messages.append(response_msg)
                        message_count += 1
                    
                    delegation_span.set_attribute("agent.response_messages_count", message_count)
                
                # Process and format response
                with tracer.start_as_current_span("format_response") as response_span:
                    if response_messages and len(response_messages) > 0:
                        # Get the last response from the agent
                        last_response = response_messages[-1]
                        if hasattr(last_response, 'content') and last_response.content:
                            final_response = str(last_response.content)
                        else:
                            final_response = str(last_response)
                        
                        response_span.set_attribute("response.length", len(final_response))
                        response_span.set_attribute("response.type", "success")
                        
                        # Log timing and metrics
                        processing_time = time.time() - start_time
                        span.set_attribute("processing.time_seconds", processing_time)
                        span.set_attribute(PROCESSING_STATUS_ATTR, "success")
                        
                        logger.info(f"Message processed successfully in {processing_time:.3f}s - Response length: {len(final_response)} chars")
                        return final_response
                    else:
                        no_response_msg = "No response generated from the agent system."
                        response_span.set_attribute("response.type", "empty")
                        span.set_attribute(PROCESSING_STATUS_ATTR, "no_response")
                        return no_response_msg
                
            except Exception as e:
                # Record exception in span
                span.record_exception(e)
                span.set_attribute(PROCESSING_STATUS_ATTR, "error")
                span.set_attribute("error.type", type(e).__name__)
                
                logger.error(f"Error processing message with enhanced agent: {e}", exc_info=True)
                error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again."
                return error_response


# Global instance
enhanced_product_manager = None

def get_enhanced_product_manager() -> ProductManagementAgent:
    """Get or create the global enhanced ProductManagementAgent instance"""
    global enhanced_product_manager
    if enhanced_product_manager is None:
        enhanced_product_manager = ProductManagementAgent()
    return enhanced_product_manager