import discord

from .cache_v2 import *  # noqa
from .checks import *  # noqa
from .converters import *  # noqa
from .decos import *  # noqa
from .emojis import *  # noqa
from .intents import *  # noqa
from .sql import *  # noqa
from .wand_helpers import *  # noqa


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
    intents = discord.Intents()

    intents.guilds = True
    intents.members = True
    intents.bans = True
    intents.emojis = True
    intents.invites = True
    intents.voice_states = True
    intents.presences = True
    intents.messages = True
    intents.reactions = True

    return intents
