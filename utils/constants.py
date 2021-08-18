from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime

    from typing import Optional, Union

    from discord.utils import MISSING

import discord


class Embed(discord.Embed):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("color", discord.Color.fuchsia())
        kwargs.setdefault("timestamp", discord.utils.utcnow())

        super().__init__(*args, **kwargs)

    def add_field(self, *args, **kwargs) -> Embed:
        kwargs.setdefault("inline", False)
        return super().add_field(*args, **kwargs)
