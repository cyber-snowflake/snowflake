#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import traceback

import discord
from discord.ext import commands
from loguru import logger

from tomodachi.core.bot import Tomodachi
from tomodachi.core.exceptions import GloballyRateLimited


class ErrorHandling(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot
        self.ignored = (commands.CommandNotFound,)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error = getattr(error, "original", error)

        # ignored error types are being suppressed
        # along with local error handler in order
        # to let local's handle the error
        if isinstance(error, self.ignored) or hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, GloballyRateLimited):
            if not self.bot.owner_has_limits:
                return await ctx.reinvoke()

            retry_after = f"{error.retry_after:.2f}"
            return await ctx.reply(
                f"You are being rate limited. Please, chill out and try again in `{retry_after}` seconds.",
                delete_after=error.retry_after,
                mention_author=True,
            )

        elif isinstance(error, commands.CommandOnCooldown):
            if not self.bot.owner_has_limits:
                return await ctx.reinvoke()

            retry_after = f"{error.retry_after:.2f}"
            return await ctx.reply(f"Please, try again in `{retry_after}` seconds.", mention_author=True)

        # send some debug information to bot owner
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(f"Ignoring exception in command {ctx.command}.")
        logger.exception(tb)

        e = discord.Embed(color=0xFF0000, title="Exception")
        e.add_field(name="Command", value=f"{ctx.message.content[0:1000]}")
        e.add_field(name="Author", value=f"{ctx.author} (`{ctx.author.id}`)")
        e.add_field(name="Guild", value="{}".format(f"{g.name} (`{g.id}`)" if (g := ctx.guild) else "None"))

        if u := self.bot.get_user(self.bot.owner_id):
            await u.send(embed=e, content=f"```\n{tb[0:2000]}\n```")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.channel.send(f"{error}")


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
