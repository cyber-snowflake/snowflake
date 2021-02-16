from discord.ext.commands import Cog

from . import Tomodachi


class Module(Cog):
    """Subclassed Cog just to reduce the amount of duplicate code"""

    def __init__(self, bot: Tomodachi):
        self.bot = bot
