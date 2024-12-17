import asyncio
import redis.asyncio as aioredis

from src.settings import RedisConfig
from src.util.storage.abstract import AbstractStorage


class RedisHandler(AbstractStorage):
    def __init__(self):
        self.client = aioredis.Redis(
            host=RedisConfig.host,
            port=RedisConfig.port,
            db=RedisConfig.db,
        )

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value, ex: int | None = None):
        await self.client.set(key, str(value), ex=ex)

    def set_batch(self, key: str, values: list, ex: int | None = None):
        for value in values:
            self.client.set(f'{key}:{value}', value, ex=ex)

    def get_pubsub(self):
        return self.client.pubsub()
