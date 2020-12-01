import asyncio
from functools import wraps
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def aioify(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Coroutine[Any, Any, T]:
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return wrapper
