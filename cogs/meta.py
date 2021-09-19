import time
from collections import Counter

import discord
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages

from utils import FormatList, Context, Embed


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "socket_stats"):
            self.bot.socket_stats = Counter()

    @commands.Cog.listener("on_socket_event_type")
    async def count_event_dispatches(self, event: str):
        """Handles counting the event dispatches

        Args:
            event (str): The event name dispatched
        """
        self.bot.socket_stats[event] += 1

    @commands.command(aliases=["ss", "socketstats"])
    async def socket_stats(self, ctx: Context):
        await ViewMenuPages(
            FormatList(
                [
                    f"{e}: {v}"
                    for e, v in sorted(
                        self.bot.socket_stats.items(), key=lambda x: x[1], reverse=True
                    )
                ],
                per_page=10,
            )
        ).start(ctx)

    @commands.command()
    async def ping(self, ctx: Context):
        embed = discord.Embed(title="Pong!")

        embed.add_field(
            name="WS Latency", value=f"``{round((ctx.bot.latency * 1000)):,}ms``"
        )

        start = time.perf_counter()
        msg = await ctx.send(embed=embed)
        end = time.perf_counter()
        elapsed = round((end - start) * 1000)

        embed.add_field(name="API Latency", value=f"``{elapsed:,}ms``", inline=False)
        await msg.edit(embed=embed)

    @commands.command(aliases=["src"])
    async def source(self, ctx: Context):
        """Sends the source of the bot"""
        await ctx.send("<https://github.com/imvaskel/personal-bot>")


def setup(bot):
    bot.add_cog(Meta(bot))
