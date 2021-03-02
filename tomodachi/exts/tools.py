#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io

import discord
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


def setup(bot):
    bot.add_cog(Tools(bot))
