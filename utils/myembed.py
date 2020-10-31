#  The MIT License (MIT)
#
#  Copyright (c) 2020 cyber-snowflake
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

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
        self.colour = kwargs.get("colour") or kwargs.get("color") or 0x7289DA

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
