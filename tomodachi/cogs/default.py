import asyncio

from discord import Member, Message
from discord.ext import commands

from tomodachi.core.module import Module


class Default(Module):
    @commands.command(hidden=True)
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hi, I'm {self.bot.user.name} and I'm a bot.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def clown(self, ctx: commands.Context, target: Member):
        def check(m):
            return m.author.id == target.id

        try:
            m: Message = await self.bot.wait_for("message", timeout=120.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            await m.add_reaction("🤡")


def setup(bot):
    bot.add_cog(Default(bot))
