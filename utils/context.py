from __future__ import annotations

from typing import TYPE_CHECKING
from utils import Embed

if TYPE_CHECKING:
    from typing import Union

    from .bot import Bot

import discord
from discord.ext import commands


class Context(commands.Context):
    if TYPE_CHECKING:
        bot: Bot
        author: Union[discord.Member, discord.User]
        message: discord.Message

    @property
    def embed(self):
        return Embed().set_footer(
            text=f"Requested by: {self.author}", icon_url=self.author.avatar.url
        )


def setup(bot: Bot):
    bot.context = Context


def teardown(bot: Bot):
    bot.context = commands.Context
