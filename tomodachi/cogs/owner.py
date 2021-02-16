from typing import Optional

from asyncpg.exceptions import UniqueViolationError
from discord.ext import commands
from discord.ext.menus import MenuPages
from tabulate import tabulate

from tomodachi.core.module import Module
from tomodachi.src.exceptions import InformUser
from tomodachi.src.myembed import MyEmbed
from tomodachi.src.mymenus import GuildsPagesSource
from tomodachi.utils import DUser


class Owner(Module):
    async def cog_check(self, ctx: commands.Context):
        return await ctx.bot.is_owner(ctx.author)

    @commands.group()
    async def blacklist(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            raise InformUser("You haven't specified any subcommand.") from None

    @blacklist.command(name="add")
    async def blacklist_add(self, ctx: commands.Context, target: DUser, *, reason: Optional[str]):
        query = "INSERT INTO blacklisted (user_id) VALUES ($1);", target.id
        if reason:
            query = "INSERT INTO blacklisted (user_id, reason) VALUES ($1, $2);", target.id, reason

        try:
            async with self.bot.pg.pool.acquire() as conn:
                await conn.execute(*query)
        except UniqueViolationError:
            return await ctx.send(f":x: **{target}** (`{target.id}`) is already blacklisted from the bot.")

        await self.bot.cache.blacklist_refresh()
        await ctx.send(f":ok_hand: **{target}** (`{target.id}`) was blacklisted: `{reason}`")

    @blacklist.command(name="remove", aliases=("rmv", "del", "delete"))
    async def blacklist_remove(self, ctx: commands.Context, target: DUser):
        query = "DELETE FROM blacklisted WHERE user_id = $1 RETURNING user_id;", target.id

        async with self.bot.pg.pool.acquire() as conn:
            user_id = await conn.fetchval(*query)

        await self.bot.cache.blacklist_refresh()
        await ctx.send(f":ok_hand: **{target}** (`{target.id}`) is not blacklisted anymore")

    @commands.command()
    async def botstats(self, ctx: commands.Context):
        """Some statistics of the bot"""
        embed = MyEmbed(title="Bot Stats", footer_text="Requested by %s" % ctx.author)

        embed.add_field(name="Guilds", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Cached Users", value=f"{len(self.bot.users)}")
        embed.add_field(name="Average Latency", value=f"{round(self.bot.latency * 1000, 1)}ms")

        await ctx.send(embed=embed)

    @commands.group(aliases=("guild",))
    async def guilds(self, ctx: commands.Context):
        """Owner manipulations with guilds"""
        if not ctx.invoked_subcommand:
            await ctx.send("see help bro")

    @guilds.command(aliases=("ls",))
    async def guild_list(self, ctx: commands.Context):
        """Shows a table of Guild ID and Guild Owner"""
        rows = ((f"{guild.id}", f"{guild.owner.id}") for guild in self.bot.guilds)
        table = tabulate(rows, headers=("Guild ID", "Owner ID"), tablefmt="fancy_grid")

        src = GuildsPagesSource(table.splitlines(), per_page=10)
        menu = MenuPages(src, delete_message_after=True)

        await menu.start(ctx)


def setup(bot):
    bot.add_cog(Owner(bot))
