import re

from aiohttp import FormData
from discord import Attachment
from discord.ext import commands

from bot import BigMommy

IMGUR_EXTENSIONS = re.compile(r"\.(gif|jpe?g|tiff?|a?png|webp|bmp)$", re.IGNORECASE)


class Tools(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @commands.command()
    async def imgur(self, ctx: commands.Context):
        """Upload an image from discord to imgur"""
        attachment: Attachment = a[0] if len(a := ctx.message.attachments) > 0 else None

        if not attachment:
            raise commands.BadArgument("No attachements detected") from None

        if not re.findall(IMGUR_EXTENSIONS, attachment.filename):
            raise commands.BadArgument("Attachemnt type must be an image") from None

        fp = await attachment.read()

        headers = {"Authorization": f"Client-ID {self.bot.config.Bot.imgur_id}"}

        data = FormData()
        data.add_field("image", fp)

        request = await self.bot.aiosession.post("https://api.imgur.com/3/image", headers=headers, data=data)
        _json = await request.json()

        await ctx.send(f":frame_photo: Uploaded to Imgur: <{_json['data']['link']}>")


def setup(bot):
    bot.add_cog(Tools(bot))
