from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, menus
from .constants import Embed

if TYPE_CHECKING:
    from typing import Optional, List

    from discord.ext.menus.views import ViewMenuPages


class FormatList(menus.ListPageSource):
    """Formats a list like
    ```
    1. A
    2. B
    3. C
    ```
    Or
    ```
    A
    B
    C
    ```
    depending on whether ``enumerate`` is true.
    """

    def __init__(
        self, entries, *, per_page: Optional[int] = 5, enumerate: bool = False
    ):
        super().__init__(entries, per_page=per_page)
        self.enumerate = enumerate

    async def format_page(self, menu: ViewMenuPages, entries: List[str]):
        embed = Embed(description="")

        if self.get_max_pages() > 1:
            embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")

        if self.enumerate:

            for index, entry in enumerate(
                entries, start=self.per_page * menu.current_page + 1
            ):
                embed.description += f"{index}: {entry}\n"

        else:
            embed.description = "\n".join(entries)

        return embed
