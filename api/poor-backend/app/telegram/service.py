import aiofiles
import msgspec
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database import fetch_all
from app.rabbitmq import rabbitmq
from app.rediss import redis
from app.tasks import service as tasks_service
from app.telegram.exceptions import (
    AccountsAreNotLoaded,
    ProxiesAreNotLoaded,
    SessionNotFound,
    TaskIsAlreadyRunning,
)
from app.telegram.models import TelegramAccount
from app.proxies import service as proxies_service
from app.telegram.schemas import (
    CreateAuthorizationTask,
    CreateFirstMessagerTask,
    CreateInviterTask,
    CreateMailerTask,
    MessagesBlock,
)
from app.websocket.connection_manager import manager


async def save_files(files: list[UploadFile]) -> dict:
    result: dict[str, str] = {}

    if not files:
        return []

    for file in files:
        if file.filename == "":
            continue

        async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as f:
            while chunk := await file.read(52428800):  # 50 MB
                await f.write(chunk)

        result[file.filename] = f.name

    return result


async def handle_create_task(
    task: CreateAuthorizationTask
    | CreateInviterTask
    | CreateMailerTask
    | CreateFirstMessagerTask,
    files: list[UploadFile],
    user_id: int,
) -> None:
    session_id = str(user_id)

    r_task = await get_task(session_id, str(task.type))

    if r_task:
        raise TaskIsAlreadyRunning()

    data = task.data

    files: dict[str, str] = await save_files(files)

    if isinstance(task, CreateAuthorizationTask):
        sessions, proxies = [], []

        for filename in data.sessions:
            if filename in files:
                sessions.append(files[filename])

        for filename in data.proxies:
            if filename in files:
                proxies.append(files[filename])

        if len(sessions) == 0:
            raise AccountsAreNotLoaded()
        elif len(proxies) == 0:
            raise ProxiesAreNotLoaded()

        await rabbitmq.rpc.call(
            "telegram.createTask",
            dict(
                session_id=session_id,
                type=str(task.type),
                data=dict(sessions=sessions, proxies=proxies),
            ),
        )

        return

    a_task = await get_task(session_id, "authorization")

    if not a_task:
        raise SessionNotFound()

    if isinstance(task, (CreateMailerTask, CreateFirstMessagerTask)):
        task.data.chat_ids = task.data.chat_ids

        for item in data.config.items:
            if not isinstance(item, MessagesBlock):
                continue

            for message in item.messages:
                if not message.media:
                    continue

                message.media.type = str(message.media.type)

                message.media.filename = files.get(message.media.filename, None)

                if message.media.filename is None:
                    message.media = None

    if isinstance(task, CreateInviterTask):
        task.data.chat_id = task.data.chat_id
        task.data.user_ids = task.data.user_ids

    await rabbitmq.rpc.call(
        "telegram.createTask",
        dict(session_id=session_id, type=str(task.type), data=task.data.model_dump()),
    )


async def get_task(session_id: str, task_type: str):
    return await rabbitmq.rpc.call(
        "telegram.getTask", dict(session_id=session_id, type=task_type)
    )


async def get_accounts_by_auth_key(auth_keys: list[bytes]):
    select_query = select(TelegramAccount).where(
        TelegramAccount.auth_key.in_(auth_keys)
    )

    return await fetch_all(select_query)


async def create_accounts(accounts: dict):
    insert_query = (
        insert(TelegramAccount)
        .values(accounts)
        .on_conflict_do_nothing()
        .returning(TelegramAccount)
    )

    return await fetch_all(insert_query)


async def on_data(data):
    user_id = int(data["session_id"])

    for client in manager.clients:
        if client.user_id != int(user_id):
            continue

        if data["type"] == "proxies":
            await proxies_service.upload_proxies(data["data"])

            return

        if data["type"] == "accounts":
            await converted_accounts(data["data"])

            return

        await client.send_event(
            "data",
            dict(
                service="telegram",
                task=data["task"],
                type=data["type"],
                data=data["data"],
            ),
        )


async def on_task_completed(data):
    await tasks_service.set_task_status(data["task_id"], "completed")

    task = await tasks_service.get_task(data["task_id"])

    if not task:
        return

    if task.name == "convertAccounts":
        await converted_accounts(task, data["data"])


async def converted_accounts(data: list[str]):
    parsed = []

    for string in data:
        parts = string.split(":")

        parsed.append({"auth_key": bytes.fromhex(parts[0]), "dc_id": int(parts[1])})

    db_accounts = await get_accounts_by_auth_key([x["auth_key"] for x in parsed])

    to_insert = []

    for account in parsed:
        exists = next(
            (x for x in db_accounts if x["auth_key"] == account["auth_key"]), None
        )

        if not exists:
            to_insert.append(account)

    if len(to_insert):
        db_accounts.extend(await create_accounts(to_insert))
