import asyncio
import contextlib
from functools import partial, wraps
from typing import Callable, Optional, TypeVar

from discord import Message
from discord.ext import commands
from discord.utils import find
from loguru import logger

__all__ = ["executor", "typing", "loading"]

T = TypeVar("T")


def executor(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug(f"Running {func.__name__}")
        to_run = partial(func, *args, **kwargs)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, to_run)
        return result

    return wrapper


def loading(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = find(lambda el: isinstance(el, commands.Context), args)
        task = asyncio.create_task(func(*args, **kwargs))

        if not ctx:
            return await task

        emote = ctx.bot.my_emojis("loading")
        is_added = False

        try:
            await ctx.message.add_reaction(emote)
        except:
            pass
        else:
            is_added = True

        if not task.done():
            await task

        if is_added:
            with contextlib.suppress(Exception):
                await ctx.message.remove_reaction(emote, ctx.bot.user)

    return wrapper


def typing(inform_if_long: bool = False):
    def inner(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Optional[commands.Context] = find(lambda el: isinstance(el, commands.Context), args)

            if not ctx:
                return await func(*args, **kwargs)

            info: Optional[Message] = None

            if inform_if_long is True:
                info = await ctx.reply("This operation may take a while, please, be patient.")

            try:
                async with ctx.typing():
                    executed = await func(*args, **kwargs)
            finally:
                if inform_if_long and info:
                    await info.delete()

            return executed

        return wrapper

    return inner
