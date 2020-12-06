from discord import Guild, Message, Member
from discord.ext import commands

from bot import BigMommy


class Events(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        await self.bot.pg.add_guild(guild.id)

    @commands.Cog.listener(name="on_message")
    async def count_messages(self, message: Message):
        uid = message.author.id

        async with self.bot.pg.pool.acquire() as conn:
            query = "INSERT INTO users_stats (user_id, messages_sent) VALUES ($1, 1) " \
                    "ON CONFLICT (user_id) DO UPDATE SET messages_sent = users_stats.messages_sent + 1;"

            await conn.execute(query, uid)

            if g := message.guild:
                query = "INSERT INTO guilds_stats (guild_id, messages_sent) VALUES ($1, 1) " \
                        "ON CONFLICT (guild_id) DO UPDATE SET messages_sent = guilds_stats.messages_sent + 1;"

                await conn.execute(query, g.id)

    @commands.Cog.listener(name="on_member_join")
    async def count_members(self, member: Member):
        gid = member.guild.id

        async with self.bot.pg.pool.acquire() as conn:
            query = "INSERT INTO guilds_stats (guild_id, members_joined) VALUES ($1, 1) " \
                    "ON CONFLICT (guild_id) DO UPDATE SET members_joined = guilds_stats.members_joined + 1;"

            await conn.execute(query, gid)


def setup(bot):
    bot.add_cog(Events(bot))
