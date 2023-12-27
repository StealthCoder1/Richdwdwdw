import time
from typing import Any

from sqlalchemy import delete, func, insert, select, update

from app.database import execute, fetch_all, fetch_one
from app.users.models import User, UserLicense, UserTelegram


async def get_users() -> list[dict[str, Any]]:
    select_query = select(User)

    return await fetch_all(select_query)


async def get_user_by_id(id: int) -> dict[str, Any] | None:
    select_query = select(User).where(User.id == id)

    return await fetch_one(select_query)


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    select_query = select(User).where(User.email == email)

    return await fetch_one(select_query)


async def get_user_by_username(username: str) -> dict[str, Any] | None:
    select_query = select(User).where(User.username == username)

    return await fetch_one(select_query)


async def get_user_telegram_by_telegram_id(telegram_id: int) -> dict[str, Any] | None:
    select_query = select(UserTelegram).where(UserTelegram.telegram_id == telegram_id)

    return await fetch_one(select_query)


async def delete_user_telegram_by_user_id(user_id: int):
    delete_query = delete(UserTelegram).where(UserTelegram.user_id == user_id)

    return await execute(delete_query)


async def update_user_by_id(id: int, values: Any):
    update_query = update(User).where(User.id == id).values(values)

    return await execute(update_query)


async def create_user_telegram(user_id: int, telegram_id: int, username: str | None):
    insert_query = (
        insert(UserTelegram)
        .values({"user_id": user_id, "telegram_id": telegram_id, "username": username})
        .returning(UserTelegram.id)
    )

    return await fetch_one(insert_query)


async def get_user_licenses(user_id: int):
    select_query = select(UserLicense).where(UserLicense.user_id == user_id)

    return await fetch_all(select_query)

async def get_users_telegram_ids():
    select_query = select(UserTelegram.telegram_id)

    return await fetch_all(select_query)


async def take_user_balance(user_id: int, amount: int):
    await execute(
        update(User)
        .where(User.id == user_id)
        .values({"balance": User.balance - amount})
    )

async def give_user_balance(user_id: int, amount: int):
    await execute(
        update(User)
        .where(User.id == user_id)
        .values({"balance": User.balance + amount})
    )

async def get_users_count():
    select_query = select(func.count()).select_from(User)

    return (await execute(select_query)).scalar()

async def get_users_telegram_count():
    select_query = select(func.count()).select_from(UserTelegram)

    return (await execute(select_query)).scalar()

async def give_user_license(user_id: int, license_id: str, license_duration: int):
    license_user = await fetch_one(
        select(UserLicense).where(
            UserLicense.user_id == user_id, UserLicense.license_id == license_id
        )
    )

    current_time = int(time.time())

    if license_user:
        await execute(
            update(UserLicense)
            .where(UserLicense.user_id == user_id, UserLicense.license_id == license_id)
            .values(
                {
                    "expires_at": max(license_user["expires_at"], current_time)
                    + license_duration
                }
            )
        )
    else:
        await execute(
            insert(UserLicense).values(
                {
                    "user_id": user_id,
                    "license_id": license_id,
                    "expires_at": current_time + license_duration,
                }
            )
        )
