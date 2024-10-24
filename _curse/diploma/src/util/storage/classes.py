from redis import Redis

from src.settings import RedisConfig


class RedisHandler:
    def __init__(self):
        self.client = Redis(
            host=RedisConfig.host,
            port=RedisConfig.port,
            db=RedisConfig.db,
        )

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value, ex: int | None = None):
        self.client.set(key, str(value), ex=ex)

    def set_batch(self, key: str, values: list, ex: int | None = None):
        for value in values:
            self.client.set(f'{key}:{value}', value, ex=ex)
