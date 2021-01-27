from typing import Optional

from discord.ext import commands

from bot import BigMommy


class MyContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.bot: Optional[BigMommy] = attrs.pop("bot", None)  # yep yep, did it for type hinting
