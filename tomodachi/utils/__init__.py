from collections import defaultdict

import discord

from .cache_v2 import *  # noqa
from .checks import *  # noqa
from .converters import *  # noqa
from .decos import *  # noqa
from .emojis import *  # noqa
from .sql import *  # noqa
from .wand_helpers import *  # noqa


_FLAGS_TO_HUMAN = {
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

FLAGS_TO_HUMAN = defaultdict(lambda: "Unknown Flags", _FLAGS_TO_HUMAN)


def make_progress_bar(position: float, total: float, *, length: int = 15, filler="█", emptiness=" ", in_brackets=False):
    bar = ""

    target_pos = (position * 100) / total

    for i in range(1, length + 1):
        i_pos = round(i * 100 / length)
        if i_pos <= target_pos:
            bar += filler
        else:
            bar += emptiness

    return bar if not in_brackets else f"[{bar}]"


def make_intents():
    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        invites=True,
        voice_states=True,
        presences=True,
        messages=True,
        reactions=True,
    )

    return intents
