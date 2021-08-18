from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from .bot import Bot

import discord
from discord.ext import commands


class Context(commands.Context):
    if TYPE_CHECKING:
        bot: Bot
        message: discord.Message


def setup(bot: Bot):
    bot.context = Context


def teardown(bot: Bot):
    bot.context = commands.Context
