from utils.sql import psql
from src.storage import InternalStorage
from src.decos import executor
from src.exceptions import BadCacheRequest
from src.types import GuildSettings

SETTINGS_PREFIX = "S-"  # S-{GUILD}


class cachemanager:  # noqa
    storage = InternalStorage()

    @classmethod
    async def settings(cls, guild_id: int) -> GuildSettings:
        @executor
        def get_data():
            return cls.storage[guild_id]

        data = await get_data()
        if not data:
            is_fresh = await cls.refresh(guild_id)
            if not is_fresh:
                raise BadCacheRequest(f"There is no data for {guild_id}.")
            data = await get_data()

        return data

    @classmethod
    async def refresh(cls, guild_id: int) -> bool:
        query = "SELECT * FROM guilds WHERE guild_id = $1;", guild_id
        row = await psql().pool.fetchrow(*query)

        if not row:
            raise BadCacheRequest(f"Couldn't find any data for {guild_id}.") from None

        data = dict(row)
        settings = GuildSettings(**data)
        cls.storage[guild_id] = settings

        return True if settings else False
