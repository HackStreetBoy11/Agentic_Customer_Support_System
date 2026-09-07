"""
main.py (Updated with Admin & DB Initialization for Step 8)
"""

import json
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import HumanMessage
from sqlmodel import Session, select

from app.database import init_db, engine, get_session
from app.models import ReviewTicket, Order
from app.tools.order_tools import process_refund
from app.agent.graph import app_graph


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI(
    title="Autonomous Customer Support Agentic API",
    description="Production-grade LangGraph Agent for Automated E-Commerce Customer Support.",
    version="1.0.0"
)
# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_ui():
    """Serves the single-page web UI."""
    return FileResponse("app/static/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize SQLite database and seed test data on launch."""
    init_db()


class ChatRequest(BaseModel):
    message: str = Field(description="The customer input query.")
    thread_id: str = Field(default="session_default", description="Unique session ID.")


class AdminActionRequest(BaseModel):
    action: str = Field(description="Action choice: 'APPROVE' or 'REJECT'")


@app.get("/")
async def health_check():
    return {"status": "online", "service": "Agentic Customer Support Workflow"}


async def event_generator(request_data: ChatRequest) -> AsyncGenerator[str, None]:
    """Streams LangGraph node updates over SSE."""
    config = {"configurable": {"thread_id": request_data.thread_id}}
    inputs = {"messages": [HumanMessage(content=request_data.message)]}

    try:
        for event in app_graph.stream(inputs, config=config):
            for node_name, node_state in event.items():
                payload = {"node": node_name, "content": ""}
                if "messages" in node_state and node_state["messages"]:
                    last_msg = node_state["messages"][-1]
                    payload["content"] = getattr(last_msg, "content", str(last_msg))

                yield json.dumps(payload)
                await asyncio.sleep(0.05)

    except Exception as e:
        yield json.dumps({"error": str(e)})


@app.post("/api/v1/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    return EventSourceResponse(event_generator(request))


# ---------------------------------------------------------------------------
# Admin & Human-in-the-Loop Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/v1/admin/tickets")
def list_pending_tickets(session: Session = Depends(get_session)):
    """Retrieves all pending human-review tickets."""
    tickets = session.exec(select(ReviewTicket).where(ReviewTicket.status == "PENDING")).all()
    return {"success": True, "tickets": tickets}


@app.post("/api/v1/admin/tickets/{ticket_id}/action")
def resolve_ticket(
    ticket_id: int, 
    action_req: AdminActionRequest, 
    session: Session = Depends(get_session)
):
    """Processes manager approval/rejection for held requests."""
    ticket = session.get(ReviewTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Review ticket not found.")

    if ticket.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Ticket already resolved as {ticket.status}.")

    action = action_req.action.upper()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE' or 'REJECT'.")

    ticket.status = action
    session.add(ticket)

    result_message = f"Ticket {ticket_id} marked as {action}."

    # If manager approves refund request, execute refund tool in DB
    if action == "APPROVE" and ticket.order_id:
        refund_res = process_refund.invoke({
            "order_id": ticket.order_id, 
            "reason": f"Approved by admin review ticket #{ticket_id}"
        })
        result_message += f" Refund result: {refund_res.get('message', refund_res.get('error'))}"

    session.commit()
    return {"success": True, "message": result_message}