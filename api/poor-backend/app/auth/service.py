from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, insert, select

from app.auth.config import auth_config
from app.auth.exceptions import InvalidCredentials
from app.auth.models import RefreshToken
from app.auth.schemas import SignInRequest, SignUpRequest
from app.auth.security import check_password, hash_password
from app.database import execute, fetch_one
from app.users import service as users_service
from app.users.exceptions import UserNotFound
from app.users.models import User


async def create_user(data: SignUpRequest):
    insert_query = (
        insert(User)
        .values(
            {
                "email": data.email,
                "username": data.username,
                "password": hash_password(data.password),
            }
        )
        .returning(User)
    )

    return await fetch_one(insert_query)


async def authenticate_user(data: SignInRequest):
    user = await users_service.get_user_by_username(data.username)

    if not user:
        raise UserNotFound()

    if not check_password(data.password, user["password"]):
        raise InvalidCredentials()

    return user


async def create_refresh_token(user_id: int):
    refresh_token = str(uuid4())

    insert_query = insert(RefreshToken).values(
        {
            "refresh_token": refresh_token,
            "user_id": user_id,
            "expires_at": datetime.utcnow()
            + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        }
    )

    await execute(insert_query)

    return refresh_token


async def get_refresh_token(refresh_token: str):
    select_query = select(RefreshToken).where(
        RefreshToken.refresh_token == refresh_token
    )

    return await fetch_one(select_query)


async def expire_refresh_token(refresh_token: str):
    delete_query = delete(RefreshToken).where(
        RefreshToken.refresh_token == refresh_token
    )

    await execute(delete_query)
