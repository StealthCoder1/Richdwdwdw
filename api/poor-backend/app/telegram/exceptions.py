from app.exceptions import BadRequest
from app.telegram.constants import ErrorCode


class ProxiesAreNotLoaded(BadRequest):
    DETAIL = ErrorCode.PROXIES_ARE_NOT_LOADED


class AccountsAreNotLoaded(BadRequest):
    DETAIL = ErrorCode.ACCOUNTS_ARE_NOT_LOADED


class TaskIsAlreadyRunning(BadRequest):
    DETAIL = ErrorCode.TASK_IS_ALREADY_RUNNING


class SessionNotFound(BadRequest):
    DETAIL = ErrorCode.SESSION_NOT_FOUND


class NoLicense(BadRequest):
    DETAIL = ErrorCode.NO_LICENSE
