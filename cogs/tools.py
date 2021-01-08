import random
import re
import sys
from io import BytesIO
from src.exceptions import InformUser
from utils.checks import is_manager_or_bot_owner

from aiohttp import FormData
from discord import Attachment, File
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from discord.mentions import AllowedMentions
from discord.message import Message
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
        try:
            tts = gTTS(text, lang=detected_language)
        except:
            raise InformUser(":x: Well, language detection failed ¯\\_(ツ)_/¯", reply=True)

        tts.write_to_fp(fp)
        fp.seek(0)

        return fp

    @commands.command(aliases=("winner", "winners", "choose_winners"))
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_manager_or_bot_owner()
    async def choose_winner(self, ctx: commands.Context, message_id: int, winners: int = 1):
        """Randomly selects someone who reacted with 🎉 on message of your choice"""
        try:
            m: Message = await ctx.fetch_message(message_id)
        except (NotFound, Forbidden):
            return await ctx.reply(f":x: Couldn't retrive message ID `{message_id}`")

        reactions = tuple(r for r in m.reactions if r.emoji == "🎉")
        if not reactions:
            return await ctx.reply(":x: There's no one who reacted with :tada: on this message!")

        participants = await reactions[0].users().flatten()
        winner = random.choice(participants)

        await ctx.send(
            f":sparkles: {winner.mention} wins! Congratulations!",
            allowed_mentions=AllowedMentions(users=True),
            reference=m,
        )

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
