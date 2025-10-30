"""
Agent Executor for A2A Protocol
Handles the execution lifecycle of agent requests
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .product_management_agent import get_enhanced_product_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled" 
    FAILED = "failed"


class AgentExecutor:
    """
    Agent Executor implementation for A2A Protocol
    Responsible for processing requests and generating responses
    """
    
    def __init__(self):
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.product_manager = get_enhanced_product_manager()
        
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent request
        
        Args:
            request: The agent request containing message and context
            
        Returns:
            Dict containing execution result
        """
        execution_id = str(uuid.uuid4())
        
        # Initialize execution tracking
        self.executions[execution_id] = {
            "id": execution_id,
            "status": ExecutionStatus.PENDING,
            "request": request,
            "result": None,
            "error": None,
            "start_time": datetime.utcnow(),
            "end_time": None
        }
        
        try:
            logger.info(f"Starting execution {execution_id}")
            
            # Update status to running
            self.executions[execution_id]["status"] = ExecutionStatus.RUNNING
            
            # Extract message from request
            message = request.get("message", "")
            
            if not message:
                raise ValueError("Message is required")
            
            # Process the message using the Enhanced Product Manager
            response = await self.product_manager.process_message(message)
            
            # Prepare the result
            result = {
                "execution_id": execution_id,
                "response": response,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "agent_type": "product_manager"
            }
            
            # Update execution status
            self.executions[execution_id].update({
                "status": ExecutionStatus.COMPLETED,
                "result": result,
                "end_time": datetime.utcnow()
            })
            
            logger.info(f"Execution {execution_id} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            logger.error(f"Execution {execution_id} failed: {error_msg}")
            
            # Update execution status with error
            self.executions[execution_id].update({
                "status": ExecutionStatus.FAILED,
                "error": error_msg,
                "end_time": datetime.utcnow()
            })
            
            return {
                "execution_id": execution_id,
                "response": f"I apologize, but I encountered an error processing your request: {error_msg}",
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "agent_type": "product_manager",
                "error": error_msg
            }
    
    async def cancel(self, execution_id: str) -> Dict[str, Any]:
        """
        Cancel a running execution
        
        Args:
            execution_id: The ID of the execution to cancel
            
        Returns:
            Dict containing cancellation result
        """
        if execution_id not in self.executions:
            return {
                "execution_id": execution_id,
                "status": "error",
                "message": "Execution not found"
            }
        
        execution = self.executions[execution_id]
        
        if execution["status"] in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
            return {
                "execution_id": execution_id,
                "status": "error",
                "message": f"Execution already {execution['status'].value}"
            }
        
        # Update status to cancelled
        execution.update({
            "status": ExecutionStatus.CANCELLED,
            "end_time": datetime.utcnow()
        })
        
        logger.info(f"Execution {execution_id} cancelled")
        
        return {
            "execution_id": execution_id,
            "status": "cancelled",
            "message": "Execution cancelled successfully"
        }
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of an execution
        
        Args:
            execution_id: The ID of the execution
            
        Returns:
            Dict containing execution status
        """
        if execution_id not in self.executions:
            return {
                "execution_id": execution_id,
                "status": "error",
                "message": "Execution not found"
            }
        
        execution = self.executions[execution_id]
        
        return {
            "execution_id": execution_id,
            "status": execution["status"].value,
            "start_time": execution["start_time"].isoformat() if execution["start_time"] else None,
            "end_time": execution["end_time"].isoformat() if execution["end_time"] else None,
            "result": execution.get("result"),
            "error": execution.get("error")
        }
    
    def list_executions(self) -> List[Dict[str, Any]]:
        """
        List all executions
        
        Returns:
            List of execution summaries
        """
        return [
            {
                "execution_id": execution_id,
                "status": execution["status"].value,
                "start_time": execution["start_time"].isoformat() if execution["start_time"] else None,
                "end_time": execution["end_time"].isoformat() if execution["end_time"] else None
            }
            for execution_id, execution in self.executions.items()
        ]


# Global instance
agent_executor = None

def get_agent_executor() -> AgentExecutor:
    """Get or create the global AgentExecutor instance"""
    global agent_executor
    if agent_executor is None:
        agent_executor = AgentExecutor()
    return agent_executor