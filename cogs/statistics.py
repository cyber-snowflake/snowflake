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
import random
from collections import Counter, OrderedDict
from typing import Iterable

import matplotlib.pyplot as plt
from discord import File, CategoryChannel
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

    @staticmethod
    def find_yticks(x: Iterable):
        return range(min(x), math.ceil(max(x)) + 1)

    @stats.command()
    async def channels(self, ctx: commands.Context):
        """Creates a pie chart of channels"""
        labels = []
        counters = []
        colors = []

        for cat, channels in sorted(ctx.guild.by_category(), key=lambda pair: len(pair[1]), reverse=True):
            count = len(channels)
            counters.append(count)

            if cat is None:
                labels.append(f"No Category ({count})")
            elif isinstance(cat, CategoryChannel):
                labels.append(f"{cat.name} ({count})")

            r = lambda: random.randint(0, 255)
            colors.append("#%02X%02X%02X" % (r(), r(), r()))

        @aioify
        def gen_image():
            plt.xkcd()
            plt.subplots()

            patches, texts = plt.pie(counters, startangle=90)
            plt.axis("equal")

            plt.title("Channels per category")
            plt.legend(patches, labels, loc="best")

            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)

    @stats.command()
    async def badges(self, ctx: commands.Context):
        def badges_iterator():
            for m in ctx.guild.members:
                for f in m.public_flags.all():
                    yield str(f.name).replace("_", " ").title()

        badges = OrderedDict(Counter(badges_iterator()).most_common())
        labels = badges.keys()
        data = badges.values()

        @aioify
        def gen_image():
            plt.xkcd()
            plt.subplots()
            plt.bar(labels, data, color="#7289da")

            plt.xlabel("")
            plt.ylabel("Number of owners")

            plt.yticks(self.find_yticks(data))
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)

    @stats.command()
    async def members(self, ctx: commands.Context):
        """Creates a chart of members by statuses"""
        labels = ["Online", "Idle", "DND", "Offline"]
        colors = ["#43b581", "#faa61a", "#f04747", "#747f8d"]

        statuses_data = dict(Counter(str(x.status) for x in ctx.guild.members))
        statuses = [int(statuses_data.get(label.lower(), 0)) for label in labels]
        del statuses_data

        @aioify
        def gen_image():
            plt.xkcd()
            plt.subplots()
            plt.bar(labels, statuses, color=colors)

            plt.xlabel("Status")
            plt.ylabel("Number of members")

            plt.yticks(self.find_yticks(statuses))
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Statistics(bot))
