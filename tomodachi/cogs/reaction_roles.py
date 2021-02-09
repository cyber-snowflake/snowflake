from discord import RawReactionActionEvent, Guild, Member

from tomodachi.core import Module


class ReactionRoles(Module):
    @Module.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if not payload.member:
            return

        member: Member = payload.member
        guild: Guild = member.guild

        async with self.bot.pg.pool.acquire() as conn:
            query = "SELECT * FROM reaction_roles WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3;"
            records = await conn.fetch(query, guild.id, payload.channel_id, payload.message_id)

        if not records:
            return

        roles = [guild.get_role(record["role_id"]) for record in records]
        for role in roles:
            if role not in member.roles:
                await member.add_roles(role, reason="Reaction role: add")


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
