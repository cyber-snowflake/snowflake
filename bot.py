import asyncio
from glob import glob
from os.path import basename, dirname, join
from typing import Optional

import aiohttp
from discord import Guild, HTTPException, Message, User, AllowedMentions
from discord.ext import commands
from loguru import logger

import configurator as config
from utils import Emojis, MyIntents, cachemanager, psql, is_blacklisted


async def get_prefix(client, message: Message):
    # Checks if the message in DMs
    if not message.guild:
        return commands.when_mentioned_or(config.bot_config.default_prefix)(client, message)

    settings = await client.cache.get(message.guild.id)

    prefix = None
    if settings is not None:
        prefix = settings.prefix

    # prefix can be None and in that case it will use bot's default prefix
    return commands.when_mentioned_or(prefix or config.bot_config.default_prefix)(client, message)


class BigMommy(commands.AutoShardedBot):
    def __init__(self, **options):
        super().__init__(
            command_prefix=get_prefix,
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False, replied_user=False),
            case_insensitive=True,
            shard_count=config.bot_config.shard_count,
            shard_ids=config.bot_config.shard_ids,
            intents=MyIntents(),
            **options,
        )

        self.was_ready_once = False
        self.config = config.bot_config

        self.pg = psql()
        self.cache = cachemanager()

        self.owner: Optional[User] = None
        self.support_guild: Optional[Guild] = None
        self.my_emojis = Emojis()

        self.aiosession = aiohttp.ClientSession()

    def run(self):
        # Implement blacklist check
        self.add_check(is_blacklisted)
        # Run the bot
        super().run(config.bot_config.token, reconnect=True)

    async def close(self):
        await self.aiosession.close()
        await super().close()

    async def fetch_bot_owner(self):
        try:
            info = await self.application_info()
            self.owner = info.owner

            logger.info("Owner data has been refreshed.")
        except HTTPException as e:
            logger.error(e)

    async def on_message_edit(self, before: Message, after: Message):
        # process the message as a command if it was edited quickly
        delta = after.created_at - before.created_at
        if delta.seconds <= 60:
            await self.process_commands(after)

    async def on_ready(self):
        for guild in self.guilds:
            if guild.id == self.config.support_guild_id:
                self.support_guild = guild
                self.my_emojis.setup(self.support_guild.emojis)

            await self.pg.add_guild(guild.id)

        if not self.was_ready_once:
            self.was_ready_once = not self.was_ready_once

            asyncio.create_task(self.fetch_bot_owner())
            asyncio.create_task(self.cache.blacklist_refresh())

            cogs = glob(join(dirname(__file__), "cogs/*.py"))
            for ext_path in cogs:
                filename = basename(ext_path)[:-3]

                if not filename.endswith("disabled"):
                    self.load_extension(f"cogs.{filename}")
                    logger.info(f"{filename} extension loaded")

        logger.info(f"{self.user} is ready and working")
        logger.info(f"Guilds: {len(self.guilds)}")
        logger.info(f"Cached Users: {len(set(self.users))}")
