from sqlalchemy import insert
from app.database import fetch_one
from app.transactions.constants import PaymentMethod, PaymentStatus
from app.transactions.models import Transaction


async def create_transaction(values: dict):
    insert_query = insert(Transaction).values(values)

    return await fetch_one(insert_query)


async def get_transaction_by_id():
    pass


async def get_transactions_by_recipient_id():
    pass
