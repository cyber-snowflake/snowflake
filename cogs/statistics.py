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

import io
import math
from collections import Counter

import matplotlib.pyplot as plt
from discord import File
from discord.ext import commands

from bot import BigMommy
from utils.decos import aioify


class Statistics(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @commands.group()
    async def stats(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("See help for stats command, you need a subcommand here")

    @stats.command()
    async def members(self, ctx: commands.Context):
        """Creates a chart of members by statuses"""
        statuses_data = dict(Counter(str(x.status) for x in ctx.guild.members))
        labels = ["Online", "Idle", "DND", "Offline"]
        colors = ["#43b581", "#faa61a", "#f04747", "#747f8d"]

        statuses = []
        for label in labels:
            statuses.append(int(statuses_data.get(label.lower(), 0)))

        del statuses_data

        @aioify
        def gen_image():
            fig, ax = plt.subplots()
            plt.bar(labels, statuses, color=colors)

            plt.xlabel("Status")
            plt.ylabel("Number of members")

            plt.yticks(range(min(statuses), math.ceil(max(statuses)) + 1))

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Statistics(bot))
