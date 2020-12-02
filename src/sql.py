from typing import Optional

import asyncpg
from loguru import logger

from utils.singleton import MetaSingleton


class psql(metaclass=MetaSingleton):  # noqa
    __slots__ = ("_pool",)

    def __init__(self):
        self._pool: Optional[asyncpg.pool.Pool] = None

    @property
    def pool(self):
        if self._pool is not None:
            return self._pool
        else:
            raise AttributeError("Postgres._pool is not defined!")

    async def connect(self, dsn: str):
        self._pool = await asyncpg.create_pool(dsn)
        logger.info("Postgres connection established")

    async def add_guild(self, guild_id: int):
        await self.pool.execute("INSERT INTO guilds(guild_id) VALUES($1) ON CONFLICT DO NOTHING;", guild_id)
