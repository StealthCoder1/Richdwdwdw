from typing import Any

import msgspec

from aio_pika import ExchangeType, connect_robust, Message
from aio_pika.patterns import Master, RPC
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractChannel,
    AbstractExchange,
)


class RabbitMQ:
    connection: AbstractRobustConnection | None = None
    channel: AbstractChannel | None = None
    exchange: AbstractExchange | None = None
    master: Master | None = None
    rpc: RPC | None = None

    def __init__(self, url: str):
        self.url = url

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, *_):
        await self.disconnect()

    async def connect(self):
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange("main")
        self.master = Master(self.channel)
        self.rpc = await RPC.create(self.channel)

        self.api_exchange = await self.channel.declare_exchange(
            "api", ExchangeType.FANOUT
        )

    async def disconnect(self):
        if self.channel:
            await self.channel.close()

        if self.connection:
            await self.connection.close()

    async def send_message(
        self, exchange: AbstractExchange, messages: Any, routing_key: str
    ):
        if type(messages) != "list":
            messages = [messages]

        for message in messages:
            await exchange.publish(
                Message(msgspec.msgpack.encode(message)),
                routing_key,
            )


rabbitmq = RabbitMQ("amqp://admin:ca84ab58-47d6-4268-b8f3-acb6fd68ed6e@103.113.71.89/")
