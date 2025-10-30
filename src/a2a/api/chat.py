"""
Chat API router for the A2A Product Manager agent
Handles chat requests and interfaces with the agent executor
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..agent.executor import get_agent_executor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["chat"])

# Global agent executor (will be initialized on first use)
agent_executor = None

def get_or_create_agent_executor():
    """Get the agent executor, creating it if necessary"""
    global agent_executor
    if agent_executor is None:
        agent_executor = get_agent_executor()
    return agent_executor


class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="The user message")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    response: str = Field(..., description="The agent's response")
    execution_id: str = Field(..., description="The execution ID for tracking")
    status: str = Field(..., description="The execution status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


@router.post("/chat/message", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the Product Manager agent
    
    Args:
        request: Chat request containing message and optional metadata
        
    Returns:
        ChatResponse with agent's response and execution details
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        # Prepare execution request
        execution_request = {
            "message": request.message,
            "conversation_id": request.conversation_id or request.session_id,
            "metadata": request.metadata or {}
        }
        
        # Execute the request
        executor = get_or_create_agent_executor()
        result = await executor.execute(execution_request)
        
        # Extract response from result
        if result.get("status") == "success":
            # The response is directly in the result
            response_text = result.get("response", "")
        else:
            response_text = result.get("error", "An error occurred during processing")
        
        return ChatResponse(
            response=response_text,
            execution_id=result.get("execution_id", ""),
            status="completed" if result.get("status") == "success" else result.get("status", "unknown"),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get("/chat/status/{execution_id}")
async def get_chat_status(execution_id: str):
    """
    Get the status of a chat execution
    
    Args:
        execution_id: The execution ID to check
        
    Returns:
        Execution status information
    """
    try:
        executor = get_or_create_agent_executor()
        result = executor.get_execution_status(execution_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail="Execution not found")
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Status retrieval failed: {str(e)}"
        )


@router.post("/chat/cancel/{execution_id}")
async def cancel_chat_execution(execution_id: str):
    """
    Cancel a running chat execution
    
    Args:
        execution_id: The execution ID to cancel
        
    Returns:
        Cancellation result
    """
    try:
        executor = get_or_create_agent_executor()
        result = await executor.cancel(execution_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Cancellation failed"))
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling chat execution: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cancellation failed: {str(e)}"
        )


@router.get("/chat/executions")
async def list_chat_executions():
    """
    List all chat executions
    
    Returns:
        List of execution summaries
    """
    try:
        executor = get_or_create_agent_executor()
        executions = executor.list_executions()
        return {"executions": executions}
        
    except Exception as e:
        logger.error(f"Error listing chat executions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Listing executions failed: {str(e)}"
        )


@router.get("/chat/agent-info")
async def get_agent_info():
    """
    Get information about the Product Manager agent
    
    Returns:
        Agent capabilities and information
    """
    return {
        "agent_id": "zava-product-manager",
        "name": "Zava Product Manager",
        "description": "A specialized agent for managing Zava product information, recommendations, and enhanced descriptions",
        "version": "1.0.0",
        "capabilities": [
            "Product Information Retrieval",
            "Product Recommendations", 
            "Enhanced Product Descriptions",
            "Inventory Queries",
            "Customer Support"
        ],
        "supported_languages": ["en"],
        "response_formats": ["text", "json"]
    }