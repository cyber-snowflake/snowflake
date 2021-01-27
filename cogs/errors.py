import traceback

from discord import Forbidden, TextChannel, Embed
from discord.ext import commands
from loguru import logger

from bot import BigMommy
from src.exceptions import BlacklistedUser, InformUser, NotInVoiceChat


class ErrorHandler(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot
        self.ignored = (BlacklistedUser, commands.CommandNotFound)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """
        ctx   : Context
        error : Exception
        """
        label = ctx.command.qualified_name if ctx.command else None

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, self.ignored):
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.send(":x: Maximum concurrency reached! Try again later.")

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id == self.bot.owner_id:
                return await ctx.reinvoke()

            return await ctx.send(
                f":warning: Please, wait {round(error.retry_after, 2)} seconds before using this command.",
                delete_after=10,
            )

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"`{ctx.command}` is disabled.")

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(":x: This command can only be executed from a server.")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(":lock: You don't have enough permissions to run this command.")

        elif isinstance(error, commands.errors.NotOwner):
            return await ctx.send(":lock: You don't have enough permissions to run this command.")

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(":lock: You don't have enough permissions to run this command.")

        elif isinstance(error, NotInVoiceChat):
            return await ctx.send(":x: You must be in a voice channel to run this command.")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                f":warning: You missed a required command argument!"
                f"\n:gear: Usage — {ctx.prefix}{label} {ctx.command.signature}"
            )

        elif isinstance(error, commands.BadArgument):
            if label == "userinfo":
                return await ctx.send(":x: You have provided an invalid User ID.")

            elif label == "serverinfo":
                return await ctx.send(":x: You have provided an invalid Server ID.")

            elif label == "reminder add":
                return await ctx.send(":x: You have provided an invalid length of time.")

            elif label == "imgur":
                return await ctx.send(":x: You have to send a command with an image or gif!")

            else:
                return await ctx.reply(
                    "Hey, it looks like you messed up some arguments in the command!\n"
                    f"Please, use `{ctx.prefix}help {label}` to learn more."
                )

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(
                ":x: I don't have enough permissions. "
                "Make sure you gave me those permissions: "
                ", ".join(error.missing_perms)
            )

        elif isinstance(error, Forbidden):
            return await ctx.send(":x: I don't have enough permissions.")

        elif isinstance(error, InformUser):
            if error.reply:
                return await ctx.reply(error.message)
            else:
                return await ctx.send(error.message)

        tb: str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(f"Ignoring exception in command {ctx.command}.")
        logger.exception(tb)

        e = Embed(color=0xFF0000, title="Unexpected Exception")
        e.add_field(name="Command", value=f"{ctx.message.content[0:1000]}")
        e.add_field(name="Author", value=f"{ctx.author} (`{ctx.author.id}`)")
        e.add_field(name="Guild", value="{}".format(f"{g.name} (`{g.id}`)" if (g := ctx.guild) else "None"))

        if u := self.bot.get_user(self.bot.owner_id):
            await u.send(embed=e, content=f"```\n{tb[0:2000]}\n```")

        if isinstance(ctx.channel, TextChannel):
            await ctx.channel.send(":x: Unexpected error! Traceback is sent to the bot developer.")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
