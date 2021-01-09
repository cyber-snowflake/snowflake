import asyncio
from functools import wraps
from typing import Any, Coroutine, TypeVar

from discord.ext import commands
from loguru import logger

T = TypeVar("T")


def executor(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Coroutine[Any, Any, T]:
        loop = asyncio.get_running_loop()
        logger.debug(f"Running {func.__name__}")
        future = loop.run_in_executor(None, lambda: func(*args, **kwargs))
        return future

    return wrapper


def typing_indicator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        for obj in args:
            if isinstance(obj, commands.Context):
                await obj.trigger_typing()
                break

        return await func(*args, **kwargs)

    return wrapper
