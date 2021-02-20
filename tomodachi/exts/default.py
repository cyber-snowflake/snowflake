#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from discord.ext import commands

from tomodachi.core.bot import Tomodachi


class Default(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello, {ctx.author.name}! I'm {ctx.bot.user.name}.")


def setup(bot):
    bot.add_cog(Default(bot))
