from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt

from app.auth.config import auth_config
from app.auth.exceptions import InvalidAccessToken
from app.auth.schemas import JWTUserData
from app.exceptions import Unauthorized
from app.users import service as users_service
from app.users.exceptions import UserNotFound
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", auto_error=False)


def create_access_token(
    user_id: str | int,
    expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
    data = {"sub": str(user_id), "exp": datetime.utcnow() + expires_delta}

    return jwt.encode(data, auth_config.JWT_SECRET, auth_config.JWT_ALG)


def parse_jwt_user_data_optional(
    access_token: Annotated[str, Depends(oauth2_scheme)]
) -> JWTUserData | None:
    if not access_token:
        return None

    try:
        payload = jwt.decode(
            access_token, auth_config.JWT_SECRET, algorithms=auth_config.JWT_ALG
        )
    except JWTError:
        raise InvalidAccessToken()

    return JWTUserData(**payload)


def parse_jwt_user_data(
    jwt_user_data: Annotated[JWTUserData | None, Depends(parse_jwt_user_data_optional)]
) -> JWTUserData:
    if not jwt_user_data:
        raise Unauthorized()

    return jwt_user_data


async def get_current_user(
    jwt_user_data: Annotated[JWTUserData, Depends(parse_jwt_user_data)]
) -> User:
    user = await users_service.get_user_by_id(jwt_user_data.user_id)

    if not user:
        return UserNotFound()

    return user


UserDependency = Annotated[User, Depends(get_current_user)]
JWTUserDataDependency = Annotated[JWTUserData, Depends(parse_jwt_user_data)]
