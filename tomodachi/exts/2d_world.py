#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import discord
from discord.ext import commands

from tomodachi.core.bot import Tomodachi
from tomodachi.core.context import TomodachiContext
from tomodachi.core.menus import TomodachiMenu
from tomodachi.utils.apis import AniList, AniMedia, MediaType


class AniListMenu(TomodachiMenu):
    async def format_embed(self, media: AniMedia):
        self.embed.clear_fields()

        media_title = media.title.get("english") or media.title.get("romaji") or media.title.get("native")
        title = f"{media_title} ({self.current_index + 1}/{self.max_index + 1})"

        self.embed.title = title
        self.embed.url = media.url

        if media.cover_image.color:
            self.embed.colour = await commands.ColourConverter().convert(None, media.cover_image.color)
        else:
            self.embed.colour = 0x2F3136

        self.embed.description = media.description
        self.embed.timestamp = media.start_date or discord.Embed.Empty

        self.embed.set_image(url=media.banner_image or media.cover_image.large)

        if media.type is MediaType.ANIME:
            self.embed.add_field(name="Episodes", value=f"`{media.episodes}`")
            self.embed.add_field(name="Average duration", value=f"`{media.duration}` minutes")

        if media.type is MediaType.MANGA:
            self.embed.add_field(name="Volumes", value=f"`{media.volumes}`")
            self.embed.add_field(name="Chapters", value=f"`{media.chapters}`")

        if media.average_score is not None:
            self.embed.add_field(name="Average score", value=f"`{media.average_score}%`")
        else:
            self.embed.add_field(name="Mean score", value=f"`{media.mean_score}`%")

        if media.genres:
            self.embed.add_field(name="Genres", value=", ".join(media.genres))


class TwoDimWorld(commands.Cog, name="2D-World"):
    __anilist_notice = "Adult content is hidden from non-NSFW channels"

    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @commands.cooldown(1, 7.0, commands.BucketType.user)
    @commands.command(help="Searches for information about mangas on AniList", description=__anilist_notice)
    async def manga(self, ctx: TomodachiContext, *, query: str):
        async with ctx.typing():
            data = await AniList.lookup(query, MediaType.MANGA, hide_adult=not ctx.channel.is_nsfw())
            if not data:
                return await ctx.send(embed=discord.Embed(title=":x: Nothing was found!"))

            menu = AniListMenu(data)
            await menu.start(ctx)

    @commands.cooldown(1, 7.0, commands.BucketType.user)
    @commands.command(help="Searches for information about animes on AniList", description=__anilist_notice)
    async def anime(self, ctx: TomodachiContext, *, query: str):
        async with ctx.typing():
            data = await AniList.lookup(query, hide_adult=not ctx.channel.is_nsfw())
            if not data:
                return await ctx.send(embed=discord.Embed(title=":x: Nothing was found!"))

            menu = AniListMenu(data)
            await menu.start(ctx)


def setup(bot):
    bot.add_cog(TwoDimWorld(bot))
