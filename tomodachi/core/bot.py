#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

import discord
from discord.ext import commands

import config
from tomodachi.utils import pg

__all__ = ["Tomodachi"]


async def get_prefix(bot, message: discord.Message):
    prefixes = []

    if not (p := bot.prefixes.get(message.guild.id)):
        prefixes.append(config.DEFAULT_PREFIX)
    else:
        prefixes.append(p)

    return commands.when_mentioned_or(*prefixes)(bot, message)


class Tomodachi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, command_prefix=get_prefix)

        self.pg = pg()
        self.prefixes = {}

        self.__once_ready_ = asyncio.Event()
        self.loop.create_task(self.once_ready())
        self.loop.create_task(self.fetch_prefixes())

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
        print("hi")
