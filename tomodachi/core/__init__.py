import asyncio
from contextlib import suppress

import aiohttp
import discord as dc
from discord.ext import commands
from loguru import logger

import config
from tomodachi.utils import Emojis, cachemanager, is_blacklisted, psql, make_intents

__all__ = ["Tomodachi"]


async def get_prefix(bot, message: dc.Message):
    prefixes = [config.DEFAULT_PREFIX]

    if message.guild:
        settings = await bot.cache.get(message.guild.id)
        prefix = settings.prefix
        if prefix:
            prefixes.remove(config.DEFAULT_PREFIX)
            prefixes.append(prefix)

    if bot.listen_without_prefix is True and message.author.id == bot.owner_id:
        prefixes.append("")

    return commands.when_mentioned_or(*prefixes)(bot, message)


class Tomodachi(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            allowed_mentions=dc.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False),
            case_insensitive=True,
            shard_count=config.SHARD_COUNT,
            shard_ids=config.SHARD_IDS,
            intents=make_intents(),
            max_messages=200,
            member_cache_flags=dc.MemberCacheFlags(online=True, voice=False, joined=True),
        )

        self.config = config

        self.pg = psql()
        self.cache = cachemanager()

        self.owner = None
        self.support_guild = None
        self.listen_without_prefix = False
        self.my_emojis = Emojis()

        self.aiosession = aiohttp.ClientSession()

        self.default_cd = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)

        self.__once_ready = asyncio.Event()
        self.loop.create_task(self.once_ready())

    def run(self):
        # Run the bot
        super().run(config.TOKEN, reconnect=True)
        # Implement blacklist check
        self.add_check(is_blacklisted)

    async def close(self):
        with suppress(Exception):
            await self.aiosession.close()
            await self.pg.pool.close()

        await super().close()

    async def fetch_bot_owner(self):
        try:
            info = await self.application_info()
            self.owner = info.owner

            logger.info("Owner data has been refreshed.")
        except dc.HTTPException as e:
            logger.error(e)

    async def reset_status(self):
        a = dc.Activity(
            name=f"{config.DEFAULT_STATUS}",
            type=dc.ActivityType.playing,
        )

        await self.change_presence(activity=a, status=dc.Status.dnd)

    async def on_message(self, message: dc.Message):
        bucket = self.default_cd.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        author_id = message.author.id

        ctx = await self.get_context(message)

        if retry_after and author_id != self.owner_id:
            logger.debug(f"{message.author} ({author_id}) is spamming.")
        else:
            await self.invoke(ctx)

    async def on_message_edit(self, before: dc.Message, after: dc.Message):
        # process the message as a command if it was edited quickly
        delta = after.created_at - before.created_at
        if delta.seconds <= 60:
            await self.process_commands(after)

    async def once_ready(self):
        await self.__once_ready.wait()

        self.support_guild = await self.fetch_guild(config.SUPPORT_GUILD_ID)

        emoji = await self.support_guild.fetch_emoji(config.DEFAULT_EMOJI_ID)
        self.my_emojis.setup(self.support_guild.emojis, default_emoji=lambda: emoji)

        for guild in self.guilds:
            await self.pg.add_guild(guild.id)

        # Run all the setup methods
        await asyncio.gather(
            self.fetch_bot_owner(),
            self.cache.blacklist_refresh(),
            self.reset_status(),
        )

    async def on_ready(self):
        if not self.__once_ready.is_set():
            self.__once_ready.set()

        logger.info(f"Guilds: {len(self.guilds)}")
        logger.info(f"Cached Users: {len(set(self.users))}")
