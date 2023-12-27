from app.exceptions import BadRequest, NotFound
from app.products.constants import ErrorCode


class ProductNotFound(NotFound):
    DETAIL = ErrorCode.PRODUCT_NOT_FOUND


class InsufficientFunds(BadRequest):
    DETAIL = ErrorCode.INSUFFICIENT_FUNDS
