import asyncio
import time

from functools import partial
from itertools import cycle
from typing import Any, Callable

from pyrogram.errors import Unauthorized
from opentele.td import API

from src.constants import LogLevel, Messages
from src.custom_client import CustomClient
from src.utils import parse_proxy, sha256
from src.rabbitmq import rabbitmq


def on_pyrogram_task_done(
    loop: asyncio.AbstractEventLoop, context: dict[Any, Any], client: CustomClient
):
    # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_exception_handler
    print(context, loop)

    if isinstance(context, Unauthorized):
        asyncio.create_task(client.stop())


class Account:
    id: int | None
    avatar: str | None
    first_name: str | None
    last_name: str | None
    spamblock: bool | None

    client: CustomClient


class SessionTask:
    task: asyncio.Task[Any]

    def __init__(self, session: "Session") -> None:
        self.session = session

        self.lock_counters = asyncio.Lock()
        self.counters: dict[str, int] = {"success": 0, "error": 0}

        self.lock_storage = asyncio.Lock()
        self.storage = {}

    def on_done_callback(self, task: asyncio.Task[Any]):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as exception:
            print("on_done_callback, exception", task, exception)

    def get_session_clients(self):
        return self.session.get_clients()

    def get_session_proxies(self):
        return self.session.proxies

    async def increase_counter(self, name: str):
        async with self.lock_counters:
            self.counters[name] = self.counters.get(name, 0) + 1

        await self.send_counters()

    async def send_log(self, level: LogLevel, text: str):
        await self.session.send_data(
            self.get_name(),
            "log",
            dict(level=level.upper(), time=int(time.time()), text=text),
        )

    async def send_counters(self):
        await self.session.send_data(self.get_name(), "counters", self.counters)

    def get_name(self):
        return self.task.get_name()

    def cancel(self):
        self.task.cancel()


class Session:
    def __init__(self, session_id: str) -> None:
        self.id = session_id
        self.lock_clients: asyncio.Lock = asyncio.Lock()
        self.clients: dict[bytes, CustomClient] = {}
        self.accounts: set[Account] = set()
        self.proxies: list[str] = []
        self.tasks: set[SessionTask] = set()
        self.proxies_cycle: "cycle[str]" = cycle([])

    async def send_data(self, task: str, type: str, data: Any):
        print(task, type, data)

        await rabbitmq.send_message(
            rabbitmq.api_exchange,
            dict(
                action="telegram.data",
                data={
                    "session_id": self.id,
                    "task": task,
                    "type": type,
                    "data": data,
                },
            ),
            routing_key="api",
        )

    def get_clients(self):
        return [self.clients[auth_key] for auth_key in self.clients]

    def create_task(
        self,
        name: str,
        coro: Callable[..., Any],
        *args: tuple[Any],
        **kwargs: dict[str, Any]
    ):
        session_task = SessionTask(self)

        session_task.task = asyncio.create_task(
            partial(coro, session_task)(*args, **kwargs), name=name
        )

        self.tasks.add(session_task)

        return name

    def close(self):
        for task in self.tasks:
            task.cancel()

    def get_task(self, name: str):
        for task in self.tasks:
            if task.task.get_name() == name:
                return task

        return None

    def cancel_task(self, name: str):
        task = self.get_task(name)

        if not task:
            return

        task.cancel()

        self.tasks.remove(task)

    def get_proxy(self):
        proxy = next(self.proxies_cycle, None)

        return parse_proxy(proxy) if proxy else None

    def set_proxies(self, proxies: list[str]):
        self.proxies = proxies
        self.proxies_cycle = cycle(proxies)

    async def create_client(self, task: SessionTask, auth_key: bytes, dc_id: int):
        application = API.TelegramIOS.Generate(auth_key.hex())

        proxy = self.get_proxy()

        if not proxy:
            return None

        print(proxy)

        client = CustomClient(
            sha256(auth_key),
            application.api_id,
            application.api_hash,
            application.app_version,
            application.device_model,
            application.system_version,
            application.lang_code,
            proxy=proxy,
            workdir="/root/.richsmm/telegram/session",
        )

        client.lang_pack = application.lang_pack

        await client.storage.open()

        if not await client.storage.auth_key():  # storage_auth_key == auth_key
            await client.set_storage(
                dc_id, application.api_id, False, auth_key, 999999, False, 0
            )

            await client.storage.save()

        client.loop.set_exception_handler(partial(on_pyrogram_task_done, client=client))

        @client.on_disconnect()
        async def _(_):
            await task.send_log(LogLevel.DEBUG, Messages.RECONNECTING_ACCOUNT)

            proxy = self.get_proxy()

            if proxy:
                client.proxy = proxy

        return client

    async def stop_client(self, client: CustomClient):
        try:
            await client.stop()
        except Exception as exception:
            print(exception)

    async def stop_clients(self, clients: list[CustomClient]):
        await asyncio.gather(
            *[self.stop_client(client) for client in clients if client.is_connected]
        )


class SessionsHub:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = dict()

    def get(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def add(self, session_id: str) -> Session:
        if session_id in self.sessions:
            raise KeyError()

        session = Session(session_id)

        self.sessions[session_id] = session

        return session


sessions_hub = SessionsHub()
