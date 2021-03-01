#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import asyncio
import functools
from typing import Callable

__all__ = ["run_in_executor"]


def run_in_executor(func: Callable):
    """Decorator that runs sync functions in executor"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        partial = functools.partial(func, *args, **kwargs)
        future = await asyncio.get_event_loop().run_in_executor(None, partial)

        return future

    return wrapper
