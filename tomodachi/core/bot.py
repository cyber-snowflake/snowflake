#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Union

import aiohttp
import discord
from discord.ext import commands

import config
from tomodachi.core.context import TomodachiContext
from tomodachi.core.icons import Icons
from tomodachi.utils import pg, make_intents, make_cache_policy, AniList

__all__ = ["Tomodachi"]


class Tomodachi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            max_messages=150,
            command_prefix=self.get_prefix,
            intents=make_intents(),
            member_cache_flags=make_cache_policy(),
            owner_id=config.OWNER_ID,
        )
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()  # noqa

        # Alias to config module
        self.config = config

        self.pg = pg()
        self.prefixes = {}
        # tuple with user ids
        self.blacklist = ()

        # Alias to Icons singleton
        self.icon = Icons()
        # Faster access to support guild data
        self.support_guild: Optional[discord.Guild] = None

        # Global rate limit cooldowns mapping
        self.global_rate_limit = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.user)

        self.session = aiohttp.ClientSession()

        self.__once_ready_ = asyncio.Event()
        self.loop.create_task(self.once_ready())

        # Fetch custom prefixes and blacklisted users
        self.loop.create_task(self.fetch_blacklist())
        self.loop.create_task(self.fetch_prefixes())

    async def close(self):
        if not self.session.closed:
            await self.session.close()

        await super().close()

    async def get_prefix(self, message: discord.Message):
        prefixes = (f'<@!{self.user.id}> ', f'<@{self.user.id}> ')

        if not (p := self.prefixes.get(message.guild.id)):
            prefixes += (config.DEFAULT_PREFIX,)
        else:
            prefixes += (p,)

        return prefixes

    async def update_prefix(self, guild_id: int, new_prefix: str):
        prefix = await self.pg.update_prefix(guild_id, new_prefix)
        self.prefixes[guild_id] = prefix
        return self.prefixes[guild_id]

    async def get_context(self, message, *, cls=None) -> Union[TomodachiContext, commands.Context]:
        return await super().get_context(message, cls=cls or TomodachiContext)

    async def process_commands(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id in self.blacklist:
            return

        ctx = await self.get_context(message)

        bucket = self.global_rate_limit.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after and ctx.author.id != self.owner_id:
            return await message.channel.send(
                content=f"You are being globally rate limited. Please, wait `{retry_after:.2f}` seconds.",
                delete_after=retry_after,
            )

        await self.invoke(ctx)

    async def fetch_prefixes(self):
        await self.pg.connection_established.wait()

        async with self.pg.pool.acquire() as conn:
            records = await conn.fetch("SELECT guild_id, prefix FROM guilds;")

        self.prefixes.update({k: v for k, v in map(tuple, records)})

    async def fetch_blacklist(self):
        await self.pg.connection_established.wait()

        async with self.pg.pool.acquire() as conn:
            records = await conn.fetch("SELECT DISTINCT * FROM blacklisted;")

        self.blacklist = tuple(r["user_id"] for r in records)

    async def on_ready(self):
        if not self.__once_ready_.is_set():
            self.__once_ready_.set()

    async def once_ready(self):
        await self.__once_ready_.wait()

        for guild in self.guilds:
            self.loop.create_task(self.pg.store_guild(guild.id))

        self.support_guild = support_guild = await self.fetch_guild(config.SUPPORT_GUILD_ID)
        await self.icon.setup(support_guild.emojis)
        await AniList.setup(self.session)

        for ext in config.EXTENSIONS:
            self.load_extension(f"tomodachi.exts.{ext}")
            logging.info(f"loaded {ext}")
