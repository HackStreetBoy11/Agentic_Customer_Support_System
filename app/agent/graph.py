"""
app/agent/graph.py
LangGraph Stateful Graph Workflow Assembly.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import SupportAgentState
from app.agent.nodes import triage_node, policy_guardrail_node, execution_node
from app.tools.order_tools import fetch_order_details, process_refund, update_shipping_address


# ---------------------------------------------------------------------------
# 1. Instantiate Graph with Central State
# ---------------------------------------------------------------------------
builder = StateGraph(SupportAgentState)


# ---------------------------------------------------------------------------
# 2. Add Nodes to Graph
# ---------------------------------------------------------------------------
builder.add_node("triage", triage_node)
builder.add_node("policy_check", policy_guardrail_node)
builder.add_node("execution", execution_node)

# Built-in LangGraph Tool Execution Node for automatic tool handling
tools = [fetch_order_details, process_refund, update_shipping_address]
builder.add_node("tools", ToolNode(tools))


# ---------------------------------------------------------------------------
# 3. Define Conditional Routing Functions (Edges)
# ---------------------------------------------------------------------------
def route_after_policy(state: SupportAgentState) -> Literal["execution", "human_review_node"]:
    """Routes to human review if policy flagged it, otherwise proceeds to execution."""
    if state.get("requires_human_review"):
        return "human_review_node"
    return "execution"


def human_review_node(state: SupportAgentState):
    """Fallback Node when human approval is required."""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": "Your request exceeds our automated threshold or requires manager verification. I have routed your ticket to a human support agent."
            }
        ]
    }

builder.add_node("human_review_node", human_review_node)


# ---------------------------------------------------------------------------
# 4. Connect Edges & Flow Control
# ---------------------------------------------------------------------------
# Entry point: START -> Triage
builder.add_edge(START, "triage")

# Triage -> Policy Guardrail
builder.add_edge("triage", "policy_check")

# Policy Check -> Conditional Edge (Human Review OR Execution)
builder.add_conditional_edges(
    "policy_check",
    route_after_policy,
    {
        "human_review_node": "human_review_node",
        "execution": "execution"
    }
)

# Execution -> Conditional Edge for Tool Calling Loop
# If Gemini requests a tool, route to "tools", else END
builder.add_conditional_edges("execution", tools_condition)

# Tools -> Execution (Loop back to summarize tool output to user)
builder.add_edge("tools", "execution")

# End paths
builder.add_edge("human_review_node", END)


# ---------------------------------------------------------------------------
# 5. Compile Graph with In-Memory Checkpointer (For State Persistence)
# ---------------------------------------------------------------------------
checkpointer = MemorySaver()
app_graph = builder.compile(checkpointer=checkpointer)