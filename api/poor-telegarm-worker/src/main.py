import asyncio

from pathlib import Path
from typing import Any

from src.bot import bot
from src.rabbitmq import rabbitmq
from src.sessions_hub import sessions_hub
from src.tasks.authorization import run as run_authorization
from src.tasks.first_messager import run as run_first_messager
from src.tasks.inviter import run as run_inviter
from src.tasks.mailer import run as run_mailer


async def create_task(session_id: str, type: str, data: Any):
    session = sessions_hub.get(session_id)

    if not session and type != "authorization":
        return False

    if type == "authorization":
        session = sessions_hub.add(session_id)

        session.create_task(
            "authorization",
            run_authorization,
            sessions=data["sessions"],
            proxies=data["proxies"],
        )

        return True

    coro = None

    if type == "mailer":
        coro = run_mailer
    elif type == "first_messager":
        coro = run_first_messager
    elif type == "inviter":
        coro = run_inviter

    if coro is None:
        return False

    session.create_task(type, coro, data)

    return True


async def get_task(session_id: str, type: str):
    session = sessions_hub.get(session_id)

    if not session:
        return False

    if type == "authorization":
        return True

    return True if session.get_task(type) else False


async def terminate_task(session_id: str, type: str):
    session = sessions_hub.get(session_id)

    if not session:
        return False

    if type == "authorization":
        session.close()

        await session.stop_clients(session.get_clients())

        sessions_hub.sessions.pop(session_id, None)

        return True

    session.cancel_task(type)

    return True


async def main():
    try:
        path = Path("/root/.richsmm/telegram/session")
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    await bot.set_default_administrator_rights(True)
    await bot.set_default_administrator_rights(False)

    async with rabbitmq:
        print("connected")

        if not rabbitmq.rpc:
            return

        await rabbitmq.rpc.register("telegram.createTask", create_task)
        await rabbitmq.rpc.register("telegram.getTask", get_task)
        await rabbitmq.rpc.register("telegram.terminateTask", terminate_task)

        try:
            await asyncio.Future()
        finally:
            pass


if __name__ == "__main__":
    asyncio.run(main())
