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

from typing import Optional

import asyncpg

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
        print("Postgres connection created")

    async def add_guild(self, guild_id: int):
        await self.pool.execute("INSERT INTO guilds(guild_id) VALUES($1) ON CONFLICT DO NOTHING;", guild_id)
