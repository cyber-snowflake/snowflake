#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Optional

import asyncpg

from .singleton import MetaSingleton

__all__ = ["pg"]


class pg(metaclass=MetaSingleton):  # noqa
    def __init__(self):
        self.__pool_: Optional[asyncpg.Pool] = None

    async def setup(self, dsn: str):
        self.__pool_ = await asyncpg.create_pool(dsn)
        print("connection established to pgsql")

    @property
    def pool(self):
        return self.__pool_

    @pool.setter
    def pool(self, value):
        raise AttributeError("Can not set this.") from None
