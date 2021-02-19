import random
import re
from typing import Optional, Union

from discord import Attachment, File, Member, User
from discord.ext import commands

from tomodachi import utils
from tomodachi.core.module import Module
from tomodachi.src.exceptions import InformUser
from tomodachi.src.regulars import IMAGE_EXTENSIONS
from tomodachi.utils import executor, loading


class Images(Module):
    async def get_img_bytes(self, attachments: list[Attachment], _obj: Optional[Union[User, Member, str]]) -> bytes:
        if len(attachments) > 0:
            fp: bytes = await attachments[0].read()
            return fp

        else:
            if isinstance(_obj, User) or isinstance(_obj, Member):
                fp = await _obj.avatar_url_as(format="png", size=1024).read()
                return fp

            elif isinstance(_obj, str):
                if not re.search(IMAGE_EXTENSIONS, _obj):
                    raise InformUser("You must provide a png/jpg/webp image URL!", reply=True) from None

                if not _obj.startswith("https://"):
                    raise InformUser("Image URL must use secure transfer protocol (https)!", reply=True) from None

                resp = await self.bot.aiosession.get(_obj)
                fp = await resp.read()

                return fp

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @loading
    async def magik(self, ctx: commands.Context, user_or_url: Optional[Union[User, Member, str]] = None):
        """Woosh! It's a magik..."""
        fp = await self.get_img_bytes(ctx.message.attachments, user_or_url or ctx.author)

        @executor
        def run():
            with utils.WandImage(blob=fp) as orig:
                with orig.convert("png") as img:
                    img.adaptive_sharpen(radius=8, sigma=4)
                    for amount in (random.uniform(0.1, 0.8), random.uniform(1.2, 1.9)):
                        img.liquid_rescale(
                            width=int(img.width * amount),
                            height=int(img.height * amount),
                            delta_x=1,
                            rigidity=0,
                        )
                    img.resize(*orig.size)

                    stream = img.to_bin_stream()
            return stream

        image = await run()
        _file = File(image, "magik.png")

        await ctx.send(file=_file)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @loading
    async def implode(
        self, ctx: commands.Context, amount: float = 0.35, user_or_url: Optional[Union[User, Member, str]] = None
    ):
        """Apply implode effect to an image

        If no url is provided, your avatar will be used.
        Please, note that URLs must be secure and end with .png/.jpg"""
        fp = await self.get_img_bytes(ctx.message.attachments, user_or_url or ctx.author)

        @executor
        def run():
            with utils.WandImage(blob=fp) as orig:
                with orig.convert("png") as img:
                    img.implode(amount=amount)

                    stream = img.to_bin_stream()
            return stream

        image = await run()
        _file = File(image, "result.png")

        await ctx.send(file=_file)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @loading
    async def swirl(
        self, ctx: commands.Context, degrees: int = -90, user_or_url: Optional[Union[User, Member, str]] = None
    ):
        """Apply swirl effect to an image

        If no url is provided, your avatar will be used.
        Please, note that URLs must be secure and end with .png/.jpg"""
        fp = await self.get_img_bytes(ctx.message.attachments, user_or_url or ctx.author)

        @executor
        def run():
            with utils.WandImage(blob=fp) as orig:
                with orig.convert("png") as img:
                    img.swirl(degree=degrees)

                    stream = img.to_bin_stream()
            return stream

        image = await run()
        _file = File(image, "result.png")

        await ctx.send(file=_file)

    @commands.group()
    async def blur(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            raise InformUser("You have to specify a subcommand, see help.")

    @blur.command()
    @loading
    async def normal(
        self,
        ctx: commands.Context,
        radius: int = 0,
        sigma: int = 3,
        user_or_url: Optional[Union[User, Member, str]] = None,
    ):
        """Basic blur operation. The radius argument defines the size of the area to sample, and the sigma defines the standard deviation. For all blur based methods, the best results are given when the radius is larger than sigma."""  # noqa
        fp = await self.get_img_bytes(ctx.message.attachments, user_or_url or ctx.author)

        @executor
        def run():
            with utils.WandImage(blob=fp) as orig:
                with orig.convert("png") as img:
                    img.blur(radius=radius, sigma=sigma)

                    stream = img.to_bin_stream()
            return stream

        image = await run()
        _file = File(image, "blur.png")

        await ctx.send(file=_file)

    @blur.command()
    @loading
    async def adaptive(
        self,
        ctx: commands.Context,
        radius: int = 8,
        sigma: int = 4,
        user_or_url: Optional[Union[User, Member, str]] = None,
    ):
        """Blurs less intensely around areas of an image with detectable edges, and blurs more intensely for areas without edges. The radius should always be larger than the sigma (standard deviation)."""  # noqa
        fp = await self.get_img_bytes(ctx.message.attachments, user_or_url or ctx.author)

        @executor
        def run():
            with utils.WandImage(blob=fp) as orig:
                with orig.convert("png") as img:
                    img.adaptive_blur(radius=radius, sigma=sigma)

                    stream = img.to_bin_stream()
            return stream

        image = await run()
        _file = File(image, "adaptive_blur.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Images(bot))
