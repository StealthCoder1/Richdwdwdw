from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.auth.config import auth_config
from app.exceptions import Unauthorized

security = HTTPBasic(auto_error=False)


def parse_basic_credentials(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(security)]
) -> HTTPBasicCredentials:
    if not credentials:
        raise Unauthorized()

    return credentials


class PermissionChecker:
    def __init__(self, username: str):
        self.username = username

    def __call__(
        self,
        credentials: Annotated[HTTPBasicCredentials, Depends(parse_basic_credentials)],
    ):
        # TODO: Timing Attack

        if (
            credentials.username != "admin"
            or credentials.password != auth_config.ADMIN_PASSWORD
        ):
            raise Unauthorized()
