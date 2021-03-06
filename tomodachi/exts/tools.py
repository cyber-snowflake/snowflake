#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
from typing import Union

import discord
import more_itertools as miter
from PIL import Image
from aiohttp import ClientResponseError
from discord.ext import commands
from gtts import gTTS

from tomodachi.core import Tomodachi, TomodachiContext, TomodachiMenu
from tomodachi.utils import to_thread

EmojiProxy = Union[discord.Emoji, discord.PartialEmoji]


class Tools(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @staticmethod
    @to_thread
    def make_color_circle(color):
        buff = io.BytesIO()

        with Image.new("RGB", (256, 256), color) as im:
            im.save(buff, format="png")

        buff.seek(0)
        return buff

    @staticmethod
    @to_thread
    def make_text_to_speech(lang, text):
        buff = io.BytesIO()

        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(buff)

        buff.seek(0)
        return buff

    @staticmethod
    async def get_image_url(message: discord.Message, user: Union[discord.Member, discord.User] = None):
        url = None

        if not message.attachments:
            if user is not None:
                url = str(user.avatar_url)
        else:
            url = message.attachments[0].url

        return url

    @commands.command()
    @commands.cooldown(1, 10.0, commands.BucketType.user)
    async def caption(self, ctx: TomodachiContext, user: Union[discord.Member, discord.User] = None):
        """Caption an image"""
        await ctx.trigger_typing()

        user = user or ctx.author
        image_url = await self.get_image_url(ctx.message, user)

        url = "https://captionbot.azurewebsites.net/api/messages"
        payload = {"Content": image_url, "Type": "CaptionRequest"}

        try:
            async with self.bot.session.post(url, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.text()

            e = discord.Embed(title="CaptionBot", description=str(data))
            e.set_image(url=image_url)

            await ctx.send(embed=e)

        except ClientResponseError:
            await ctx.send(":x: API request failed")

    @commands.guild_only()
    @commands.group(aliases=("emote", "e"), help="Group of emoji related commands")
    async def emoji(self, ctx: TomodachiContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command.qualified_name)

    @commands.cooldown(1, 10.0, commands.BucketType.channel)
    @emoji.command(name="list", aliases=("ls",), help="Spawns a menu with a list of emojis of this server")
    async def emoji_list(self, ctx: TomodachiContext):
        lines_chunks = miter.chunked([f"{e} | `{e}`" for e in ctx.guild.emojis], 10)
        pages = ["\n".join(lines) for lines in lines_chunks]

        menu = TomodachiMenu(pages, title=f"Emojis for {ctx.guild.name}")
        await menu.start(ctx)

    @commands.cooldown(1, 10.0, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.has_permissions(manage_emojis=True)
    @emoji.command(name="add", help="Adds new emoji to the server from attached images")
    async def emoji_add(self, ctx: TomodachiContext, name: str):
        if not ctx.message.attachments:
            raise commands.BadArgument("Emoji to upload was not provided as an argument or attachment")

        attachment = ctx.message.attachments[0]
        if attachment.size > 256000:
            return await ctx.send(":x: Your attachment exceeds 256kb file size limit!")

        b = await attachment.read()
        e = await ctx.guild.create_custom_emoji(name=name, image=b)

        await ctx.send(f"{e} has been uploaded")

    @commands.cooldown(1, 7.0, commands.BucketType.user)
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.has_permissions(manage_emojis=True)
    @emoji.command(name="grab", aliases=("steal", "reupload"), help="Steals emojis from other servers")
    async def emoji_grab(self, ctx: TomodachiContext, emojis: commands.Greedy[EmojiProxy]):
        c = 0

        for emoji in emojis:
            if isinstance(emoji, (discord.Emoji, discord.PartialEmoji)):
                if e_guild := getattr(emoji, "guild", None):
                    if e_guild.id == ctx.guild.id:
                        continue

                buff = await emoji.url.read()
                created_emoji = await ctx.guild.create_custom_emoji(name=emoji.name, image=buff)

                if created_emoji:
                    c += 1

        await ctx.send(f":ok_hand: Uploaded `{c}`/`{len(emojis)}` emojis.")

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
