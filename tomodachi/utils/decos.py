import asyncio
from functools import wraps, partial
from typing import TypeVar, Optional, Any, Callable

from discord.ext import commands
from loguru import logger

__all__ = ["executor", "typing_indicator"]

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
