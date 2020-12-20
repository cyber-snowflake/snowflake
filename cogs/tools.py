import re
import sys
from io import BytesIO

from aiohttp import FormData
from discord import Attachment, File
from discord.ext import commands
from gtts import gTTS
from polyglot.detect import Detector

from bot import BigMommy
from src.decos import executor
from src.regulars import IMGUR_EXTENSIONS


class Tools(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @staticmethod
    @executor
    def make_tts(text: str, *, language_code: str = None):
        """Generates TTS audio in bytes"""
        fp = BytesIO()

        detected_language = language_code or Detector(text, quiet=True).language.code
        tts = gTTS(text, lang=detected_language)

        tts.write_to_fp(fp)
        fp.seek(0)

        return fp

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tts(self, ctx: commands.Context, *, text: str):
        """Converts text into a speech"""
        await ctx.trigger_typing()

        if len(text) <= 4:
            return await ctx.send(":x: Your text is too short.")

        fp = await self.make_tts(text)
        file = File(fp, filename=f"{ctx.author} Text-To-Speech.mp3")

        if round((sys.getsizeof(fp) / 1048576), 2) > 5:
            return await ctx.send(":x: Resulting file bigger than 5 MB.")

        await ctx.reply(":sparkles: Here's your tts!", file=file)

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def imgur(self, ctx: commands.Context):
        """Upload an image from discord to imgur"""
        attachment: Attachment = a[0] if len(a := ctx.message.attachments) > 0 else None

        if not attachment:
            raise commands.BadArgument("No attachements detected") from None

        if not re.findall(IMGUR_EXTENSIONS, attachment.filename):
            raise commands.BadArgument("Attachemnt type must be an image") from None

        await ctx.trigger_typing()

        fp = await attachment.read()

        headers = {"Authorization": f"Client-ID {self.bot.config.Bot.imgur_id}"}

        data = FormData()
        data.add_field("image", fp)

        request = await self.bot.aiosession.post("https://api.imgur.com/3/image", headers=headers, data=data)
        _json = await request.json()

        await ctx.reply(f":frame_photo: Uploaded to Imgur: <{_json['data']['link']}>")


def setup(bot):
    bot.add_cog(Tools(bot))
