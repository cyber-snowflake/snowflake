import io
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from discord import File
from discord.ext import commands

from bot import BigMommy
from src.decos import executor


class Statistics(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def stats(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("See help for stats command, you need a subcommand here")

    @stats.command()
    async def badges(self, ctx: commands.Context):
        """Generates a chart of counted flags (badges)"""

        @executor
        def gen_image():
            data = Counter([flag.name for flags in [m.public_flags.all() for m in ctx.guild.members] for flag in flags])
            data = [{"flag": k, "counter": v} for k, v in data.most_common()]

            df = pd.DataFrame(data)

            sns.set_theme(style="darkgrid")
            _, ax = plt.subplots(figsize=(14, 7))

            g = sns.barplot(
                x="flag",
                y="counter",
                data=df,
                palette="husl",
                ci="cd",
                ax=ax,
            )
            g.set(xlabel="", ylabel="")
            plt.xticks(rotation=45)

            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            plt.close()
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)

    @stats.command()
    async def members(self, ctx: commands.Context):
        """Creates a chart of members by statuses"""

        @executor
        def gen_image():
            data = Counter(str(x.status) for x in ctx.guild.members)
            data = [{"status": k, "counter": v} for k, v in data.most_common()]

            df = pd.DataFrame(data)
            df = df.sort_values("counter", ascending=False)

            sns.set_theme(style="darkgrid")

            _, ax = plt.subplots(figsize=(12, 7))
            g = sns.barplot(
                x="status",
                y="counter",
                data=df,
                palette="husl",
                ci="cd",
                ax=ax,
            )
            g.set(xlabel="Statuses", ylabel="Members (count)")
            plt.xticks(rotation=45)

            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            plt.close()
            return buf

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Statistics(bot))
