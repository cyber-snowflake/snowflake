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

import sys
from typing import MutableMapping, Optional, Dict, Union

from utils.types import GuildSettings


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
