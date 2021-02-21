#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from typing import Optional

import discord as dc
from discord.ext import commands

from tomodachi.core.bot import Tomodachi
from tomodachi.utils import make_progress_bar


class Info(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotify(self, ctx, member: Optional[dc.Member] = None):
        member = member or ctx.author
        activity = dc.utils.find(lambda a: isinstance(a, dc.Spotify), member.activities)

        if not activity:
            return await ctx.send(f"{member} is not using Spotify right now.")

        track_url = f"https://open.spotify.com/track/{activity.track_id}"

        current_pos = datetime.utcnow() - activity.start
        bar = make_progress_bar(
            current_pos.seconds,
            activity.duration.seconds,
            length=16,
            in_brackets=True,
            emptiness="#",
        )
        elapsed = "%02d:%02d" % divmod(current_pos.seconds, 60)
        duration = "%02d:%02d" % divmod(activity.duration.seconds, 60)
        progression = f"{elapsed} `{bar}` {duration}"

        e = dc.Embed(colour=0x1ED760)
        # todo: add set_author with spotify logo
        e.add_field(name="Title", value=f"[{activity.title}]({track_url})")
        e.add_field(name="Artists", value=", ".join(activity.artists))
        e.add_field(name="Album", value=f"{activity.album}")
        e.add_field(name="Player", value=progression, inline=False)
        e.set_image(url=activity.album_cover_url)

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Info(bot))
