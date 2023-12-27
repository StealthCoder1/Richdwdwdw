from enum import StrEnum, auto


class ProductType(StrEnum):
    LICENSE = auto()


class ErrorCode:
    PRODUCT_NOT_FOUND = "product not found"
    INSUFFICIENT_FUNDS = "insufficient funds"


class LicenseIds(StrEnum):
    TELEGRAM = auto()
