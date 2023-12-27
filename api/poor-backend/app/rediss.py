from redis.asyncio import ConnectionPool, Redis


class _Redis:
    def __init__(self):
        pass

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, *args):
        await self.disconnect()

    async def connect(self):
        self.pool = ConnectionPool.from_url(
            "redis://:8e0a3cd3-9a4e-4c09-abae-da9a92214ef5@103.113.71.89",
            decode_responses=True,
        )

        self.client = Redis(connection_pool=self.pool, decode_responses=True)

    async def disconnect(self):
        await self.pool.disconnect()


redis = _Redis()
