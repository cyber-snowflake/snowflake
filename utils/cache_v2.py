#  The MIT License (MIT)
#
#  Copyright (c) 2020 cyber-snowflake
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import asyncio
from functools import partial
from typing import Optional

from src.sql import psql
from src.storage import InternalStorage

from .decos import aioify
from .exceptions import BadCacheRequest
from .types import GuildSettings

SETTINGS_PREFIX = "S-"  # S-{GUILD}
TEMP_ROOM_PREFIX = "R-"  # R-{GUILD}-{OWNER}


class cachemanager:  # noqa
    storage = InternalStorage()

    @classmethod
    async def settings(cls, guild_id: int) -> GuildSettings:
        @aioify
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

    @classmethod
    async def set_room_id(cls, owner_id: int, guild_id: int, room_id: int):
        func = partial(cls.storage.update, {f"{TEMP_ROOM_PREFIX}{guild_id}-{owner_id}": room_id})
        await asyncio.get_event_loop().run_in_executor(None, func)

    @classmethod
    async def get_room_id(cls, owner_id: int, guild_id: int) -> Optional[int]:
        func = partial(cls.storage.get, f"{TEMP_ROOM_PREFIX}{guild_id}-{owner_id}")
        result = await asyncio.get_event_loop().run_in_executor(None, func)

        return result

    @classmethod
    async def del_room_id(cls, owner_id: int, guild_id: int):
        func = partial(cls.storage.__delitem__, f"{TEMP_ROOM_PREFIX}{guild_id}-{owner_id}")
        await asyncio.get_event_loop().run_in_executor(None, func)
