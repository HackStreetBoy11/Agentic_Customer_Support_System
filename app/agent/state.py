"""
app/agent/state.py
Central State Definition for Customer Support Agentic Workflow.
"""

from typing import Annotated, TypedDict, List, Optional, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class TriageOutput(BaseModel):
    """Structured output schema returned by the Intent & Triage Agent."""
    intent: str = Field(
        description="Detected user intent (e.g., ORDER_STATUS, INITIATE_REFUND, ADDRESS_CHANGE, GENERAL_FAQ, ESCALATE)"
    )
    confidence: float = Field(
        description="Confidence score of intent detection between 0.0 and 1.0"
    )
    order_id: Optional[str] = Field(
        default=None,
        description="Extracted Order ID if present (e.g., ORD-12345)"
    )
    urgency: str = Field(
        default="NORMAL",
        description="Urgency level: LOW, NORMAL, HIGH, CRITICAL"
    )
    sentiment: str = Field(
        default="NEUTRAL",
        description="Customer emotional state: CALM, FRUSTRATED, ANGRY"
    )

class SupportAgentState(TypedDict):
    """
    The main Graph State object tracking conversation history, intent,
    verification status, and tool execution outputs across the workflow.
    """
    # Conversation history with automatic appending reducer
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Structured Intent metadata from Triage Agent
    intent_data: Optional[TriageOutput]
    
    # State flags for control routing
    user_authenticated: bool
    policy_passed: bool
    requires_human_review: bool
    
    # Tool execution results (e.g., retrieved DB records, API outputs)
    tool_outputs: List[dict[str, Any]]