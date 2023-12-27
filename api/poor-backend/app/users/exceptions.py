from app.exceptions import BadRequest, NotFound
from app.users.constants import ErrorCode


class UserNotFound(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND


class UserTelegramAlreadyExists(BadRequest):
    DETAIL = ErrorCode.USER_TELEGRAM_ALREADY_EXISTS


class UserTelegramNotFound(BadRequest):
    DETAIL = ErrorCode.USER_TELEGRAM_NOT_FOUND
