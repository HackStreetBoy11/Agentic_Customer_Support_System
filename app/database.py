"""
app/database.py
Database setup, session management, and initial data seeding.
"""

from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Order

SQLITE_FILE_NAME = "support.db"
DATABASE_URL = f"sqlite:///{SQLITE_FILE_NAME}"


# Make sure 'engine' is defined HERE at the top level (outside any function):
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """Creates database tables and seeds initial mock orders if empty."""
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Check if database is already seeded
        existing_order = session.exec(select(Order)).first()
        if not existing_order:
            print("Seeding initial order data into SQLite database...")
            initial_orders = [
                Order(
                    order_id="ORD-8821",
                    customer_name="Jane Doe",
                    item_name="Mechanical Keyboard",
                    amount=89.99,
                    status="PROCESSING",
                    order_date="2026-08-29",
                    shipping_address="123 Tech Street, Haldwani, Uttarakhand",
                    return_eligible=True
                ),
                Order(
                    order_id="ORD-9940",
                    customer_name="John Doe",
                    item_name="Gaming Monitor 27-inch",
                    amount=349.50,
                    status="PROCESSING",  # Set to PROCESSING so policy guardrail can test $100 threshold
                    order_date="2026-08-15",
                    shipping_address="45 Park Avenue, Delhi",
                    return_eligible=True
                ),
                Order(
                    order_id="ORD-1102",
                    customer_name="Alice Smith",
                    item_name="Wireless Mouse",
                    amount=25.00,
                    status="DELIVERED",
                    order_date="2026-08-28",
                    shipping_address="78 Hill Road, Dehradun",
                    return_eligible=True
                )
            ]
            for order in initial_orders:
                session.add(order)
            session.commit()
            print("Database seeding completed successfully.")


def get_session():
    """Dependency provider for database sessions."""
    with Session(engine) as session:
        yield session