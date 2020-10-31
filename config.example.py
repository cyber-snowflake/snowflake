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

from dataclasses import dataclass


# noinspection DuplicatedCode
@dataclass(frozen=True)
class Postgres:
    user = "postgres"
    password = "postgres"
    database = "bot"
    host = "localhost"
    port = 5432
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"


# noinspection DuplicatedCode
@dataclass(frozen=True)
class Bot:
    default_prefix = "!"
    token = "Nzas2Ksakjjksdllkdgsjlsdkgkdlfgljkdfjkglk23r"
    shard_count = 1
    shard_ids = [0]
    support_guild_id = 123123123123
