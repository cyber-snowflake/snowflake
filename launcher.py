#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import importlib
import logging
import os
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

# Enforcing jishaku flags
for flag in config.JISHAKU_FLAGS:
    os.environ[f"JISHAKU_{flag}"] = "True"

# Setting up logging
format_ = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
logging.basicConfig(level=logging.INFO, format=format_)

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

# Creating database pool
loop = asyncio.get_event_loop()
loop.run_until_complete(pg().setup(config.POSTGRES_DSN))

# Running the bot
tomodachi = Tomodachi()
tomodachi.load_extension("jishaku")
tomodachi.run()
