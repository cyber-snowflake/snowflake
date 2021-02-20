#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import importlib
import logging
import os
import sys
from typing import Any

from loguru import logger

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
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging_level = os.environ.get("LOGGING_LEVEL", "INFO")

std_logger = logging.getLogger()
std_logger.setLevel(logging_level)
std_logger.handlers = [InterceptHandler()]

logger.remove()
logger.add(sys.stderr, enqueue=True, level=logging_level)

# Creating database pool
loop = asyncio.get_event_loop()
loop.run_until_complete(pg().setup(config.POSTGRES_DSN))

# Running the bot
tomodachi = Tomodachi()
tomodachi.load_extension("jishaku")
tomodachi.run()
