import asyncio

import aiofiles

from src.constants import LogLevel, Messages
from src.custom_client import CustomClient
from src.session_reader import SessionReader
from src.sessions_hub import SessionTask
from src.utils import format_additional_error_info


async def pool(task: SessionTask, client: CustomClient):
    await task.increase_counter("sent")

    try:
        await client.start()

        # new_client = await client.qr_login_to_new_client()

        # try:
        #     await client.stop()
        # except Exception:
        #     pass

        # await client.storage.open()

        # await client.set_storage(
        #     await new_client.storage.dc_id(),
        #     await new_client.storage.api_id(),
        #     await new_client.storage.test_mode(),
        #     await new_client.storage.auth_key(),
        #     await new_client.storage.user_id(),
        #     await new_client.storage.is_bot(),
        #     await new_client.storage.date(),
        # )

        # try:
        #     await new_client.stop()
        # except Exception:
        #     pass

        # await client.start(False)

        await task.increase_counter("success")
        await task.send_log(LogLevel.INFO, Messages.ACCOUNT_CONNECTED)
    except Exception as exception:
        print(exception)

        try:
            await client.stop()
        except Exception:
            pass

        await task.increase_counter("error")
        await task.send_log(
            LogLevel.ERROR,
            Messages.LOGIN_ERROR.format(format_additional_error_info(exception)),
        )


async def run(task: SessionTask, sessions: list[str], proxies: list[str]):
    # await asyncio.sleep(0.5)

    session_reader = SessionReader()

    await session_reader.read_sessions_from_files(sessions)

    lines: list[str] = []

    for proxy_file_path in proxies:
        async with aiofiles.open(proxy_file_path) as file:
            lines.extend(
                ["socks5://" + line.rstrip() for line in await file.readlines()]
            )

    task.session.set_proxies(lines)

    for auth_key, dc_id in session_reader.sessions:
        client = await task.session.create_client(task, auth_key, dc_id)

        if client:
            task.session.clients[auth_key] = client

    clients, proxies = task.get_session_clients(), task.get_session_proxies()

    async with task.lock_counters:
        task.counters.update(
            {"sessions": len(clients), "proxies": len(proxies), "sent": 0}
        )

    await task.send_counters()
    await task.session.send_data(
        "authorization", "accounts", session_reader.get_sessions()
    )
    await task.session.send_data("authorization", "proxies", lines)

    await asyncio.gather(*[pool(task, client) for client in clients])

    new_clients = {}

    for auth_key in task.session.clients:
        client = task.session.clients[auth_key]

        if client.is_connected:
            new_clients[auth_key] = client

    task.session.clients = new_clients
