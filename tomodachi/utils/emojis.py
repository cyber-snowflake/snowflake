import logging
from collections import defaultdict
from functools import cache
from typing import Iterable, Union

from discord import Emoji

from tomodachi.src.singleton import MetaSingleton

__all__ = ["Emojis"]


class Emojis(metaclass=MetaSingleton):
    __slots__ = ("_emojis",)

    @staticmethod
    def _default_emoji_factory():
        return "\U0001f614"

    def __init__(self):
        self._emojis: defaultdict[str, Union[Emoji, str]] = defaultdict(self._default_emoji_factory)

    @cache
    def __call__(self, name: str):
        return str(self._emojis[name])

    def setup(self, emojis: Iterable[Emoji]):
        for emoji in set(emojis):
            self._emojis[emoji.name] = emoji

        logging.info("~ Custom Emojis initiated.")
