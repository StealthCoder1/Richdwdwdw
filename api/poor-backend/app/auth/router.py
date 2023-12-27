from typing import Any

from fastapi import APIRouter, Depends, Response

from app.auth import jwt, service
from app.auth.dependencies import (
    valid_refresh_token,
    valid_refresh_token_user,
    valid_user_create,
)
from app.auth.schemas import AccessTokenResponse, SignInRequest, SignUpRequest
from app.auth.utils import get_refresh_token_cookie
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Auth"])


@router.post("/auth.signUp", response_model=APISuccess[AccessTokenResponse])
async def sign_up(response: Response, data: SignUpRequest = Depends(valid_user_create)):
    user = await service.create_user(data)
    refresh_token = await service.create_refresh_token(user["id"])

    response.set_cookie(**get_refresh_token_cookie(refresh_token))

    return create_response(
        AccessTokenResponse(
            access_token=jwt.create_access_token(user["id"]),
            refresh_token=refresh_token,
        )
    )


@router.post("/auth.signIn", response_model=APISuccess[AccessTokenResponse])
async def sign_in(data: SignInRequest, response: Response):
    user = await service.authenticate_user(data)
    refresh_token = await service.create_refresh_token(user["id"])

    response.set_cookie(**get_refresh_token_cookie(refresh_token))

    return create_response(
        AccessTokenResponse(
            access_token=jwt.create_access_token(user["id"]),
            refresh_token=refresh_token,
        )
    )


@router.post("/auth.refreshToken", response_model=APISuccess[AccessTokenResponse])
async def refresh_token(
    response: Response,
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
    user: dict[str, Any] = Depends(valid_refresh_token_user),
) -> APISuccess[AccessTokenResponse]:
    new_refresh_token = await service.create_refresh_token(user["id"])

    response.set_cookie(**get_refresh_token_cookie(new_refresh_token))

    await service.expire_refresh_token(refresh_token["refresh_token"])

    return create_response(
        AccessTokenResponse(
            access_token=jwt.create_access_token(user["id"]),
            refresh_token=new_refresh_token,
        )
    )


@router.post("/auth.logout", response_model=APISuccess[None])
async def logout():
    pass
