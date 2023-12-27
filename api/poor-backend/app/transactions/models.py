from sqlalchemy import (
    Column,
    Enum,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base
from app.transactions.constants import PaymentCategory, PaymentMethod, PaymentStatus


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, default="")
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.SUCCESS)
    category = Column(Enum(PaymentCategory), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payload = Column(JSONB, nullable=False)
