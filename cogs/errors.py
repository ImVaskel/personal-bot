from __future__ import annotations

import logging

import discord
from discord.ext import commands
from utils import Embed, CharacterNotFound


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.ignored = (commands.CommandNotFound,)
        self.handle = (CharacterNotFound,)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, exception: commands.CommandError
    ):
        if isinstance(exception, self.ignored):
            return

        exception = getattr(exception, "original", exception)

        embed = Embed(
            title="An error occured!", description=f"```diff\n- {exception}```"
        )
        await ctx.send(embed=embed)

        if not isinstance(exception, commands.CommandError) and not isinstance(
            exception, self.handle
        ):
            self.logger.error(
                f"an error occurred in `{ctx.command}`",
                exc_info=(type(exception), exception, exception.__traceback__),
            )


def setup(bot):
    bot.add_cog(Errors(bot))
