from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

import discord
from discord.ext import commands
from utils import Context, Embed

if TYPE_CHECKING:
    from utils import Bot


class Info(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def whois(
        self,
        ctx: Context,
        *,
        user: Optional[Union[discord.Member, discord.User]] = None,
    ):
        user = user or ctx.author

        description = (
            f"ID: {user.id} \n"
            f"Bot: {'Yes' if user.bot else 'No'} \n"
            f"Created at: {discord.utils.format_dt(user.created_at)}"
        )

        embed = Embed(
            title=f"Info about {user}!",
            description=description,
            color=getattr(user, "color", None),
        ).set_thumbnail(url=user.avatar)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
