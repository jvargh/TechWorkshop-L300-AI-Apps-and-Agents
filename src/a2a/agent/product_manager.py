"""
Product Management Agent for A2A Protocol
This agent handles product-related queries using Semantic Kernel
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent, AuthorRole
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductManager:
    """Product Management Agent using Semantic Kernel"""
    
    def __init__(self):
        self.kernel = None
        self._initialize_kernel()
        
    def _initialize_kernel(self):
        """Initialize the Semantic Kernel with Azure OpenAI"""
        try:
            # Create kernel
            self.kernel = Kernel()
            
            # Add Azure OpenAI Chat Completion service
            service_id = "azure_openai_chat"
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id=service_id,
                    deployment_name=os.getenv("gpt_deployment", "gpt-4.1"),
                    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
                )
            )
            
            # Add product management functions
            self._add_product_functions()
            
            logger.info("Semantic Kernel initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Semantic Kernel: {e}")
            raise
    
    def _add_product_functions(self):
        """Add product management functions to the kernel"""
        
        @kernel_function(
            name="get_product_info",
            description="Get detailed information about a specific product"
        )
        def get_product_info(product_name: str) -> str:
            """Get product information"""
            # This would typically query a database or API
            # For demo purposes, return mock data
            product_db = {
                "standard paint roller": {
                    "name": "Standard Paint Roller",
                    "price": "$12.99",
                    "description": "A reliable paint roller for smooth and even paint application.",
                    "category": "Painting Tools",
                    "in_stock": True,
                    "features": ["9-inch roller", "Synthetic cover", "Ergonomic handle"]
                },
                "premium paint roller": {
                    "name": "Premium Paint Roller",
                    "price": "$24.99", 
                    "description": "Professional-grade paint roller with superior finish quality.",
                    "category": "Painting Tools",
                    "in_stock": True,
                    "features": ["12-inch roller", "Microfiber cover", "Anti-slip grip"]
                }
            }
            
            product_key = product_name.lower()
            if product_key in product_db:
                product = product_db[product_key]
                return f"""
Product: {product['name']}
Price: {product['price']}
Description: {product['description']}
Category: {product['category']}
In Stock: {'Yes' if product['in_stock'] else 'No'}
Features: {', '.join(product['features'])}
"""
            else:
                return f"Product '{product_name}' not found in our catalog."
        
        @kernel_function(
            name="recommend_products", 
            description="Recommend products based on customer preferences and budget"
        )
        def recommend_products(need: str, budget: str = "medium") -> str:
            """Recommend products based on needs"""
            recommendations = {
                "painting": [
                    "Standard Paint Roller - $12.99 (Great for beginners)",
                    "Premium Paint Roller - $24.99 (Professional quality)",
                    "Paint Brush Set - $19.99 (For detailed work)",
                    "Drop Cloth - $8.99 (Protect your floors)"
                ],
                "kitchen": [
                    "Kitchen Paint (Heat Resistant) - $34.99",
                    "Cabinet Hardware - $15.99",
                    "LED Under-Cabinet Lighting - $45.99"
                ]
            }
            
            need_key = need.lower()
            for key in recommendations:
                if key in need_key:
                    products = recommendations[key]
                    if budget.lower() == "low":
                        products = products[:2]  # Show fewer options for low budget
                    
                    return f"Here are my recommendations for {need}:\n" + "\n".join(f"• {product}" for product in products)
            
            return f"I'd be happy to help with recommendations for {need}. Could you provide more specific details about what you're looking for?"
        
        @kernel_function(
            name="enhance_product_description",
            description="Create enhanced, marketing-friendly product descriptions"
        )
        def enhance_product_description(product_name: str, current_description: str = "") -> str:
            """Enhance product descriptions with marketing appeal"""
            
            enhanced_descriptions = {
                "standard paint roller": """
🎨 **Transform Your Space with the Standard Paint Roller**

