from typing import Optional

import aioredis
import orjson
from loguru import logger

from src.exceptions import CacheException, CacheMiss
from src.singleton import MetaSingleton
from src.decos import executor
from src.storage import InternalStorage
from src.types import GuildSettings
from utils.sql import psql

SETTINGS_PREFIX = "S-"  # S-{GUILD}


class cachemanager(metaclass=MetaSingleton):
    def __init__(self) -> None:
        self.storage = InternalStorage()
        self._redis: Optional[aioredis.Redis] = None

    async def connect_redis(self, uri: str):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(uri, encoding="utf-8")
            logger.info("Redis connection pool created")

        elif isinstance(self._redis, aioredis.Redis):
            raise CacheException(
                "You have to destroy previously create Redis connection first before creating a new one!"
            ) from None

    @property
    def redis(self):
        return self._redis

    async def get(self, guild_id: int) -> GuildSettings:
        exists = await self.redis.exists(f"{SETTINGS_PREFIX}{guild_id}")
        if not exists:
            try:
                await self.refresh(guild_id)
            except CacheException as e:
                raise CacheMiss(*e.args) from None

        jsonified = await self.redis.get(f"{SETTINGS_PREFIX}{guild_id}")

        # must run orjson in the executor since non-async
        aioloads = executor(lambda: orjson.loads(jsonified))
        data = await aioloads()
        return GuildSettings(**data)

    async def refresh(self, guild_id: int):
        query = "SELECT * FROM guilds WHERE guild_id = $1;", guild_id
        row = await psql().pool.fetchrow(*query)

        if not row:
            raise CacheException(f"Couldn't find any data for {guild_id}.") from None

        data = dict(row)

        # must run orjson in the executor since non-async
        aiodumps = executor(lambda: orjson.dumps(data).decode(encoding="utf-8"))
        jsonified = await aiodumps()

        # 172800 is 2 days
        await self.redis.setex(f"{SETTINGS_PREFIX}{guild_id}", 172800, jsonified)
