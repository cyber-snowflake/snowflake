#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import importlib
from typing import Any

import config
from tomodachi.core.bot import Tomodachi
from tomodachi.utils import pg

try:
    uvloop: Any = importlib.import_module("uvloop")
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop = asyncio.get_event_loop()
loop.run_until_complete(pg().setup(config.POSTGRES_DSN))

tomodachi = Tomodachi()
tomodachi.run()
