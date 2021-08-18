import discord
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def outer(self, ctx):
        ...

    @outer.group()
    async def inner(self, ctx):
        ...


def setup(bot):
    bot.add_cog(Info(bot))
