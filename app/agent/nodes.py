"""
app/agent/nodes.py (Updated for Step 8)
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from sqlmodel import Session

from app.agent.state import SupportAgentState, TriageOutput
from app.tools.order_tools import fetch_order_details, process_refund, update_shipping_address
from app.database import engine
from app.models import ReviewTicket

load_dotenv()



llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0
)

tools = [fetch_order_details, process_refund, update_shipping_address]
llm_with_tools = llm.bind_tools(tools)


def triage_node(state: SupportAgentState) -> Dict[str, Any]:
    """Node 1: Analyzes user message to extract intent, sentiment, order ID, and urgency."""
    messages = state["messages"]
    last_user_message = messages[-1].content

    structured_llm = llm.with_structured_output(TriageOutput)
    triage_result: TriageOutput = structured_llm.invoke(last_user_message)

    return {
        "intent_data": triage_result
    }


def policy_guardrail_node(state: SupportAgentState) -> Dict[str, Any]:
    """
    Node 2: Policy Rules + SQLite Review Ticket Creation.
    """
    triage = state.get("intent_data")
    if not triage:
        return {"policy_passed": False, "requires_human_review": True}

    requires_review = False
    review_reason = ""

    # Rule 1: High urgency or angry sentiment
    if triage.sentiment == "ANGRY" or triage.urgency == "CRITICAL":
        requires_review = True
        review_reason = f"Customer sentiment is {triage.sentiment} with {triage.urgency} urgency."

    # Rule 2: Refund over $100 threshold check
    elif triage.intent in ["INITIATE_REFUND", "CANCEL_ORDER"] and triage.order_id:
        order_info = fetch_order_details.invoke({"order_id": triage.order_id})
        if order_info.get("success"):
            amount = order_info["order"]["amount"]
            if amount > 100.00:
                requires_review = True
                review_reason = f"Requested refund amount (${amount}) exceeds auto-approval limit ($100.00)."

    if requires_review:
        # Persist review ticket to SQLite database
        with Session(engine) as session:
            ticket = ReviewTicket(
                thread_id="session_active",  # Dynamic thread mapping in production
                order_id=triage.order_id,
                customer_intent=triage.intent,
                reason=review_reason,
                status="PENDING"
            )
            session.add(ticket)
            session.commit()

        return {
            "policy_passed": False,
            "requires_human_review": True,
            "tool_outputs": [{"system_note": review_reason}]
        }

    return {
        "policy_passed": True,
        "requires_human_review": False
    }


def execution_node(state: SupportAgentState) -> Dict[str, Any]:
    """Node 3: Executes tool calls or generates final response."""
    messages = state["messages"]
    system_prompt = SystemMessage(
        content=(
            "You are an empathetic customer support agent. "
            "Use the provided tools to lookup orders, issue refunds, or update addresses when needed. "
            "If a tool operation succeeds or fails, clearly explain the result to the customer."
        )
    )
    full_prompt = [system_prompt] + messages
    response = llm_with_tools.invoke(full_prompt)

    return {
        "messages": [response]
    }