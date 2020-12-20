from discord import Member
from discord.ext import commands

from src.exceptions import NotInVoiceChat


def is_manager_or_bot_owner():
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.author, Member):
            author: Member = ctx.author

            if author.id == ctx.bot.owner_id or author.guild_permissions.manage_guild:
                return True
            else:
                raise commands.CheckFailure(f"{author.id} is not allowed to run {ctx.command.qualified_name}") from None

    return commands.check(predicate=predicate)


def is_in_voice():
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.author, Member):
            if ctx.author.voice is not None:
                return True
            else:
                raise NotInVoiceChat(f"{ctx.author.id} is not in voice chat.", ctx.author) from None

    return commands.check(predicate)
