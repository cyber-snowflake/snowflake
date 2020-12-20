import re
from typing import Optional

from discord import File, Attachment, Asset
from discord.ext import commands
from discord.ext.commands.errors import BadArgument
from wand.image import Image

import utils
from bot import BigMommy
from src.decos import executor
from src.regulars import IMAGE_EXTENSIONS


class Images(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    async def get_image(self, attachments: list[Attachment], avatar_url: Asset, url: Optional[str]):
        if not url:
            if not attachments:
                fp = await avatar_url.read()
            else:
                fp = await attachments[0].read()
        else:
            if not re.search(IMAGE_EXTENSIONS, url):
                raise BadArgument("You must provide a png/jpg/webp image URL!") from None

            if not url.startswith("https://"):
                raise BadArgument("Image URL must use secure transfer protocol (https)!") from None

            resp = await self.bot.aiosession.get(url)
            fp = await resp.read()

        return fp

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def implode(self, ctx: commands.Context, amount: float = 0.35, url: Optional[str] = None):
        """Apply implode effect to an image

        If no url is provided, your avatar will be used.
        Please, note that URLs must be secure and end with .png/.jpg"""
        await ctx.trigger_typing()

        fp = await self.get_image(ctx.message.attachments, ctx.author.avatar_url, url)

        @executor
        def run():
            with Image(blob=fp) as img:
                with img.convert("png") as converted:
                    converted.implode(amount=amount)
                    _buffer = utils.img_to_buffer(converted)
            return _buffer

        image = await run()
        _file = File(image, "result.png")
        await ctx.send(file=_file)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def swirl(self, ctx: commands.Context, degrees: int = -90, url: Optional[str] = None):
        """Apply swirl effect to an image

        If no url is provided, your avatar will be used.
        Please, note that URLs must be secure and end with .png/.jpg"""
        await ctx.trigger_typing()

        fp = await self.get_image(ctx.message.attachments, ctx.author.avatar_url, url)

        @executor
        def run():
            with Image(blob=fp) as img:
                with img.convert("png") as converted:
                    converted.format = "png"
                    converted.swirl(degree=degrees)
                    _buffer = utils.img_to_buffer(converted)
            return _buffer

        buffer = await run()
        _file = File(buffer, "result.png")
        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Images(bot))
