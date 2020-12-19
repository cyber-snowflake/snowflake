import io
import math
from collections import Counter
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from discord import File
from discord.ext import commands

from bot import BigMommy
from utils.decos import aioify


class Statistics(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @staticmethod
    def make_dataframe_from_dict(
        data: dict,
        keys: str = "labels",
        values: str = "values",
        sort_values: bool = False,
        asc: bool = False,
    ):
        """

        Args:
            data: base dictionary of data
            keys: name of keys column
            values: name of values column
            sort_values: should the data get sorted
            asc: an alias to DataFrame.sort_value(ascending=x)

        """
        df = pd.DataFrame({keys: data.keys(), values: data.values()})
        if sort_values:
            df = df.sort_values(values, ascending=asc)

        return df

    @staticmethod
    def find_yticks(x: Iterable):
        return range(min(x), math.ceil(max(x)) + 1)

    @commands.group()
    async def stats(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("See help for stats command, you need a subcommand here")

    @stats.command()
    async def badges(self, ctx: commands.Context):
        """Generates a chart of counted flags (badges)"""
        def badges_iterator():
            for m in ctx.guild.members:
                for f in m.public_flags.all():
                    yield str(f.name).replace("_", " ").title()

        badges = dict(Counter(badges_iterator()).most_common())

        @aioify
        def gen_image():
            sns.set_theme(style="darkgrid")

            df = self.make_dataframe_from_dict(badges, "flags", "count", sort_values=True)

            ax = sns.barplot(x="flags", y="count", data=df, palette="Blues_d")
            ax.set(xlabel="Flag", ylabel="Members (count)")

            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            plt.yticks(self.find_yticks(badges.values()))
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
        data = dict(Counter(str(x.status) for x in ctx.guild.members))

        @aioify
        def gen_image():
            df = pd.DataFrame({"Statuses": data.keys(), "Counters": data.values()})
            df = df.sort_values("Counters", ascending=False)

            sns.set_theme(style="darkgrid")

            ax = sns.barplot(x="Statuses", y="Counters", data=df, palette="rocket")
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            ax.set(xlabel="Statuses", ylabel="Members (count)")

            plt.yticks(self.find_yticks(data.values()))
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
