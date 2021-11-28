from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from discord.webhook.async_ import Webhook

if TYPE_CHECKING:
    from typing import Type, Optional

import aiohttp
import discord
import pytomlpp
import jishaku
from discord.ext import commands

from .webhook_logger import WebhookLogger

jishaku.Flags.FORCE_PAGINATOR = True
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.NO_DM_TRACEBACK = True


class Bot(commands.Bot):
    session: aiohttp.ClientSession
    context: Type[commands.Context]

    def __init__(self, session: aiohttp.ClientSession):
        self.logger = logging.getLogger(__name__)
        self.session = session
        self.config = pytomlpp.load("./config.toml")

        self.hook = Webhook.from_url(
            self.config["bot"]["keys"]["webhook"],
            session=session,
            bot_token=self.config["bot"]["keys"]["token"],
        )

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        root.addHandler(handler)
        handler = WebhookLogger(webhook=self.hook)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        root.addHandler(handler)

        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            **self.config["bot"]["config"],
            intents=intents,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        for extension in self.config["bot"]["extensions"]:
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
