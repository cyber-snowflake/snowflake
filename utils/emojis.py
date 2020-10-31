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

import logging
from collections import defaultdict
from typing import Iterable, Union

from discord import Emoji

from .singleton import MetaSingleton


class Emojis(metaclass=MetaSingleton):
    @staticmethod
    def _default_emoji_factory():
        return "\U0001f614"

    def __init__(self):
        self._emojis: defaultdict[str, Union[Emoji, str]] = defaultdict(self._default_emoji_factory)

    def setup(self, emojis: Iterable[Emoji]):
        for emoji in set(emojis):
            self._emojis[emoji.name] = emoji

        logging.info("~ Custom Emojis initiated.")

    def find_attr(self, query: str):
        """Simplified getattr for this emojis singleton class"""
        try:
            x = getattr(self, f"{query}")
        except AttributeError:
            return None
        else:
            return x

    @property
    def staff(self):
        return self._emojis["staff"]

    @property
    def partner(self):
        return self._emojis["partner"]

    @property
    def hypesquad(self):
        return self._emojis["hypesquad"]

    @property
    def bug_hunter(self):
        return self._emojis["bug_hunter"]

    @property
    def bug_hunter_level_2(self):
        return self._emojis["bug_hunter_level_2"]

    @property
    def verified_bot_developer(self):
        return self._emojis["verified_bot_developer"]

    @property
    def verified_bot(self) -> str:
        part1 = self._emojis["verified_bot1"]
        part2 = self._emojis["verified_bot2"]
        return f"{part1}{part2}"

    @property
    def hypesquad_brilliance(self):
        return self._emojis["hypesquad_brilliance"]

    @property
    def hypesquad_balance(self):
        return self._emojis["hypesquad_balance"]

    @property
    def hypesquad_bravery(self):
        return self._emojis["hypesquad_bravery"]

    @property
    def bot(self):
        return self._emojis["bot"]

    @property
    def early_supporter(self):
        return self._emojis["early_supporter"]

    @property
    def online(self):
        return self._emojis["online"]

    @property
    def dnd(self):
        return self._emojis["dnd"]

    @property
    def idle(self):
        return self._emojis["idle"]

    @property
    def offline(self):
        return self._emojis["offline"]

    @property
    def rounded_check(self):
        return self._emojis["roundedCheck"]

    @property
    def owner(self):
        return self._emojis["owner"]

    @property
    def members(self):
        return self._emojis["members"]

    @property
    def text_channel(self):
        return self._emojis["text_channel"]

    @property
    def voice_channel(self):
        return self._emojis["voice_channel"]

    @property
    def slowmode(self):
        return self._emojis["slowmode"]

    @property
    def game_metadata(self):
        return self._emojis["game_metadata"]

    @property
    def rich_presence(self):
        return self._emojis["rich_presence"]

    @property
    def wump_flag(self):
        return self._emojis["wump_flag"]
