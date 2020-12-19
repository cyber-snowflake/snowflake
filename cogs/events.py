from discord import Guild, Message, Member
from discord.ext import commands

from bot import BigMommy


class Events(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        await self.bot.pg.add_guild(guild.id)


def setup(bot):
    bot.add_cog(Events(bot))
