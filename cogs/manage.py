from discord import VoiceChannel, Member, CategoryChannel, PermissionOverwrite, VoiceState
from discord.ext import commands

from bot import BigMommy
from utils.checks import is_in_voice
from utils.exceptions import RoomNotFound


class RoomsManager(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_vc_join(self, member: Member, _: VoiceState, after: VoiceState):
        guild = member.guild

        if after.channel is not None:
            settings = await self.bot.cache.settings(guild.id)

            # Detects connections into rooms creator channel of the guild
            if after.channel.id == settings.main_vc_id:
                room = await self.create_temporary_room(member, after.channel.category)
                if room is not None:
                    await self.bot.cache.set_room_id(member.id, guild.id, room.id)

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_vc_leave(self, member: Member, before: VoiceState, after: VoiceState):
        guild = member.guild

        # Detects disconnections from channels
        if before.channel is not None:
            if before.channel != after.channel:
                room_id = await self.bot.cache.get_room_id(member.id, guild.id)
                if before.channel.id == room_id:
                    c = guild.get_channel(room_id)
                    # We better check if it's a voice channel, just in case
                    if isinstance(c, VoiceChannel):
                        try:
                            await c.delete(reason="Room owner left the channel.")
                        except:
                            raise
                        finally:
                            await self.bot.cache.del_room_id(member.id, guild.id)

    async def get_room(self, ctx: commands.Context):
        room_id = await self.bot.cache.get_room_id(ctx.author.id, ctx.guild.id)
        if not room_id:
            raise RoomNotFound() from None

        room: VoiceChannel = ctx.guild.get_channel(room_id)
        if not room:
            raise RoomNotFound() from None

        return room

    async def create_temporary_room(self, member: Member, category: CategoryChannel = None):
        """Creates the temporary voice channel"""
        name = f"🚪 {member.display_name}"
        overwrites = {
            member.guild.default_role: PermissionOverwrite(connect=False),
            member: PermissionOverwrite(connect=True, manage_channels=True),
            member.guild.me: PermissionOverwrite(
                connect=True, move_members=True, manage_channels=True, manage_permissions=True
            ),
        }

        room = await (category or member.guild).create_voice_channel(name, overwrites=overwrites, user_limit=2)
        await member.move_to(room, reason="Private room created")

        return room

    @is_in_voice()
    @commands.group()
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def room(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            room = self.bot.get_channel(await self.bot.cache.get_room_id(ctx.author.id, ctx.guild.id))
            if not room:
                return await ctx.send(":x: You don't have a private room!")

            await ctx.send(f":information_source: Your current private room is **{room.name}** (`{room.id}`)")

    @room.command()
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        """Makes your room locked/unlocked for everyone."""
        await ctx.trigger_typing()

        try:
            room = await self.get_room(ctx)
        except RoomNotFound:
            return await ctx.send(
                ":warning: It looks like you don't have a private room" " or your room channel doesn't exist!"
            )

        overwrites = room.overwrites_for(ctx.guild.default_role)
        overwrites.update(connect=(not dict(overwrites)["connect"]))

        await room.set_permissions(ctx.guild.default_role, overwrite=overwrites)

        if dict(overwrites)["connect"]:
            await ctx.send(":green_heart: Now everyone will be able to connect to your private room.")
        else:
            await ctx.send(":heart: Now no one will be able to connect to your private room.")

    @room.command()
    @commands.bot_has_guild_permissions(move_members=True)
    async def kick(self, ctx: commands.Context, target: Member):
        """Kicks a person from your room."""
        await ctx.trigger_typing()

        if target == ctx.author:
            return await ctx.send(":x: You can not kick yourself!")

        try:
            room = await self.get_room(ctx)
        except RoomNotFound:
            return await ctx.send(
                ":warning: It looks like you don't have a private room" " or your room channel doesn't exist!"
            )

        if target not in room.members:
            await ctx.send(":x: This person is not in your room.")
        else:
            await target.move_to(None, reason="Requested by a room owner.")
            await ctx.send(f":ok_hand: I have kicked **{target}** (`{target.id}`) from your room.")


def setup(bot):
    bot.add_cog(RoomsManager(bot))
