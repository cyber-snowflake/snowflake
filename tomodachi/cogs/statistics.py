import io
from collections import Counter

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
from discord import File, Message, Member, RawMessageDeleteEvent, RawMessageUpdateEvent, Guild, User
from discord.ext import commands

from tomodachi.core import Module
from tomodachi.utils import executor, typing


class Statistics(Module):
    @staticmethod
    def save_plot():
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return buf

    # this code is probably super bad since
    # my knowledge of asyncio is quite bad
    # TODO: check if those listeners need some enhancements
    async def run_query(self, query: tuple = None, *args):
        query = query or tuple(args)

        async with self.bot.pg.pool.acquire() as conn:
            await conn.execute(*query)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if guild := message.guild:
            query = (
                """
                INSERT INTO stats (guild_id, messages_sent) VALUES ($1, 1)
                ON CONFLICT (guild_id, _date)
                DO UPDATE SET messages_sent = stats.messages_sent + 1;
                """,
                guild.id,
            )

            await self.run_query(query)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        if gid := payload.data.get("guild_id"):
            gid = int(gid)

            query = (
                """
                INSERT INTO stats (guild_id, messages_edited) VALUES ($1, 1)
                ON CONFLICT (guild_id, _date)
                DO UPDATE SET messages_edited = stats.messages_edited + 1;
                """,
                gid,
            )

            await self.run_query(query)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        if gid := payload.guild_id:
            query = (
                """
                INSERT INTO stats (guild_id, messages_deleted) VALUES ($1, 1)
                ON CONFLICT (guild_id, _date)
                DO UPDATE SET messages_deleted = stats.messages_deleted + 1;
                """,
                gid,
            )

            await self.run_query(query)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        query = (
            """
            INSERT INTO stats (guild_id, members_joined) VALUES ($1, 1)
            ON CONFLICT (guild_id, _date)
            DO UPDATE SET members_joined = stats.members_joined + 1;
            """,
            member.guild.id,
        )

        await self.run_query(query)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        query = (
            """
            INSERT INTO stats (guild_id, members_left) VALUES ($1, 1)
            ON CONFLICT (guild_id, _date)
            DO UPDATE SET members_left = stats.members_left + 1;
            """,
            member.guild.id,
        )

        await self.run_query(query)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: Guild, _user: User):
        query = (
            """
            INSERT INTO stats (guild_id, members_banned) VALUES ($1, 1)
            ON CONFLICT (guild_id, _date)
            DO UPDATE SET members_banned = stats.members_banned + 1;
            """,
            guild.id,
        )

        await self.run_query(query)

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def stats(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("See help for stats command, you need a subcommand here")

    @stats.command()
    @typing()
    async def members(self, ctx: commands.Context):
        """Generates a chart of audience retention for the last 7 days"""
        async with self.bot.pg.pool.acquire() as conn:
            query = """
                SELECT
                    unnest(array[_date, _date, _date]) as day,
                    unnest(array['Members Joined', 'Members Left', 'Members Banned']) as criteria,
                    unnest(array[members_joined, members_left, members_banned]) as counter
                FROM stats
                WHERE stats._date >= timezone('utc'::text, now()) - INTERVAL '7 days'
                AND guild_id = $1
                ORDER BY _date DESC, criteria DESC;
                """

            rows = await conn.fetch(query, ctx.guild.id)

        @executor
        def gen_image():
            df = pd.DataFrame(dict(row) for row in rows)

            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.suptitle("Members retention for the last 7 days")

            g = sns.lineplot(
                ax=ax,
                alpha=0.8,
                x="day",
                y="counter",
                hue="criteria",
                data=df,
                palette="husl",
                ci="cd",
                style="criteria",
                markers=True,
                dashes=False,
                linewidth=2,
            )
            g.set(xlabel="", ylabel="")

            # format the ticks
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_minor_locator(mticker.NullLocator())

            ax.yaxis.get_major_locator().set_params(integer=True)

            fig.autofmt_xdate()
            ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")

            plt.tight_layout()

            return self.save_plot()

        fp = await gen_image()
        _file = File(fp, "stats.png")
        await ctx.send(file=_file)

    @stats.command()
    @typing()
    async def messages(self, ctx: commands.Context):
        """Generates a chart with messages activity for the last week"""
        async with self.bot.pg.pool.acquire() as conn:
            query = (
                """
                SELECT
                    unnest(array[_date, _date, _date]) as day,
                    unnest(array['Messages Sent', 'Messages Edited', 'Messages Deleted']) as criteria,
                    unnest(array[messages_sent, messages_edited, messages_deleted]) as counter
                FROM stats
                WHERE stats._date >= timezone('utc'::text, now()) - INTERVAL '7 days'
                AND guild_id = $1
                ORDER BY _date DESC, criteria DESC;
                """,
                ctx.guild.id,
            )
            rows = await conn.fetch(*query)

        @executor
        def gen_image():
            df = pd.DataFrame(dict(row) for row in rows)

            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.suptitle("Messages activity for the last 7 days")

            g = sns.lineplot(
                ax=ax,
                alpha=0.8,
                x="day",
                y="counter",
                hue="criteria",
                data=df,
                palette="husl",
                ci="cd",
                style="criteria",
                markers=True,
                dashes=False,
                linewidth=2,
            )
            g.set(xlabel="", ylabel="")

            # format the ticks
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_minor_locator(mticker.NullLocator())

            ax.yaxis.get_major_locator().set_params(integer=True)

            fig.autofmt_xdate()
            ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")

            plt.tight_layout()

            return self.save_plot()

        fp = await gen_image()
        _file = File(fp, "stats.png")
        await ctx.send(file=_file)

    @stats.command()
    @typing()
    async def badges(self, ctx: commands.Context):
        """Generates a chart of counted flags (badges)"""

        @executor
        def gen_image():
            data = Counter([flag.name for flags in [m.public_flags.all() for m in ctx.guild.members] for flag in flags])
            df = pd.DataFrame({"flag": k, "counter": v} for k, v in data.most_common())

            sns.set_theme(style="whitegrid")
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
            ax.yaxis.get_major_locator().set_params(integer=True)

            plt.tight_layout()

            return self.save_plot()

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)

    @stats.command()
    @typing()
    async def statuses(self, ctx: commands.Context):
        """Creates a chart of members by statuses"""

        @executor
        def gen_image():
            data = Counter(str(x.status) for x in ctx.guild.members)
            df = pd.DataFrame({"status": k, "counter": v} for k, v in data.most_common())
            df = df.sort_values("counter", ascending=False)

            sns.set_theme(style="whitegrid")

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
            ax.yaxis.get_major_locator().set_params(integer=True)

            plt.tight_layout()

            return self.save_plot()

        fp = await gen_image()
        _file = File(fp, "stats.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Statistics(bot))
