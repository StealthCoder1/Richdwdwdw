from enum import StrEnum, auto

from pydantic import BaseModel


class PaymentSystem(StrEnum):
    QIWI = auto()


class CreateInvoice(BaseModel):
    payment_system: PaymentSystem
    amount: int


class Invoice(BaseModel):
    invoice_url: str
