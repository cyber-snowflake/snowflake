import pytz
from discord import VoiceChannel
from discord.ext import commands

from bot import BigMommy
from utils import is_manager_or_bot_owner
from src.myembed import MyEmbed


class Admin(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    @commands.group(aliases=("cfg",))
    @commands.guild_only()
    @is_manager_or_bot_owner()
    async def config(self, ctx: commands.Context):
        """Changes settings of the bot in this server."""
        if not ctx.invoked_subcommand:
            settings = await self.bot.cache.get(ctx.guild.id)
            main_vc = self.bot.get_channel(settings.main_vc_id) if settings.main_vc_id else None

            embed = MyEmbed(title=f"Current settings of {ctx.guild.name}")
            embed.add_field(name="Prefix", value=f"{settings.prefix or self.bot.config.Bot.default_prefix}")
            embed.add_field(name="Timezone", value=f"{settings.tz}")
            if main_vc:
                embed.add_field(name="Rooms Creator Channel", value=f"{main_vc.name} (`{main_vc.id}`)", inline=False)
            else:
                embed.add_field(name="Rooms Creator Channel", value="Not set.", inline=False)

            await ctx.send(embed=embed)

    @config.command()
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        """Manage server's prefix."""
        await ctx.trigger_typing()

        if not new_prefix:
            settings = await self.bot.cache.get(ctx.guild.id)
            prefix = settings.prefix or self.bot.config.Bot.default_prefix

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
    async def timezone(self, ctx: commands.Context, tz: str = None):
        """Changes server's timezone.

        This affects some output that has something to do with time.
        """
        await ctx.trigger_typing()

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

    @config.command(aliases=("rcc",))
    async def rooms_creator(self, ctx: commands.Context, channel_id: int):
        """Sets the main voice channel rooms creator.

        When any server member joins the channel, a new one will be created just for them.
        """
        await ctx.trigger_typing()

        chann = ctx.guild.get_channel(channel_id)

        if not chann:
            await ctx.send(":x: You have provided a non-existing or bad Channel ID.")

        elif not isinstance(chann, VoiceChannel):
            await ctx.send(":x: Rooms creation channel must be a **Voice Channel**!")

        elif isinstance(chann, VoiceChannel):
            async with self.bot.pg.pool.acquire() as conn:
                query = "UPDATE guilds SET main_vc_id = $1 WHERE guild_id = $2;"
                await conn.execute(query, chann.id, ctx.guild.id)

                await self.bot.cache.refresh(ctx.guild.id)

            await ctx.send(f":ok_hand: Rooms creation channel was set to **{chann.name}** (`{chann.id}`).")


def setup(bot):
    bot.add_cog(Admin(bot))
