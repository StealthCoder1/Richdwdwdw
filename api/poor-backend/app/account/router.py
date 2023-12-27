from random import randint
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi_mail import MessageSchema, MessageType

from app.account.exceptions import IncorrectEmailCode
from app.account.schemas import (
    ConfirmEmailRequest,
    SendConfirmEmailCodeRequest,
    SendConfirmEmailCodeResponse,
)
from app.auth.jwt import JWTUserDataDependency, UserDependency, parse_jwt_user_data
from app.fastmail import fastmail
from app.rediss import redis
from app.users import service as users_service
from app.users.schemas import UserSchema
from app.utils.aes import AESCipher
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Account"], dependencies=[Depends(parse_jwt_user_data)])


@router.post("/account.getMe", response_model=APISuccess[UserSchema])
async def get_me(user: UserDependency):
    return create_response(user)


@router.post("/account.getLicenses", response_model=APISuccess[Any])
async def get_licenses(jwt_user_data: JWTUserDataDependency):
    return create_response(await users_service.get_user_licenses(jwt_user_data.user_id))


@router.post(
    "/account.sendConfirmEmailCode",
    response_model=APISuccess[SendConfirmEmailCodeResponse],
)
async def send_confirm_email_code(
    data: SendConfirmEmailCodeRequest,
    background_tasks: BackgroundTasks,
    user: UserDependency,
):
    key = f"email:{user['email']}:{data.purpose}"

    ttl = await redis.client.ttl(key)

    if ttl != -2:
        return create_response({"ttl": ttl, "sent": False})

    code = randint(100000, 999999)

    message = MessageSchema(
        subject="Проверочный код RichSMM",
        recipients=[user["email"]],
        body=f"Проверочный код: {code}. Пожалуйста, не разглашайте информацию другим лицам.",
        subtype=MessageType.html,
    )

    background_tasks.add_task(fastmail.send_message, message)

    await redis.client.set(key, code, ex=60)

    return create_response({"ttl": 60, "sent": True})


@router.post("/account.confirmEmail", response_model=APISuccess[bool])
async def confirm_email(data: ConfirmEmailRequest, user: UserDependency):
    key = f"email:{user['email']}:registration"

    redis_code = await redis.client.get(key)

    if data.code != redis_code:
        raise IncorrectEmailCode()

    await redis.client.delete(key)
    await users_service.update_user_by_id(user["id"], {"is_email_confirmed": True})

    return create_response(True)


@router.post("/account.getTelegramBotLink", response_model=APISuccess[str])
async def get_telegram_bot_link(jwt_user_data: JWTUserDataDependency):
    aes_cipher = AESCipher("32141df1-f267-42b7-92de-16075d8d271e")

    bot_username = "RichSmmSofts_bot"
    start = aes_cipher.encrypt(f"a:{jwt_user_data.user_id}", True).decode()

    return create_response(f"https://t.me/{bot_username}?start={start}")


@router.post("/account.unlinkTelegramAccount", response_model=APISuccess[None])
async def unlink_telegram_account(jwt_user_data: JWTUserDataDependency):
    await users_service.delete_user_telegram_by_user_id(jwt_user_data.user_id)

    return create_response(None)
