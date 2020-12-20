from datetime import datetime
from typing import Optional, Union

import arrow
import discord


class MyEmbed(discord.Embed):
    def __init__(
        self,
        *,
        timestamp: Union[datetime, arrow.Arrow, bool] = False,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # This will use Discord's brand colour by default if no other colour was passed
        self.colour = kwargs.get("colour") or kwargs.get("color") or 0xDD3B64

        # Checks what time type was passed and decides what to use
        if isinstance(timestamp, bool):
            if timestamp is True:
                self.timestamp = arrow.utcnow().datetime
            else:
                pass

        elif isinstance(timestamp, datetime):
            self.timestamp = timestamp

        elif isinstance(timestamp, arrow.Arrow):
            self.timestamp = timestamp.datetime

        # Setting footer
        self.set_footer(
            text=footer_text or discord.embeds.EmptyEmbed, icon_url=footer_icon or discord.embeds.EmptyEmbed
        )
