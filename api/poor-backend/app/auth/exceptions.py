from app.auth.constants import ErrorCode
from app.exceptions import BadRequest, Forbidden, Unauthorized


class IncorrectPassword(Forbidden):
    DETAIL = ErrorCode.INCORRECT_PASSWORD


class UsernameTaken(BadRequest):
    DETAIL = ErrorCode.USERNAME_TAKEN


class EmailTaken(BadRequest):
    DETAIL = ErrorCode.EMAIL_TAKEN


class InvalidCredentials(Unauthorized):
    DETAIL = ErrorCode.INVALID_CREDENTIALS


class InvalidRefreshToken(Unauthorized):
    DETAIL = ErrorCode.INVALID_REFRESH_TOKEN


class InvalidAccessToken(Unauthorized):
    DETAIL = ErrorCode.INVALID_ACCESS_TOKEN
