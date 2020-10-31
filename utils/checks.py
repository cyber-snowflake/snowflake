#  The MIT License (MIT)
#
#  Copyright (c) 2020 cyber-snowflake
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

from discord import Member
from discord.ext import commands

from .exceptions import NotInVoiceChat


def is_manager_or_bot_owner():
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.author, Member):
            author: Member = ctx.author

            if author.id == ctx.bot.owner_id or author.guild_permissions.manage_guild:
                return True
            else:
                raise commands.CheckFailure(f"{author.id} is not allowed to run {ctx.command.qualified_name}") from None

    return commands.check(predicate=predicate)


def is_in_voice():
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.author, Member):
            if ctx.author.voice is not None:
                return True
            else:
                raise NotInVoiceChat(f"{ctx.author.id} is not in voice chat.", ctx.author) from None

    return commands.check(predicate)
