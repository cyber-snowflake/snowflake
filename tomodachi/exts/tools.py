#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io

import discord
from PIL import Image
from discord.ext import commands
from gtts import gTTS

from tomodachi.core.bot import Tomodachi
from tomodachi.core.context import TomodachiContext
from tomodachi.core.menus import TomodachiMenu
from tomodachi.utils import run_in_executor, AniList, AniMedia


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
        self.embed.timestamp = media.start_date

        self.embed.set_image(url=media.banner_image or media.cover_image.large)

        self.embed.add_field(name="Episodes", value=f"`{media.episodes}`")
        self.embed.add_field(name="Average duration", value=f"`{media.duration}` minutes")
        self.embed.add_field(name="Mean score", value=f"`{media.mean_score}`")

        if media.genres:
            self.embed.add_field(name="Genres", value=", ".join(media.genres))


class Tools(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @staticmethod
    @run_in_executor
    def make_color_circle(color):
        buff = io.BytesIO()

        with Image.new("RGB", (256, 256), color) as im:
            im.save(buff, format="png")

        buff.seek(0)
        return buff

    @staticmethod
    @run_in_executor
    def make_text_to_speech(lang, text):
        buff = io.BytesIO()

        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(buff)

        buff.seek(0)
        return buff

    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.command(help="Transforms text data into speech")
    async def tts(self, ctx: TomodachiContext, language: str, *, text: str):
        try:
            buff = await self.make_text_to_speech(language, text)
        except ValueError:
            await ctx.send("Make sure you have provided correct language code.")
        else:
            file = discord.File(buff, "tts.mp3")
            await ctx.reply("Here's your requested text to speech!", file=file, mention_author=False)

    @commands.cooldown(1, 3.0, commands.BucketType.user)
    @commands.command(help="Shows information about colours")
    async def color(self, ctx: TomodachiContext, color: discord.Colour):
        buff = await self.make_color_circle(color.to_rgb())
        file = discord.File(buff, "color.png")

        embed = discord.Embed()
        embed.colour = color

        embed.add_field(name="HEX", value=f"{color}")
        embed.add_field(name="RGB", value=f"{color.to_rgb()}")

        embed.set_thumbnail(url="attachment://color.png")

        await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 7.0, commands.BucketType.user)
    @commands.command(help="Performs anime lookup on AniList")
    async def anime(self, ctx: TomodachiContext, *, query: str):
        async with ctx.typing():
            data = await AniList.lookup(query, hide_adult=not ctx.channel.is_nsfw())
            if not data:
                return await ctx.send(embed=discord.Embed(title=":x: Nothing was found!"))

            menu = AniListMenu(data)
            await menu.start(ctx)


def setup(bot):
    bot.add_cog(Tools(bot))
