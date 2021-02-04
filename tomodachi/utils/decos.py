import asyncio
from functools import wraps, partial
from typing import TypeVar, Optional, Any, Callable

from discord import Message
from discord.ext import commands
from discord.utils import find
from loguru import logger

__all__ = ["executor", "typing_indicator", "typing"]

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


def typing_indicator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        executed: Optional[Any] = None

        for obj in set(args):
            if isinstance(obj, commands.Context):
                async with obj.typing():
                    executed = await func(*args, **kwargs)
                break
            else:
                continue

        return executed

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
