from enum import StrEnum, auto


class PaymentStatus(StrEnum):
    PENDING = auto()
    SUCCESS = auto()
    ERROR = auto()


class PaymentCategory(StrEnum):
    REPLENISHMENT = auto()
    PURCHASE = auto()


class PaymentMethod(StrEnum):
    UNKNOWN = auto()
    BALANCE = auto()
    SYSTEM = auto()
