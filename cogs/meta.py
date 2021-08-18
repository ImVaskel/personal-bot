import time

import discord
from discord.ext import commands


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
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


def setup(bot):
    bot.add_cog(Meta(bot))
