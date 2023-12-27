from typing import Any

import msgspec
from aio_pika import Message, connect_robust
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
)
from aio_pika.patterns import RPC, Master


class RabbitMQ:
    connection: AbstractRobustConnection | None = None
    channel: AbstractRobustChannel | None = None
    exchange: AbstractRobustExchange | None = None
    master: Master | None = None
    rpc: RPC | None = None

    def __init__(self, url: str):
        self.url = url

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, *args):
        await self.disconnect()

    async def connect(self):
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange("main")
        self.master = Master(self.channel)
        self.rpc = await RPC.create(self.channel)

    async def disconnect(self):
        await self.rpc.close()
        await self.channel.close()
        await self.connection.close()

    async def send_message(self, messages: Any, routing_key: str):
        if type(messages) != "list":
            messages = [messages]

        for message in messages:
            await self.exchange.publish(
                Message(msgspec.msgpack.encode(message)),
                routing_key,
            )


rabbitmq = RabbitMQ("amqp://guest:guest@127.0.0.1/")
