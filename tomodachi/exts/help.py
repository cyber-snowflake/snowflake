#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import io
import itertools
from typing import Union, List

import discord
from discord.ext import commands

from tomodachi.core.bot import Tomodachi
from tomodachi.core.context import TomodachiContext

# Type alias for a commands mapping, quite helpful
Commands = List[Union[commands.Command, commands.Group]]


class TomodachiHelpCommand(commands.MinimalHelpCommand):
    context: TomodachiContext

    def __init__(self, **options):
        super().__init__(**options, command_attrs=dict(hidden=True))
        self._e_colour = 0x2F3136

    async def send_pages(self):
        e = discord.Embed(colour=self._e_colour)
        e.description = "".join(self.paginator.pages)

        await self.get_destination().send(embed=e)

    def format_command(self, command: Union[commands.Command, commands.Group]):
        fmt = "`{0}{1}` — {2}\n" if command.short_doc else "`{0}{1}`\n"
        return fmt.format(self.clean_prefix, command.qualified_name, command.short_doc)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(colour=self._e_colour)
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        embed.description = self.get_opening_note()

        def get_category(command):
            _cog = command.cog
            return _cog.qualified_name if _cog is not None else "Uncategorized"

        filtered: Commands = await self.filter_commands(self.context.bot.commands, sort=True, key=get_category)
        groups = itertools.groupby(filtered, key=get_category)

        for category, _commands in groups:
            _commands = sorted(_commands, key=lambda c: len(c.name))
            embed.add_field(name=category, value=" ".join(f"`{c.qualified_name}`" for c in _commands), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        buff = io.StringIO()
        embed = discord.Embed(colour=self._e_colour)
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)

        if note := self.get_opening_note():
            buff.writelines([note, "\n\n", f"**{group} commands:**\n"])

        filtered: Commands = await self.filter_commands(group.commands, sort=True)

        if filtered:
            for command in filtered:
                buff.write(self.format_command(command))

        if buff.seekable():
            buff.seek(0)

        embed.description = buff.getvalue()

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(title=self.get_command_signature(command))
        embed.colour = self._e_colour

        if command.help:
            embed.description = f"{self.context.bot.icon('rich_presence')} {command.help}"

        if cooldown := command._buckets._cooldown:  # noqa
            embed.add_field(name="Cooldown", value=f"{self.context.bot.icon('slowmode')} {int(cooldown.per)} seconds")

        if command.aliases:
            aliases = (f"`{alias}`" for alias in command.aliases)
            embed.add_field(name="Aliases", value=" ".join(aliases))

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(colour=self._e_colour)
        embed.title = f"{self.context.bot.icon('question')} {error}"

        await self.get_destination().send(embed=embed)


class TomodachiHelp(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = TomodachiHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(TomodachiHelp(bot))
