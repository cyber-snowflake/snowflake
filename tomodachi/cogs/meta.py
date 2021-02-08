from collections import Counter, OrderedDict
from typing import Generator, List, Optional, Union

import arrow
from discord import Activity, ActivityType, CustomActivity, Guild, Member, Permissions, Role, Spotify, User, utils
from discord.ext import commands

from tomodachi.core import Module
from tomodachi.src.myembed import MyEmbed
from tomodachi.utils import DUser, typing


class Meta(Module):
    flags_repr = {
        "staff": "Discord Staff",
        "partner": "Discord Partner",
        "hypesquad": "HypeSquad Events",
        "bug_hunter": "Discord Bug Hunter",
        "bug_hunter_level_2": "Discord Bug Hunter",
        "hypesquad_balance": "HypeSquad Balance",
        "hypesquad_brilliance": "HypeSquad Brilliance",
        "hypesquad_bravery": "HypeSquad Bravery",
        "early_supporter": "Early Supporter",
        "verified_bot": "Verified Bot",
        "verified_bot_developer": "Verified Bot Developer",
    }

    @classmethod
    def flag_humanize(cls, flag: str) -> Optional[str]:
        return cls.flags_repr.get(flag)

    @staticmethod
    def roles(guild: Guild, roles: List[Role]):
        for r in reversed(roles):
            if r.id != guild.id:
                yield r.mention

    @commands.command(aliases=("ui",))
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @typing()
    async def userinfo(self, ctx: commands.Context, user: DUser = None):
        """Shows information about discord users."""
        settings = await self.bot.cache.get(ctx.guild.id)

        user: Union[Member, User] = user or ctx.author
        avy_url = f'{user.avatar_url_as(static_format="png")}'

        embed = MyEmbed()
        embed.set_thumbnail(url=avy_url)
        embed.add_field(name="Discord Tag", value=f"{user}")
        embed.add_field(name="ID", value=f"{user.id}")
        embed.add_field(name="Avatar", value=f"[Image]({avy_url})")

        flags = ""
        if user.id == self.bot.owner.id:
            flags += f"{self.bot.my_emojis('owner')} **Bot Owner**\n"

        for flag in sorted(user.public_flags.all(), key=lambda x: x.value):
            flags += f"{self.bot.my_emojis(flag.name)} {self.flag_humanize(flag.name)}\n"

        if flags:
            embed.add_field(name="Flags", value=flags, inline=False)

        if isinstance(user, Member):
            member = user
            embed.colour = member.colour

            for activity in member.activities:
                if isinstance(activity, CustomActivity):
                    embed.add_field(name="Custom Status", value=f"{activity.name}", inline=False)

                if isinstance(activity, Spotify):
                    track_url = f"https://open.spotify.com/track/{activity.track_id}"
                    artists = " ,".join(activity.artists)
                    embed.add_field(
                        name="Listening to Spotify", value=f"[{artists} — {activity.title}]({track_url})", inline=False
                    )

                if isinstance(activity, Activity):
                    if activity.type == ActivityType.playing:
                        embed.add_field(name="Playing a game", value=f"{activity.name}", inline=False)

            if len(member.roles) > 1:
                embed.add_field(name="Roles", value=", ".join(self.roles(member.guild, member.roles)), inline=False)

            arrow_joined_at = arrow.get(member.joined_at).to(settings.tz)
            embed.add_field(
                name="Join date",
                inline=False,
                value=f"{self.bot.my_emojis('slowmode')} {arrow_joined_at.humanize()} (`{arrow_joined_at}`)",
            )

        arrow_created_at = arrow.get(user.created_at).to(settings.tz)
        embed.add_field(
            name="Account creation date",
            inline=False,
            value=f"{self.bot.my_emojis('slowmode')} {arrow_created_at.humanize()} (`{arrow_created_at}`)",
        )

        if user.id in self.bot.cache.blacklist:
            embed.colour = 0xFF0000
            embed.title = "This user is blacklisted from the bot."

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def me(self, ctx: commands.Context):
        """An alias to userinfo but shows info about you."""
        await ctx.invoke(self.userinfo)

    @commands.command(aliases=("spot", "spoti"))
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotify(self, ctx: commands.Context, member: Member = None):
        """Shows information about current Spotify track in one's status."""
        member = member or ctx.author

        spot = utils.find(lambda activity: isinstance(activity, Spotify), member.activities)

        if spot:
            track_url = f"https://open.spotify.com/track/{spot.track_id}"

            embed = MyEmbed(colour=0x1DB954)
            embed.set_thumbnail(url=spot.album_cover_url)
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")

            embed.add_field(name="Title", value=f"[{spot.title}]({track_url})")
            embed.add_field(name="Artists", value=", ".join(spot.artists))
            embed.add_field(name="Album", value=f"{spot.album}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f":x: **{member}** is not listening to Spotify.")

    @commands.command(aliases=("server", "si"))
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @typing()
    async def serverinfo(self, ctx: commands.Context, server_id: int = None):
        """Shows information summary about the server"""
        settings = await self.bot.cache.get(ctx.guild.id)

        server_id = server_id or ctx.guild.id
        guild: Guild = ctx.guild if server_id == ctx.guild.id else self.bot.get_guild(server_id)

        embed = MyEmbed(title=f"{guild.name} ({guild.id})")

        embed.set_thumbnail(url=guild.icon_url)
        if guild.discovery_splash_url:
            embed.set_image(url=guild.discovery_splash_url)

        embed.description = ""
        if guild.description:
            embed.description += f"{guild.description}\n"
        embed.description += (
            f"{self.bot.my_emojis('owner')} {guild.owner}\n"
            f"{self.bot.my_emoji('wump_flag')} {str(guild.region).replace('-', ' ').capitalize()}"
        )

        if guild.features:
            feature_cases = {
                "VIP_REGIONS": "VIP Voice Servers",
                "VANITY_URL": "Vanity URL",
                "INVITE_SPLASH": "Invite Splash",
                "VERIFIED": "Verified Server",
                "PARTNERED": "Partnered Server",
                "MORE_EMOJI": "More Emojis",
                "DISCOVERABLE": "Discovery",
                "FEATURABLE": "Featurable in discovery",
                "COMMERCE": "Commerce",
                "PUBLIC": "Public Server",
                "NEWS": "News Channel",
                "BANNER": "Banner",
                "ANIMATED_ICON": "Animated Icon",
                "PUBLIC_DISABLED": "Can't be Public",
                "WELCOME_SCREEN_ENABLED": "Welcome Screen",
                "COMMUNITY": "Community Server",
                "MEMBER_VERIFICATION_GATE_ENABLED": "Membership Screening",
            }

            features = ""
            for feature in guild.features:
                if humanized_feature := feature_cases.get(feature):
                    features += f"{self.bot.my_emojis('rounded_check')} {humanized_feature}\n"
            embed.add_field(name="Features", value=features)

        members = Counter(str(m.status) for m in guild.members)
        members_field = (
            f"{self.bot.my_emojis('online')} {members['online']} "
            f"{self.bot.my_emojis('idle')} {members['idle']} "
            f"{self.bot.my_emojis('dnd')} {members['dnd']} "
            f"{self.bot.my_emojis('offline')} {members['offline']}\n"
            f"{self.bot.my_emojis('members')} Total: {guild.member_count}"
        )

        embed.add_field(name="Members", value=members_field)

        def walk_members_flags() -> Generator[str, None, None]:
            for m in guild.members:
                if m.bot is False:
                    for f in m.public_flags.all():
                        yield f"{f}".replace("UserFlags.", "")

        flags_field = ""
        sflags = Counter(walk_members_flags())
        for flag in OrderedDict(sflags.most_common()):
            flags_field += f"{self.bot.my_emojis(flag)} {sflags[flag]} "

        if flags_field:
            embed.add_field(name="Badges Stats", value=flags_field, inline=False)

        created_at = arrow.get(guild.created_at).to(settings.tz)
        embed.add_field(
            name="Server creation date",
            value=f"{self.bot.my_emojis('slowmode')} {created_at.humanize()} (`{created_at}`)",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def botinfo(self, ctx: commands.Context):
        perms = Permissions()
        perms.add_reactions = True
        perms.attach_files = True
        perms.change_nickname = True
        perms.connect = True
        perms.embed_links = True
        perms.external_emojis = True
        perms.manage_channels = True
        perms.move_members = True
        perms.read_messages = True
        perms.read_message_history = True
        perms.send_messages = True
        perms.speak = True
        perms.manage_permissions = True

        inv_url = utils.oauth_url(self.bot.user.id, perms)

        e = MyEmbed()
        e.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar_url)
        e.add_field(name="Bot Dev", value=f"{self.bot.owner}")
        e.add_field(name="Invite", value=f"[Click to invite]({inv_url})")

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Meta(bot))
