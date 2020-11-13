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

from discord.ext import commands
from discord.ext.menus import MenuPages
from tabulate import tabulate

from bot import BigMommy
from utils.myembed import MyEmbed
from utils.mymenus import GuildsPagesSource


class Owner(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await ctx.bot.is_owner(ctx.author)

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
