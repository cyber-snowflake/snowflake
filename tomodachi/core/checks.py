#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from tomodachi.core.exceptions import Blacklisted

if TYPE_CHECKING:
    from tomodachi.core.context import TomodachiContext


async def is_blacklisted(ctx: TomodachiContext):
    if ctx.author.id in ctx.bot.blacklist and ctx.author.id != ctx.bot.owner_id:
        raise Blacklisted()

    return True


def is_manager():
    async def predicate(ctx: TomodachiContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        m: discord.Member = ctx.author

        if not m.guild_permissions.manage_guild:
            raise commands.CheckFailure(f"{m} ({m.id}) has insufficient permissions to run this command")

        return True

    return commands.check(predicate)
