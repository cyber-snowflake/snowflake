import re
from typing import Optional

from discord.ext.commands.errors import BadArgument
from src.regulars import IMAGE_EXTENSIONS
from discord.ext import commands
from discord import File

from bot import BigMommy
from src.decos import aioify
from wand.image import Image
import io


class Images(commands.Cog):
    def __init__(self, bot: BigMommy) -> None:
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def swirl(self, ctx: commands.Context, degrees: int = -90, url: Optional[str] = None):
        if not url:
            if not (a := ctx.message.attachments):
                fp = await ctx.author.avatar_url.read()
            else:
                fp = await a[0].read()
        else:
            if not re.search(IMAGE_EXTENSIONS, url):
                raise BadArgument("You must provide a png/jpg/webp image URL!") from None

            if not url.startswith("https://"):
                raise BadArgument("Image URL must use secure transfer protocol (https)!") from None

            resp = await self.bot.aiosession.get(url)
            fp = await resp.read()

        @aioify
        def run():
            buffer = io.BytesIO()

            with Image(blob=fp) as img:
                with img.convert("png") as converted:
                    converted.format = "png"
                    converted.swirl(degree=degrees)
                    converted.save(file=buffer)
                    buffer.seek(0)

            return buffer

        await ctx.trigger_typing()

        buffer = await run()
        _file = File(buffer, "result.png")

        await ctx.send(file=_file)


def setup(bot):
    bot.add_cog(Images(bot))
