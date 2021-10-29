from __future__ import annotations
from io import BytesIO

import logging
import asyncio
from typing import TYPE_CHECKING

import discord
from .constants import Embed


if TYPE_CHECKING:
    from typing import Optional


class WebhookLogger(logging.Handler):
    COLORS = {
        logging.CRITICAL: discord.Color.dark_red(),
        logging.ERROR: discord.Color.red(),
        logging.WARN: discord.Color.orange(),
        logging.INFO: discord.Color.green(),
        logging.DEBUG: discord.Color.greyple(),
    }

    def __init__(
        self,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        webhook: discord.Webhook,
    ) -> None:
        super().__init__()
        self.hook = webhook
        self.loop = loop or asyncio.get_event_loop()
        self._queue = asyncio.Queue[logging.LogRecord]()
        self.loop.create_task(self.sender())

    def emit(self, record: logging.LogRecord) -> None:
        self._queue.put_nowait(record)

    async def sender(self) -> None:
        while True:
            embeds: list[discord.Embed] = []
            files: list[discord.File] = []

            for record in [
                r
                for r in await asyncio.gather(
                    *(
                        asyncio.wait_for(self._queue.get(), timeout=10)
                        for _ in range(10)
                    ),
                    return_exceptions=True,
                )
                if isinstance(r, logging.LogRecord)
            ]:

                formatted = self.format(record)

                if len(formatted) >= 4098:
                    file = discord.File(
                        BytesIO(formatted.encode()),
                        filename=f"{record.name}-{record.levelname}.txt",
                    )
                    files.append(file)
                else:
                    embed = Embed(
                        description=discord.utils.escape_markdown(formatted),
                        color=self.COLORS[record.levelno],
                    )
                    embeds.append(embed)

            if embeds or files:
                await self.hook.send(embeds=embeds, files=files)
