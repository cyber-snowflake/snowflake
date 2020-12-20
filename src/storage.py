import sys
from typing import MutableMapping, Optional, Dict, Union

from src.types import GuildSettings


class InternalStorage(MutableMapping):
    __slots__ = ("__data",)

    def __init__(self) -> None:
        self.__data: Dict[Union[int, str], Union[GuildSettings, int]] = {}

    def __setitem__(self, k, v) -> None:
        if isinstance(k, str):
            k = sys.intern(k)

        if isinstance(v, str):
            v = sys.intern(v)

        self.__data[k] = v

    def __delitem__(self, k) -> None:
        if isinstance(k, str):
            k = sys.intern(k)

        del self.__data[k]

    def __getitem__(self, k) -> Optional[Union[GuildSettings, int]]:
        if isinstance(k, str):
            k = sys.intern(k)

        try:
            return self.__data[k]
        except KeyError:
            return None

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __repr__(self):
        return "<InternalStorage {0}>".format(self.__data)
