import traceback

import discord
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages

from utils import Codeblock


class PaginateSplitString(menus.ListPageSource):
    def __init__(self, entry):
        super().__init__(entry, per_page=1)

    async def format_page(self, menu, entry: str):
        return entry


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await ctx.bot.is_owner(ctx.author)

    @commands.group()
    async def dev(self, ctx):
        pass

    @commands.is_owner()
    @dev.command(name="load")
    async def load_extension(self, ctx: commands.Context, *, extension):
        try:
            ctx.bot.load_extension(extension)
        except commands.ExtensionError as err:
            traceback_text = str(
                Codeblock(
                    f"{''.join(traceback.format_exception(type(err), err, err.__traceback__, 4))}",
                    lang="py",
                )
            )
            await ViewMenuPages(
                PaginateSplitString(
                    [
                        traceback_text[v : v + 2000]
                        for v in range(0, len(traceback_text), 2000)
                    ]
                )
            ).start(ctx)
        else:
            await ctx.send(f"reloaded extension ``extension``.")


def setup(bot):
    bot.add_cog(Owner(bot))
