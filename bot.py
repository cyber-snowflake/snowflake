import asyncio
from glob import glob
from os.path import basename, dirname, join
from typing import Optional

import aiohttp
from discord import Guild, HTTPException, Message, User
from discord.ext import commands
from loguru import logger

import config
from src.types import Mention
from utils import Emojis, MyIntents, cachemanager, psql


async def get_prefix(client, message: Message):
    # Checks if the message in DMs
    if not message.guild:
        return commands.when_mentioned_or(config.Bot.default_prefix)(client, message)

    settings = await client.cache.get(message.guild.id)

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

        self.owner: Optional[User] = None
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

    async def fetch_bot_owner(self):
        try:
            info = await self.application_info()
            self.owner = info.owner

            logger.info("Owner data has been refreshed.")
        except HTTPException as e:
            logger.error(e)

    async def on_ready(self):
        for guild in self.guilds:
            if guild.id == self.config.Bot.support_guild_id:
                self.support_guild = guild
                self.my_emojis.setup(self.support_guild.emojis)

            await self.pg.add_guild(guild.id)

        if not self.was_ready_once:
            self.was_ready_once = not self.was_ready_once
            self.config.Bot.token = None

            asyncio.create_task(self.fetch_bot_owner())

            cogs = glob(join(dirname(__file__), "cogs/*.py"))
            for ext_path in cogs:
                filename = basename(ext_path)[:-3]

                if not filename.endswith("disabled"):
                    self.load_extension(f"cogs.{filename}")
                    logger.info(f"{filename} extension loaded")

        logger.info(f"{self.user} is ready and working")
        logger.info(f"Guilds: {len(self.guilds)}")
        logger.info(f"Cached Users: {len(set(self.users))}")
