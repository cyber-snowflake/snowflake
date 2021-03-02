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
from tomodachi.utils import run_in_executor


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


def setup(bot):
    bot.add_cog(Tools(bot))
