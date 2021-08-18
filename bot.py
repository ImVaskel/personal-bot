import asyncio

import aiohttp
import uvloop
from utils import Bot


async def startup():
    """
    Constructs the bot and then runs ``start``, so that a clientsession can be shared.
    """
    async with aiohttp.ClientSession() as cs:
        bot = Bot()

        bot.session = cs
        await bot.start(bot.config["token"])


if __name__ == "__main__":
    uvloop.install()

    asyncio.run(startup())
