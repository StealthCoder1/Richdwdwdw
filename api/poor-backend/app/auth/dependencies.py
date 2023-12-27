from datetime import datetime
from typing import Any

from fastapi import Cookie, Depends

from app.auth import service
from app.auth.exceptions import EmailTaken, InvalidRefreshToken, UsernameTaken
from app.auth.schemas import SignUpRequest
from app.users import service as users_service
from app.users.exceptions import UserNotFound


async def valid_user_create(data: SignUpRequest) -> SignUpRequest:
    if await users_service.get_user_by_username(data.username):
        raise UsernameTaken()

    if await users_service.get_user_by_email(data.email):
        raise EmailTaken()

    return data


async def valid_refresh_token(refresh_token: str = Cookie()):
    db_refresh_token = await service.get_refresh_token(refresh_token)

    if not db_refresh_token:
        raise InvalidRefreshToken()

    if not datetime.utcnow() <= db_refresh_token["expires_at"]:
        raise InvalidRefreshToken()

    return db_refresh_token


async def valid_refresh_token_user(
    refresh_token: dict[str, Any] = Depends(valid_refresh_token)
) -> dict[str, Any]:
    user = await users_service.get_user_by_id(refresh_token["user_id"])

    if not user:
        raise UserNotFound()

    return user
