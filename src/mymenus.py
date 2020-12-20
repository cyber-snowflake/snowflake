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
