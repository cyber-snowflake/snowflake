#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Union

import discord
from discord.ext.commands import CommandError

__all__ = ["GloballyRateLimited", "Blacklisted"]


class Blacklisted(CommandError):
    pass


class GloballyRateLimited(CommandError):
    def __init__(self, user: Union[discord.User, discord.Member], retry_after: Union[int, float]):
        self.user = user
        self.retry_after = retry_after


class AniListException(CommandError):
    pass
