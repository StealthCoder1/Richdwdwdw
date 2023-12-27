from app.account.constants import ErrorCode
from app.exceptions import BadRequest


class IncorrectEmailCode(BadRequest):
    DETAIL = ErrorCode.INCORRECT_EMAIL_CODE
