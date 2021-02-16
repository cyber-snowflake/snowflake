import logging
from collections import defaultdict
from functools import cache
from typing import Callable, Iterable

from discord import Emoji

from tomodachi.src.singleton import MetaSingleton

__all__ = ["Emojis"]


def default_emoji_factory():
    return "\U0001f614"


class Emojis(metaclass=MetaSingleton):
    __slots__ = ("_emojis",)

    def __init__(self):
        self._emojis = None

    @cache
    def __call__(self, name: str):
        """Gets an emoji by name, if not found default emoji will be used"""
        return self._emojis[name]

    def setup(self, emojis: Iterable[Emoji], *, default_emoji: Callable = None):
        factory = default_emoji or default_emoji_factory
        self._emojis = defaultdict(factory)

        for emoji in set(emojis):
            self._emojis[emoji.name] = emoji

        logging.info("~ Custom Emojis initiated.")
