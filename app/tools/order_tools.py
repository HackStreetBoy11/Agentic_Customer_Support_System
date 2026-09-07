"""
app/tools/order_tools.py
LangChain Tools executing queries directly against SQLite database tables.
"""

from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.database import engine
from app.models import Order


class OrderLookupInput(BaseModel):
    order_id: str = Field(description="The unique Order ID to look up, e.g., 'ORD-8821'")

class RefundInput(BaseModel):
    order_id: str = Field(description="The Order ID to issue a refund for.")
    reason: str = Field(description="Detailed reason for initiating the refund.")

class AddressUpdateInput(BaseModel):
    order_id: str = Field(description="The Order ID to update shipping address for.")
    new_address: str = Field(description="The new target shipping address.")


@tool("fetch_order_details", args_schema=OrderLookupInput)
def fetch_order_details(order_id: str) -> Dict[str, Any]:
    """Retrieves order details, status, and shipping information from the SQL database."""
    formatted_id = order_id.strip().upper()
    if not formatted_id.startswith("ORD-") and formatted_id.isdigit():
        formatted_id = f"ORD-{formatted_id}"

    with Session(engine) as session:
        order = session.get(Order, formatted_id)
        if not order:
            return {"success": False, "error": f"Order ID '{order_id}' not found in database."}
        
        return {
            "success": True,
            "order": {
                "order_id": order.order_id,
                "customer_name": order.customer_name,
                "item_name": order.item_name,
                "amount": order.amount,
                "status": order.status,
                "order_date": order.order_date,
                "shipping_address": order.shipping_address,
                "return_eligible": order.return_eligible
            }
        }


@tool("process_refund", args_schema=RefundInput)
def process_refund(order_id: str, reason: str) -> Dict[str, Any]:
    """Processes a refund for a valid order directly in the SQL database."""
    formatted_id = order_id.strip().upper()

    with Session(engine) as session:
        order = session.get(Order, formatted_id)
        if not order:
            return {"success": False, "error": f"Cannot refund: Order '{order_id}' not found."}

        if order.status == "REFUNDED":
            return {"success": False, "error": f"Order '{formatted_id}' has already been refunded."}

        if order.status == "SHIPPED":
            return {
                "success": False, 
                "error": "Order is already in transit (SHIPPED). Customer must receive item first or request return label."
            }

        # Update SQL record status
        order.status = "REFUNDED"
        session.add(order)
        session.commit()
        session.refresh(order)

        return {
            "success": True,
            "message": f"Successfully refunded ${order.amount} for order {formatted_id}.",
            "refunded_amount": order.amount,
            "reason": reason
        }


@tool("update_shipping_address", args_schema=AddressUpdateInput)
def update_shipping_address(order_id: str, new_address: str) -> Dict[str, Any]:
    """Updates the delivery address for an order in SQL database if not shipped."""
    formatted_id = order_id.strip().upper()

    with Session(engine) as session:
        order = session.get(Order, formatted_id)
        if not order:
            return {"success": False, "error": f"Order '{order_id}' not found."}

        if order.status in ["SHIPPED", "DELIVERED"]:
            return {
                "success": False, 
                "error": f"Cannot update address. Order '{formatted_id}' is already {order.status}."
            }

        order.shipping_address = new_address
        session.add(order)
        session.commit()

        return {
            "success": True,
            "message": f"Shipping address for order {formatted_id} updated to: {new_address}"
        }