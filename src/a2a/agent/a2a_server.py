"""
A2A Server implementation
Acts as a wrapper for the FastAPI application and handles A2A Protocol
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import httpx

from .executor import get_agent_executor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AServer:
    """
    A2A Server implementation
    Responsible for initializing the application, defining the Agent Executor,
    and defining Agent Cards that describe the agents
    """
    
    def __init__(self, httpx_client: httpx.AsyncClient, host: str = "0.0.0.0", port: int = 8001):
        self.httpx_client = httpx_client
        self.host = host
        self.port = port
        self.agent_executor = get_agent_executor()
        self._app = None
        
        # Initialize the Starlette app
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize the Starlette application with A2A routes"""
        routes = [
            Route("/agent-card", self._get_agent_card_endpoint, methods=["GET"]),
            Route("/execute", self._execute_endpoint, methods=["POST"]),
            Route("/cancel/{execution_id}", self._cancel_endpoint, methods=["POST"]),
            Route("/status/{execution_id}", self._status_endpoint, methods=["GET"]),
            Route("/executions", self._list_executions_endpoint, methods=["GET"]),
            Route("/health", self._health_endpoint, methods=["GET"]),
        ]
        
        self._app = Starlette(routes=routes)
    
    def get_starlette_app(self) -> Starlette:
        """Get the Starlette application instance"""
        return self._app
    
    def _get_agent_card(self) -> Dict[str, Any]:
        """
        Get the Agent Card that describes this agent's capabilities
        
        Returns:
            Dict containing agent card information
        """
        return {
            "agent_id": "zava-product-manager",
            "name": "Zava Product Manager",
            "description": "A specialized agent for managing Zava product information, recommendations, and enhanced descriptions using Semantic Kernel",
            "version": "1.0.0",
            "capabilities": [
                {
                    "name": "product_information",
                    "description": "Retrieve detailed information about specific products",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "User message asking about product information"
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "product_recommendations", 
                    "description": "Provide product recommendations based on customer needs and budget",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "User message describing their needs"
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "enhance_descriptions",
                    "description": "Create enhanced, marketing-friendly product descriptions",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Request to enhance product description"
                            }
                        },
                        "required": ["message"]
                    }
                }
            ],
            "endpoints": {
                "execute": f"http://{self.host}:{self.port}/a2a/execute",
                "cancel": f"http://{self.host}:{self.port}/a2a/cancel/{{execution_id}}",
                "status": f"http://{self.host}:{self.port}/a2a/status/{{execution_id}}",
                "agent_card": f"http://{self.host}:{self.port}/a2a/agent-card"
            },
            "protocols": ["A2A-v1.0"],
            "supported_message_types": ["text"],
            "created_at": datetime.utcnow().isoformat(),
            "contact": {
                "maintainer": "Zava Development Team",
                "email": "dev@zava.com"
            }
        }
    
    async def _get_agent_card_endpoint(self, request):
        """Agent card endpoint"""
        try:
            agent_card = self._get_agent_card()
            return JSONResponse(agent_card)
        except Exception as e:
            logger.error(f"Error getting agent card: {e}")
            return JSONResponse(
                {"error": "Failed to retrieve agent card"},
                status_code=500
            )
    
    async def _execute_endpoint(self, request):
        """Execute agent request endpoint"""
        try:
            body = await request.json()
            
            # Validate required fields
            if "message" not in body:
                return JSONResponse(
                    {"error": "Message is required"},
                    status_code=400
                )
            
            # Execute the request
            result = await self.agent_executor.execute(body)
            
            return JSONResponse(result)
            
        except Exception as e:
            logger.error(f"Error executing request: {e}")
            return JSONResponse(
                {"error": f"Execution failed: {str(e)}"},
                status_code=500
            )
    
    async def _cancel_endpoint(self, request):
        """Cancel execution endpoint"""
        try:
            execution_id = request.path_params["execution_id"]
            result = await self.agent_executor.cancel(execution_id)
            
            status_code = 200 if result.get("status") != "error" else 400
            return JSONResponse(result, status_code=status_code)
            
        except Exception as e:
            logger.error(f"Error cancelling execution: {e}")
            return JSONResponse(
                {"error": f"Cancel failed: {str(e)}"},
                status_code=500
            )
    
    async def _status_endpoint(self, request):
        """Get execution status endpoint"""
        try:
            execution_id = request.path_params["execution_id"]
            result = self.agent_executor.get_execution_status(execution_id)
            
            status_code = 200 if result.get("status") != "error" else 404
            return JSONResponse(result, status_code=status_code)
            
        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return JSONResponse(
                {"error": f"Status retrieval failed: {str(e)}"},
                status_code=500
            )
    
    async def _list_executions_endpoint(self, request):
        """List all executions endpoint"""
        try:
            result = self.agent_executor.list_executions()
            return JSONResponse({"executions": result})
            
        except Exception as e:
            logger.error(f"Error listing executions: {e}")
            return JSONResponse(
                {"error": f"Listing executions failed: {str(e)}"},
                status_code=500
            )
    
    async def _health_endpoint(self, request):
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": "zava-product-manager",
            "version": "1.0.0"
        })