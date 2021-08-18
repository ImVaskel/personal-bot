from __future__ import annotations

from typing import TYPE_CHECKING

from discord.embeds import EmptyEmbed

if TYPE_CHECKING:
    import datetime

    from typing import Optional, Union, Any

    from discord.colour import Colour
    from discord.embeds import _EmptyEmbed, MaybeEmpty, EmbedType
    from discord.utils import MISSING

import discord


class Embed(discord.Embed):
    def __init__(
        self,
        *,
        colour: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        color: Union[int, Colour, _EmptyEmbed] = None,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = "rich",
        url: MaybeEmpty[Any] = EmptyEmbed,
        description: MaybeEmpty[Any] = EmptyEmbed,
        timestamp: datetime.datetime = None,
    ):
        super().__init__(
            colour=colour,
            color=color or discord.Colour.fuchsia(),
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp or discord.utils.utcnow(),
        )

    def add_field(self, *, name: Any, value: Any, inline: bool = False) -> Embed:
        return super().add_field(name=name, value=value, inline=inline)


class Codeblock:
    __slots__ = ("text", "lang")

    def __init__(self, text: str, *, lang: Optional[str] = None):
        self.text = text
        self.lang = lang or ""

    def __str__(self) -> str:
        return f"```{self.lang}\n{self.text}```"
