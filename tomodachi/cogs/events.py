from discord import Guild
from discord.ext import commands
from loguru import logger

from tomodachi.core.module import Module


class Events(Module):
    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        await self.bot.pg.add_guild(guild.id)
        logger.info(
            f"Joined a {guild.name} ({guild.id}) with {guild.member_count} members, owned by {guild.owner} ({guild.owner_id})"  # noqa
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        logger.info(f"Left a guild {guild.name} ({guild.id})")


def setup(bot):
    bot.add_cog(Events(bot))
