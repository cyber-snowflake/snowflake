#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import asyncio
from typing import Optional

import discord
from discord.ext import commands

import config
from tomodachi.core.checks import spam_control
from tomodachi.core.context import TomodachiContext
from tomodachi.core.icons import Icons
from tomodachi.utils import pg, make_intents

__all__ = ["Tomodachi"]


class Tomodachi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            command_prefix=self.get_prefix,
            intents=make_intents(),
        )

        self.pg = pg()
        self.prefixes = {}

        # Alias to Icons singleton
        self.icon = Icons()
        # Faster access to support guild data
        self.support_guild: Optional[discord.Guild] = None

        # Global rate limit cooldowns mapping
        self.global_rate_limit = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)
        # Toggle rate limits for bot owner or not
        # by default bot owner can be rate limited
        self.owner_has_limits = True

        self.__once_ready_ = asyncio.Event()
        self.loop.create_task(self.once_ready())
        self.loop.create_task(self.fetch_prefixes())

    async def get_prefix(self, message: discord.Message):
        prefixes = []

        if not (p := self.prefixes.get(message.guild.id)):
            prefixes.append(config.DEFAULT_PREFIX)
        else:
            prefixes.append(p)

        return commands.when_mentioned_or(*prefixes)(self, message)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or TomodachiContext)

    def run(self):
        super().run(config.TOKEN, reconnect=True)

    async def fetch_prefixes(self):
        await self.pg.connection_established.wait()

        async with self.pg.pool.acquire() as conn:
            records = await conn.fetch("SELECT guild_id, prefix FROM guilds;")

        self.prefixes.update({k: v for k, v in map(tuple, records)})

    async def on_ready(self):
        if not self.__once_ready_.is_set():
            self.__once_ready_.set()

    async def once_ready(self):
        await self.__once_ready_.wait()

        self.add_check(spam_control)

        for ext in config.EXTENSIONS:
            self.load_extension(f"tomodachi.exts.{ext}")

        self.support_guild = support_guild = await self.fetch_guild(config.SUPPORT_GUILD_ID)
        await self.icon.setup(support_guild.emojis)
