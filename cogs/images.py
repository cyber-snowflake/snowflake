import random
import re
from typing import Optional

from discord import Asset, Attachment, File
from discord.ext import commands
from wand.image import Image
from src.exceptions import InformUser

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
                raise InformUser("You must provide a png/jpg/webp image URL!") from None

            if not url.startswith("https://"):
                raise InformUser("Image URL must use secure transfer protocol (https)!") from None

            resp = await self.bot.aiosession.get(url)
            fp = await resp.read()

        return fp

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def magik(self, ctx: commands.Context, url: Optional[str] = None):
        """Woosh! It's a magik..."""
        await ctx.trigger_typing()

        fp = await self.get_image(ctx.message.attachments, ctx.author.avatar_url, url)

        @executor
        def run():
            with Image(blob=fp) as img:
                with img.convert("png") as img:
                    for amount in (random.uniform(0.1, 0.8), random.uniform(1.2, 1.9)):
                        img.liquid_rescale(
                            width=int(img.width * amount),
                            height=int(img.height * amount),
                            delta_x=1,
                            rigidity=0,
                        )
                    img.adaptive_sharpen(radius=8, sigma=4)
                    _buffer = utils.img_to_buffer(img)
            return _buffer

        image = await run()
        _file = File(image, "magik.png")
        await ctx.send(file=_file)

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
