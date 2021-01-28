import itertools

import discord
from discord.ext import commands

from bot import BigMommy
from src.myembed import MyEmbed


class Help(commands.Cog):
    def __init__(self, bot: BigMommy):
        self._bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self._bot.help_command = self._original_help_command


class MyHelpCommand(commands.MinimalHelpCommand):
    def __init__(self, **options):
        super().__init__(**options, command_attrs=dict(hidden=True))
        self.embed = MyEmbed()

    # Created this as property because pickle complains when it's an attribute idk why ¯\_(ツ)_/¯
    @property
    def bot(self) -> BigMommy:
        return self.context.bot

    def command_not_found(self, string):
        return f":x: Command `{string}` not found."

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Command `{command.qualified_name}` doesn't have subcommand named `{string}`."

        return f":x: Command `{command.qualified_name}` doesn't have any subcommands."

    async def send_error_message(self, error):
        destination = self.get_destination()
        self.embed.title = error
        await destination.send(embed=self.embed)

    def prepare_embed(self):
        self.embed.color = self.bot.config.brand_color
        self.embed.description = None
        self.embed.title = None
        self.embed.clear_fields()

    async def prepare_help_command(self, ctx, command):
        await ctx.trigger_typing()
        # i18n
        self.aliases_heading = "Aliases"  # Translator.translate("ALIASES", self.context)
        self.commands_heading = "Commands"  # Translator.translate("COMMANDS", self.context)
        # Original class methods
        self.paginator.clear()
        self.prepare_embed()
        await super().prepare_help_command(ctx, command)

    # Formatter for the embed
    def format_pages(self, **kwargs):
        if (title := kwargs.get("title", None)) is not None:
            self.embed.title = f"{title}"

        if (description := kwargs.get("description", None)) is not None:
            self.embed.description = description

    async def send_pages(self):
        destination = self.get_destination()

        if len(self.embed.fields) > 0 >= len(self.paginator.pages):
            await destination.send(embed=self.embed)
        else:
            for page in self.paginator.pages:
                self.embed.description = page
                await destination.send(embed=self.embed)

    def get_opening_note(self):
        return None

    def get_ending_note(self):
        return f"Use {self.context.prefix}help [command] or {self.context.prefix}help [module] to learn more."

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = ", ".join(f"`{c.name}`" for c in commands)
            self.embed.add_field(name=f"**{heading}**", value=joined, inline=False)

    def add_subcommand_formatting(self, command):
        fmt = "`{0}{1}`: {2}" if command.short_doc else "`{0}{1}`"
        self.paginator.add_line(fmt.format(self.clean_prefix, command.qualified_name, command.short_doc))

    def add_aliases_formatting(self, aliases):
        self.embed.add_field(name=f"{self.aliases_heading}", value=", ".join((f"`{alias}`" for alias in aliases)))

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        if cooldown := command._buckets._cooldown:
            self.embed.add_field(name="Cooldowns", value=f"{self.bot.my_emojis.slowmode} {int(cooldown.per)} seconds")

        signature = self.get_command_signature(command)
        if command.aliases:
            self.format_pages(title=signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.format_pages(title=signature)

        if command.help:
            try:
                self.paginator.add_line(f"{self.bot.my_emojis.rich_presence} {command.help}", empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        title = "Available commands"
        self.format_pages(title=title)

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        no_category = "\u200b{0.no_category}".format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, _commands in to_iterate:
            _commands = sorted(_commands, key=lambda c: c.name) if self.sort_commands else list(_commands)
            self.add_bot_commands_formatting(_commands, category)

        note = self.get_ending_note()
        if note:
            self.embed.set_footer(text=note)

        await self.send_pages()

    async def send_cog_help(self, cog):
        bot = self.context.bot
        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        if cog.description:
            self.paginator.add_line(cog.description, empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            self.format_pages(title="**%s %s**" % (cog.qualified_name, self.commands_heading))
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.embed.set_footer(text=note)

        await self.send_pages()

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            self.paginator.add_line("**%s**" % self.commands_heading)
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.embed.set_footer(text=note)

        await self.send_pages()

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages()

    async def command_callback(self, ctx, *, command=None):
        await self.prepare_help_command(ctx, command)
        bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = bot.get_cog(command.lower().title())
        if cog is not None:
            return await self.send_cog_help(cog)

        maybe_coro = discord.utils.maybe_coroutine

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = command.split(" ")
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            string = await maybe_coro(self.command_not_found, self.remove_mentions(keys[0]))
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)


def setup(bot):
    bot.add_cog(Help(bot))
