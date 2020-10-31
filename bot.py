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

from glob import glob
from os.path import basename, dirname, join
from typing import Optional

import aiohttp
from discord import Guild, Message
from discord.ext import commands

import config
from src.sql import psql
from utils.cache_v2 import cachemanager
from utils.emojis import Emojis
from utils.intents import MyIntents
from utils.types import Mention


async def get_prefix(client, message: Message):
    # Checks if the message was sent in DMs
    if not message.guild:
        return commands.when_mentioned_or(config.Bot.default_prefix)(client, message)

    settings = await client.cache.settings(message.guild.id)

    prefix = None
    if settings is not None:
        prefix = settings.prefix

    # prefix can be None and in that case it will use bot's default prefix
    return commands.when_mentioned_or(prefix or config.Bot.default_prefix)(client, message)


class BigMommy(commands.AutoShardedBot):
    def __init__(self, **options):
        super().__init__(
            command_prefix=get_prefix,
            allowed_mentions=Mention.nobody,
            case_insensitive=True,
            shard_count=config.Bot.shard_count,
            shard_ids=config.Bot.shard_ids,
            intents=MyIntents(),
            **options,
        )

        self.was_ready_once = False
        self.config = config

        self.pg = psql()
        self.cache = cachemanager

        self.support_guild: Optional[Guild] = None
        self.my_emojis = Emojis()

        self.aiosession = aiohttp.ClientSession()

    def run(self):
        # Implement blacklist check
        # self.add_check(check_blacklist)
        # Run the bot
        super().run(config.Bot.token, reconnect=True)

    async def close(self):
        await self.aiosession.close()
        await super().close()

    async def on_ready(self):
        for guild in self.guilds:
            if guild.id == self.config.Bot.support_guild_id:
                self.support_guild = guild
                self.my_emojis.setup(self.support_guild.emojis)

            await self.pg.add_guild(guild.id)

        if not self.was_ready_once:
            self.was_ready_once = not self.was_ready_once

            # Hide token
            self.config.Bot.token = None

            cogs = glob(join(dirname(__file__), "cogs/*.py"))
            for ext_path in cogs:
                filename = basename(ext_path)[:-3]

                if not filename.endswith("disabled"):
                    self.load_extension(f"cogs.{filename}")
                    print(f"* {filename}")

        print(f"{self.user} is soooooooo ready sooo coooooooooooooooool!!111!!1!!")
