from datetime import timedelta

from fastapi import APIRouter, Depends

from app.auth.basic import PermissionChecker
from app.auth.jwt import create_access_token
from app.internal.schemas import (
    GetUserAccessTokenRequest,
    GetUserByTelegramIdRequest,
    GetUserRequest,
    GetUsersCountResponse,
    GiveLicenseRequest,
    LinkTelegramUserRequest,
    UserAccessToken,
    GiveUserBalanceRequest,
)
from app.transactions.constants import PaymentCategory, PaymentMethod
from app.users import service as users_service
from app.users.exceptions import (
    UserNotFound,
    UserTelegramAlreadyExists,
    UserTelegramNotFound,
)
from app.users.schemas import UserSchema
from app.utils.schemas import APISuccess, create_response
from app.transactions import service as transactions_service

router = APIRouter(
    tags=["Internal"], dependencies=[Depends(PermissionChecker("admin"))]
)


@router.post("/internal.getUserAccessToken", response_model=APISuccess[UserAccessToken])
async def get_user_access_token(data: GetUserAccessTokenRequest):
    return create_response(
        UserAccessToken(
            access_token=create_access_token(data.user_id, timedelta(days=1))
        )
    )


# @router.post("/internal.createUserByTelegram", response_model=APISuccess[int])
# async def create_user_by_telegram(data: CreateUserByTelegramRequest):
#     user_telegram = await users_service.get_user_telegram_by_telegram_id(
#         data.telegram_id
#     )

#     if user_telegram:
#         raise UserTelegramAlreadyExists()

#     empty_user = await users_service.create_empty_user()

#     await users_service.create_user_telegram(
#         empty_user["id"], data.telegram_id, data.username
#     )

#     return create_response(empty_user["id"])


@router.post("/internal.getUserByTelegramId", response_model=APISuccess[UserSchema])
async def get_user_by_telegram_id(data: GetUserByTelegramIdRequest):
    user_telegram = await users_service.get_user_telegram_by_telegram_id(
        data.telegram_id
    )

    if not user_telegram:
        raise UserTelegramNotFound()

    user = await users_service.get_user_by_id(user_telegram["user_id"])

    if not user:
        raise UserNotFound()

    return create_response(user)


@router.post("/internal.linkTelegramAccount", response_model=APISuccess[None])
async def link_user(data: LinkTelegramUserRequest):
    user_telegram = await users_service.get_user_telegram_by_telegram_id(
        data.telegram_id
    )

    if user_telegram:
        raise UserTelegramAlreadyExists()

    await users_service.create_user_telegram(
        data.user_id, data.telegram_id, data.username
    )

    return create_response(None)


@router.post("/internal.getUsersTelegramIds", response_model=APISuccess[list[int]])
async def get_telegram_user_ids():
    users = await users_service.get_users_telegram_ids()

    return create_response([user["telegram_id"] for user in users])


@router.post("/internal.giveUserBalance", response_model=APISuccess[None])
async def give_user_balance(data: GiveUserBalanceRequest):
    await users_service.give_user_balance(data.user_id, data.amount)
    await transactions_service.create_transaction(
        {
            "amount": data.amount,
            "recipient_id": data.user_id,
            "category": PaymentCategory.REPLENISHMENT,
            "payment_method": PaymentMethod.SYSTEM,
            "payload": {},
        }
    )

    return create_response(None)


@router.post(
    "/internal.getUsersCount", response_model=APISuccess[GetUsersCountResponse]
)
async def get_users_count():
    return create_response(
        GetUsersCountResponse(
            users_count=await users_service.get_users_count(),
            users_telegram_count=await users_service.get_users_telegram_count(),
        )
    )


@router.post("/internal.getUser", response_model=APISuccess[UserSchema | None])
async def find_user(data: GetUserRequest):
    user = None

    if data.email:
        user = await users_service.get_user_by_email(data.email)
    elif data.username:
        user = await users_service.get_user_by_username(data.username)

    return create_response(user)


@router.post("/internal.giveLicense", response_model=APISuccess[None])
async def give_license(data: GiveLicenseRequest):
    await users_service.give_user_license(
        data.user_id, data.license_id, data.license_duration
    )

    return create_response(None)
