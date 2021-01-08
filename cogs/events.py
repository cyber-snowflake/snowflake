import itertools

from discord import Activity, ActivityType, Guild
from discord.ext import commands, tasks
from loguru import logger

from bot import BigMommy


class Events(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot
        self.activities = itertools.cycle(
            [
                Activity(name=f"over {len(self.bot.users)} users", type=ActivityType.watching),
                Activity(name=f"with {len(self.bot.guilds)} guilds", type=ActivityType.playing),
            ]
        )

        self.cycle_activity.start()

    def cog_unload(self):
        self.cycle_activity.cancel()

    @tasks.loop(hours=1.0)
    async def cycle_activity(self):
        await self.bot.change_presence(activity=next(self.activities))

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
