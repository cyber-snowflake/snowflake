import pytz
from discord.ext import commands

from bot import Tomodachi
from tomodachi.src.decos import typing_indicator
from tomodachi.src.myembed import MyEmbed
from tomodachi.utils import is_manager_or_bot_owner


class Admin(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @commands.group(aliases=("cfg",))
    @commands.guild_only()
    @is_manager_or_bot_owner()
    async def config(self, ctx: commands.Context):
        """Changes settings of the bot in this server."""
        if not ctx.invoked_subcommand:
            settings = await self.bot.cache.get(ctx.guild.id)

            embed = MyEmbed(title=f"Current settings of {ctx.guild.name}")
            embed.add_field(name="Prefix", value=f"{settings.prefix or self.bot.config.default_prefix}")
            embed.add_field(name="Timezone", value=f"{settings.tz}")

            await ctx.send(embed=embed)

    @config.command()
    @typing_indicator
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        """Manage server's prefix."""
        if not new_prefix:
            settings = await self.bot.cache.get(ctx.guild.id)
            prefix = settings.prefix or self.bot.config.default_prefix

            await ctx.send(f":information_source: Current bot's prefix in this server is `{prefix}`")
        elif len(new_prefix) > 16:
            await ctx.send(":x: New prefix must be less than 16 characters.")
        else:
            async with self.bot.pg.pool.acquire() as conn:
                query = "UPDATE guilds SET prefix = $1 WHERE guild_id = $2 RETURNING true;"
                updated = await conn.fetchval(query, new_prefix, ctx.guild.id)

            if updated:
                await self.bot.cache.refresh(ctx.guild.id)
                await ctx.send(f":ok_hand: Bot's prefix has been updated to `{new_prefix}`")
            else:
                await ctx.send(":x: Bot's prefix didn't change. Contact bot owner if it happens again.")

    @config.command(aliases=("tz",))
    @typing_indicator
    async def timezone(self, ctx: commands.Context, tz: str = None):
        """Changes server's timezone.

        This affects some output that has something to do with time.
        """
        settings = await self.bot.cache.get(ctx.guild.id)

        if tz is None:
            await ctx.send(f":information_source: Current timezone is **{settings.tz}**")
        else:
            try:
                new_tz = pytz.timezone(tz)
            except pytz.UnknownTimeZoneError:
                await ctx.send(":x: You have provided an invalid timezone.")
            else:
                async with self.bot.pg.pool.acquire() as conn:
                    statement = "UPDATE guilds SET tz = $1 WHERE guild_id = $2 RETURNING true;"
                    is_updated = await conn.fetchval(statement, f"{new_tz}", ctx.guild.id)

                    await self.bot.cache.refresh(ctx.guild.id)

                if is_updated:
                    await ctx.send(f":ok_hand: Timezone has been updated to `{new_tz}`")
                else:
                    await ctx.send(":x: Nothing changed. Contact bot owner if it happens again.")


def setup(bot):
    bot.add_cog(Admin(bot))