Discover the perfect balance of quality and affordability! Our Standard Paint Roller is designed for DIY enthusiasts and professionals alike who demand reliable performance without breaking the bank.

✨ **Key Benefits:**
• **Smooth Application**: 9-inch synthetic cover ensures even paint distribution
• **Comfortable Grip**: Ergonomic handle reduces hand fatigue during extended use
• **Versatile**: Perfect for walls, ceilings, and large surfaces
• **Easy Cleanup**: Synthetic materials wash clean with soap and water

💡 **Perfect For**: First-time painters, weekend warriors, and budget-conscious professionals

**Why Choose Our Standard Paint Roller?**
Don't let its affordable price fool you – this roller delivers professional results every time. Whether you're refreshing a single room or tackling a whole house project, our Standard Paint Roller is your reliable partner for beautiful, streak-free finishes.

*Make every stroke count. Choose quality. Choose Standard.*
""",
                "premium paint roller": """
🏆 **Elevate Your Craft with the Premium Paint Roller**

Step into the professional league with our Premium Paint Roller – where superior engineering meets exceptional results. Designed for those who accept nothing less than perfection.

✨ **Premium Features:**
• **Professional Grade**: 12-inch microfiber cover for flawless finish
• **Advanced Grip Technology**: Anti-slip handle ensures perfect control
• **Superior Coverage**: Wider roller reduces application time by 25%
• **Durability**: Built to withstand hundreds of projects

🎯 **Perfect For**: Professional contractors, serious DIYers, and quality perfectionists

**The Premium Difference:**
When your reputation depends on results, choose the roller that professionals trust. Our Premium Paint Roller doesn't just apply paint – it delivers masterpieces. Every stroke is smoother, every finish more professional, every project a testament to your skill.

*Because excellence isn't an accident. It's a choice.*
"""
            }
            
            product_key = product_name.lower()
            if product_key in enhanced_descriptions:
                return enhanced_descriptions[product_key]
            else:
                return f"Enhanced description for {product_name}: A high-quality product designed to meet your needs with excellent performance and reliability. Contact us for more details!"
        
        # Add functions to kernel
        self.kernel.add_function(
            plugin_name="ProductManager",
            function=get_product_info
        )
        self.kernel.add_function(
            plugin_name="ProductManager", 
            function=recommend_products
        )
        self.kernel.add_function(
            plugin_name="ProductManager",
            function=enhance_product_description
        )
    
    async def process_message(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Process a user message and return a response"""
        try:
            # Create chat history
            chat_history = ChatHistory()
            
            # Add conversation history if provided
            if conversation_history:
                for entry in conversation_history:
                    role = AuthorRole.USER if entry.get("role") == "user" else AuthorRole.ASSISTANT
                    chat_history.add_message(ChatMessageContent(
                        role=role,
                        content=entry.get("content", "")
                    ))
            
            # Add system message to set context
            system_message = """You are a helpful Product Management Assistant for Zava, a home improvement store. 
You have access to product information, can make recommendations, and can enhance product descriptions.

Use the available functions when appropriate:
- get_product_info: When users ask about specific products
- recommend_products: When users need product suggestions
- enhance_product_description: When users want improved product descriptions

Always be helpful, friendly, and focused on providing value to customers."""

            chat_history.add_system_message(system_message)
            
            # Add current user message
            chat_history.add_user_message(message)
            
            # Get chat completion service
            chat_completion = self.kernel.get_service(type=AzureChatCompletion)
            
            # Generate response using the kernel with function calling
            response = await chat_completion.get_chat_message_content(
                chat_history=chat_history,
                kernel=self.kernel
            )
            
            return str(response.content) if response and response.content else "No response generated"
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again."


# Global instance
product_manager = None

def get_product_manager() -> ProductManager:
    """Get or create the global ProductManager instance"""
    global product_manager
    if product_manager is None:
        product_manager = ProductManager()
    return product_manager