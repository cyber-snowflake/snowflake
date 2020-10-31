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

from discord import Embed
from discord.ext.menus import ListPageSource


class MyPagesSource(ListPageSource):
    def __init__(self, entries, *, per_page, **kwargs):
        super().__init__(entries, per_page=per_page)
        self.embed = Embed(color=0x000000)

        if (title := kwargs.get("title", None)) is not None:
            self.embed.title = title

        if (embed := kwargs.get("embed", None)) is not None:
            self.embed = embed

    def format_page(self, menu, page):
        if isinstance(page, str):
            return page
        else:
            self.embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
            self.embed.description = "\n".join(page)
            return self.embed


class GuildsPagesSource(ListPageSource):
    def format_page(self, menu, page):
        if isinstance(page, str):
            return page
        else:
            return "```\n{0}```{1}".format("\n".join(page), f"Page {menu.current_page + 1}/{self.get_max_pages()}")
