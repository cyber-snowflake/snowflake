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
import seaborn as sns
from discord import File, CategoryChannel
from discord.ext import commands

from bot import BigMommy
from utils.decos import aioify


class Statistics(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

        self._discord_colors = {
            "online": "#43b581",
            "idle": "#faa61a",
            "dnd": "#f04747",
            "offline": "#747f8d",
            ##
            "staff": "#7289da",
            "partner": "#7289da",
            "hypesquad": "#fbb848",
            "hypesquad_balance": "#45ddc0",
            "hypesquad_brilliance": "#f47b67",
            "hypesquad_bravery": "#9c84ef",
            "bug_hunter": "#43b581",
            "bug_hunter_level_2": "#ffd56c",
            "early_supporter": "#7289da",
            "verified_bot": "#3e70dd",
            "verified_bot_developer": "#3e70dd",
        }

    @staticmethod
    def find_yticks(x: Iterable):
        return range(min(x), math.ceil(max(x)) + 1)

    @commands.group()
    async def stats(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("See help for stats command, you need a subcommand here")

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
        members = OrderedDict(Counter(x.status.name for x in ctx.guild.members).most_common())

        x = list(str(status) for status in members.keys())
        y = list(count for count in members.values())

        @aioify
        def gen_image():
            sns.set(style="darkgrid")
            f, ax = plt.subplots(1, 1)

            palette = sns.color_palette(list(self._status_colors.get(label, "#FF0000") for label in x))
            sns.barplot(x=x, y=y, ax=ax, palette=palette)

            ax.set_ylabel("Member Count")
            ax.set_xlabel("Statuses")

            plt.yticks(self.find_yticks(y))
            plt.tight_layout(pad=2)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Statistics(bot))
