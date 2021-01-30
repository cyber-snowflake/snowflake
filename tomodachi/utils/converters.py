import re
from datetime import timedelta
from typing import Union

from discord import HTTPException, Member, NotFound, User
from discord.ext.commands import BadArgument, Context, Converter
from discord.ext.commands.converter import MemberConverter, UserConverter

__all__ = ["TimeInput", "DUser"]


class TimeInput(Converter):
    async def convert(self, ctx: Context, argument: str) -> timedelta:
        argument = argument.lower()

        if not any(argument.endswith(t) for t in ("s", "m", "h", "d", "w")) or argument.startswith("-"):
            raise BadArgument("Bad timing input.") from None

        numbers = re.findall(r"\d+", argument)
        if not numbers:
            raise BadArgument("Bad timing input.") from None

        time_length = numbers[0]

        if argument.endswith("s"):
            return timedelta(seconds=int(time_length))

        elif argument.endswith("m"):
            return timedelta(minutes=int(time_length))

        elif argument.endswith("h"):
            return timedelta(hours=int(time_length))

        elif argument.endswith("d"):
            return timedelta(days=int(time_length))

        elif argument.endswith("w"):
            return timedelta(weeks=int(time_length))


class DUser(Converter):
    async def convert(self, ctx: Context, argument: str) -> Union[Member, User]:
        try:
            member: Member = await MemberConverter().convert(ctx=ctx, argument=argument)
            return member

        except BadArgument:
            try:
                user: User = await UserConverter().convert(ctx=ctx, argument=argument)
                return user

            except BadArgument:
                try:
                    int(argument)
                except ValueError:
                    raise BadArgument(f"{argument} is not a valid User ID", argument) from None

                try:
                    user: User = await ctx.bot.fetch_user(int(argument))
                except NotFound:
                    raise BadArgument("{0} not found".format(argument)) from None
                except HTTPException:
                    raise BadArgument("Fetching USER {0} failed".format(argument)) from None
                else:
                    return user
