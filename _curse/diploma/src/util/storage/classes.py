import asyncio
import redis.asyncio as aioredis

from src.settings import RedisConfig
from src.util.storage.abstract import AbstractStorage


redis_config = RedisConfig()


class RedisHandler(AbstractStorage):
    def __init__(self):
        self.client = aioredis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db,
        )

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value, ex: int | None = None):
        await self.client.set(key, str(value), ex=ex)

    async def set_batch(self, key: str, values: list, ex: int | None = None):
        for value in values:
            await self.client.set(f'{key}:{value}', value, ex=ex)

    def get_pubsub(self):
        return self.client.pubsub()
