import asyncio
from contextlib import suppress
from typing import Optional

import aiohttp
import discord as dc
from discord.ext import commands
from loguru import logger

import configurator as config
from tomodachi.utils import Emojis, MyIntents, cachemanager, is_blacklisted, psql

__all__ = ["Tomodachi", "Module"]


async def get_prefix(client, message: dc.Message):
    # Checks if the message in DMs
    if not message.guild:
        return commands.when_mentioned_or(config.bot_config.default_prefix)(client, message)

    settings = await client.cache.get(message.guild.id)

    prefix = None
    if settings is not None:
        prefix = settings.prefix

    # prefix can be None and in that case it will use bot's default prefix
    return commands.when_mentioned_or(prefix or config.bot_config.default_prefix)(client, message)


class Tomodachi(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            allowed_mentions=dc.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False),
            case_insensitive=True,
            shard_count=config.bot_config.shard_count,
            shard_ids=config.bot_config.shard_ids,
            intents=MyIntents(),
            max_messages=200,
            member_cache_flags=dc.MemberCacheFlags(online=True, voice=False, joined=True),
        )

        self.was_ready_once = False
        self.config = config.bot_config

        self.pg = psql()
        self.cache = cachemanager()

        self.owner: Optional[dc.User] = None
        self.support_guild: Optional[dc.Guild] = None
        self.my_emojis = Emojis()

        self.aiosession = aiohttp.ClientSession()

        self.default_cd = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)

    def run(self):
        # Run the bot
        super().run(config.bot_config.token, reconnect=True)
        # Implement blacklist check
        self.add_check(is_blacklisted)

    async def close(self):
        await super().close()

        with suppress(Exception):
            await self.aiosession.close()
            await self.pg.pool.close()

    async def fetch_bot_owner(self):
        try:
            info = await self.application_info()
            self.owner = info.owner

            logger.info("Owner data has been refreshed.")
        except dc.HTTPException as e:
            logger.error(e)

    async def reset_status(self):
        a = dc.Activity(
            name=f"{config.bot_config.default_status}",
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
        self.support_guild = await self.fetch_guild(config.bot_config.support_guild_id)

        emoji = await self.support_guild.fetch_emoji(config.bot_config.default_emoji_id)
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
        if not self.was_ready_once:
            self.was_ready_once = not self.was_ready_once
            asyncio.create_task(self.once_ready())

        logger.info(f"Guilds: {len(self.guilds)}")
        logger.info(f"Cached Users: {len(set(self.users))}")
