"""
app/models.py
Database tables for Orders and Human-in-the-Loop Review Tickets using SQLModel.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    """Database model storing customer orders."""
    order_id: str = Field(primary_key=True, index=True)
    customer_name: str
    item_name: str
    amount: float
    status: str = Field(default="PROCESSING")  # PROCESSING, SHIPPED, DELIVERED, REFUNDED, CANCELLED
    order_date: str
    shipping_address: str
    return_eligible: bool = Field(default=True)

class ReviewTicket(SQLModel, table=True):
    """Database model for Human-in-the-Loop pending approvals."""
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True)
    order_id: Optional[str] = Field(default=None)
    customer_intent: str
    reason: str
    status: str = Field(default="PENDING")  # PENDING, APPROVED, REJECTED
    created_at: datetime = Field(default_factory=datetime.utcnow)