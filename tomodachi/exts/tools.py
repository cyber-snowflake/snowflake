#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io

import discord
from PIL import Image
from discord.ext import commands, menus
from gtts import gTTS

from tomodachi.core.bot import Tomodachi
from tomodachi.core.context import TomodachiContext
from tomodachi.utils import run_in_executor, AniList, AniMedia


class AniListMenu(menus.Menu):
    def __init__(self, data: list[AniMedia]):
        super().__init__(timeout=45.0, delete_message_after=False, clear_reactions_after=True)
        self.embed = discord.Embed()
        self.embed.set_footer(text="Powered by AniList.co")
        self.data = data
        self.current_index = 0
        self.max_index = len(data) - 1

    def increase_index(self):
        next_index = self.current_index + 1
        self.current_index = 0 if next_index > self.max_index else next_index

    def decrease_index(self):
        next_index = self.current_index - 1
        self.current_index = self.max_index if next_index < 0 else next_index

    async def format_embed(self, media: AniMedia):
        self.embed.clear_fields()

        media_title = media.title.get("english") or media.title.get("romaji") or media.title.get("native")
        title = f"{media_title} ({self.current_index + 1}/{self.max_index + 1})"

        self.embed.set_author(name=title, url=media.url)

        self.embed.colour = await commands.ColourConverter().convert(None, media.cover_image.color) or 0x2F3136
        self.embed.description = media.description
        self.embed.timestamp = media.start_date

        self.embed.set_image(url=media.banner_image or media.cover_image.large)

        self.embed.add_field(name="Episodes", value=f"`{media.episodes}`")
        self.embed.add_field(name="Mean score", value=f"`{media.mean_score}`")

        if media.genres:
            self.embed.add_field(name="Genres", value=", ".join(media.genres))

    async def send_initial_message(self, ctx, channel):
        await self.format_embed(self.data[0])
        return await channel.send(embed=self.embed)

    async def update_page(self):
        await self.format_embed(self.data[self.current_index])
        await self.message.edit(embed=self.embed)

    @menus.button("\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def on_double_arrow_left(self, _payload):
        if self.current_index != 0:
            self.current_index = 0
            await self.update_page()

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}")
    async def on_arrow_left(self, _payload):
        self.decrease_index()
        await self.update_page()

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, _payload):
        self.stop()

    @menus.button("\N{BLACK RIGHT-POINTING TRIANGLE}")
    async def on_arrow_right(self, _payload):
        self.increase_index()
        await self.update_page()

    @menus.button("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def on_double_arrow_right(self, _payload):
        if self.current_index != self.max_index:
            self.current_index = self.max_index
            await self.update_page()


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

    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.command(help="Performs anime lookup on AniList")
    async def anime(self, ctx: TomodachiContext, *, query: str):
        data = await AniList.lookup(query)
        menu = AniListMenu(data)

        await menu.start(ctx)


def setup(bot):
    bot.add_cog(Tools(bot))
