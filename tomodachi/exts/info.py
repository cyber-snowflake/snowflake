#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
from datetime import datetime
from typing import Union

import discord
import humanize
from discord.ext import commands, flags

from tomodachi.core import Tomodachi, TomodachiContext
from tomodachi.utils import make_progress_bar, HUMAN_READABLE_FLAGS, HUMANIZED_ACTIVITY


class Info(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @flags.add_flag("--steal", "-s", action="store_true")
    @commands.command(cls=flags.FlagCommand, aliases=("avy", "av"), help="Provides you an avatar of some discord user")
    async def avatar(self, ctx: TomodachiContext, user: discord.User = None, **options):
        user = user or ctx.author

        urls = " | ".join(f"[{ext}]({user.avatar_url_as(format=ext)})" for ext in ("png", "jpeg", "webp"))
        if user.is_avatar_animated():
            urls += f" | [gif]({user.avatar_url_as(format='gif')})"

        embed = discord.Embed(
            colour=0x2F3136,
            description=urls,
            title=f"{user} ({user.id})",
        )
        embed.set_image(url=f"{user.avatar_url}")

        if not options["steal"]:
            return await ctx.send(embed=embed)

        filename = "{}.{}".format(user.id, "png" if not user.is_avatar_animated() else "gif")
        asset = user.avatar_url_as(static_format="png")

        buf = io.BytesIO()
        await asset.save(buf)

        f = discord.File(buf, filename)

        await ctx.send(content=f"Re-uploaded avatar of {user} (`{user.id}`)", file=f)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=("ui", "memberinfo", "mi"), help="Shows general information about discord users")
    async def userinfo(self, ctx: TomodachiContext, user: Union[discord.Member, discord.User] = None):
        # if target user not specified use author
        user = user or ctx.author

        embed = discord.Embed(colour=0x2F3136)
        embed.set_thumbnail(url=f"{user.avatar_url}")

        embed.add_field(name="Username", value=f"{user}")
        embed.add_field(name="ID", value=f"{user.id}")

        if user.public_flags.value > 0:
            embed.add_field(
                inline=False,
                name="Badges",
                value="\n".join(
                    f"{self.bot.icon(f.name)} {HUMAN_READABLE_FLAGS[f.name]}" for f in user.public_flags.all()
                ),
            )

        if isinstance(user, discord.Member):
            embed.colour = user.colour

            for activity in user.activities:
                if isinstance(activity, discord.Spotify):
                    track_url = f"https://open.spotify.com/track/{activity.track_id}"
                    artists = ", ".join(activity.artists)
                    value = f"[{artists} — {activity.title}]({track_url})"

                    embed.add_field(name="Listening", value=value, inline=False)

                else:
                    embed.add_field(name=f"{HUMANIZED_ACTIVITY[activity.type]}", value=f"{activity.name}", inline=False)

            roles = ", ".join(reversed(tuple(r.mention for r in user.roles if "everyone" not in r.name)))
            embed.add_field(name="Roles", value=roles or "None", inline=False)

            joined = "%s (`%s`)" % (humanize.naturaltime(datetime.utcnow() - user.joined_at), user.joined_at)
            embed.add_field(name="Join date", value=f"{self.bot.icon('slowmode')} {joined}", inline=False)

        created = "%s (`%s`)" % (humanize.naturaltime(datetime.utcnow() - user.created_at), user.created_at)
        embed.add_field(name="Creation date", value=f"{self.bot.icon('slowmode')} {created}", inline=False)

        await ctx.send(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=("spot",), help="Checks what discord user is listening to")
    async def spotify(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        activity = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)

        if not activity:
            return await ctx.send(f"{member} is not using Spotify right now.")

        track_url = f"https://open.spotify.com/track/{activity.track_id}"

        current_pos = datetime.utcnow() - activity.start
        bar = make_progress_bar(
            current_pos.seconds,
            activity.duration.seconds,
            length=18,
            in_brackets=True,
            emptiness="#",
        )
        elapsed = "%02d:%02d" % divmod(current_pos.seconds, 60)
        duration = "%02d:%02d" % divmod(activity.duration.seconds, 60)
        progression = f"{elapsed} `{bar}` {duration}"

        e = discord.Embed(colour=0x1ED760)
        e.set_author(name=f"{ctx.author.name}", icon_url=self.bot.icon("spotify").url)
        e.add_field(name="Title", value=f"[{activity.title}]({track_url})")
        e.add_field(name="Artists", value=", ".join(activity.artists))
        e.add_field(name="Album", value=f"{activity.album}")
        e.add_field(name="Player", value=progression, inline=False)
        e.set_image(url=activity.album_cover_url)

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Info(bot))
