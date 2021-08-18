from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Optional

import aiohttp
import discord
import toml
from discord.ext import commands


class Bot(commands.Bot):
    session: aiohttp.ClientSession
    context: Type[commands.Context]

    def __init__(self, session: aiohttp.ClientSession):
        self.logger = logging.getLogger(__name__)
        self.session = session

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        root.addHandler(handler)

        self.config = toml.load("./config.toml")

        intents = discord.Intents.default()
        intents.members = True  # type: ignore

        super().__init__(
            commands.when_mentioned_or(self.config["prefix"]),
            owner_ids=self.config["owner_ids"],
            intents=intents,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        for extension in self.config["extensions"]:
            try:
                self.load_extension(extension)
            except commands.ExtensionError:
                self.logger.exception("failed to load extension `%s`", extension)
            else:
                self.logger.info("loaded extension `%s`", extension)

    async def get_context(
        self, message, *, cls: Optional[Type[commands.Context]] = None
    ):
        return await super().get_context(message, cls=cls or self.context)
