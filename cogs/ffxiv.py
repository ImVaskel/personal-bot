from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional

    from utils import Bot

import discord
import pyxivapi
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages
from utils import Embed, FormatList


class FormatCharacterResponse(menus.ListPageSource):
    def __init__(
        self,
        entries,
    ):
        super().__init__(entries, per_page=1)

    async def format_page(self, menu: ViewMenuPages, entry: Dict[str, Any]):
        embed = Embed(title=f"{entry['Name']}")

        if self.get_max_pages() > 1:
            embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")

        embed.set_thumbnail(url=entry["Avatar"])

        embed.add_field(
            name="Info",
            value=(
                f"**ID:** {entry['ID']}\n"
                f"**Language:** {entry['Lang']}\n"
                f"**Server:** {entry['Server']}\n"
                f"**Rank:** {entry['Rank']}\n"
                f"**Feast Matches:** {entry['FeastMatches']}\n"
            ),
        )

        return embed


class ServerConverter(commands.Converter):
    """A converter for getting a valid server.
    This just casts the arg to titlecase then checks if the arg is in the list.
    """

    async def convert(self, ctx: commands.Context, arg: str) -> str:

        servers: List[str] = ctx.command.cog.servers

        if not servers:
            raise commands.BadArgument(
                "The FFXIV cog is currently not loaded, please try again later."
            )

        try:
            index = servers.index(arg)
        except ValueError:
            raise commands.BadArgument("The given server is not valid.")
        else:
            return servers[index]


class ApiError(commands.CommandError):
    """Representation of an api error."""

    def __init__(self, subject: str, message: str):
        m = f"An API error occured: {subject}\n{message}"
        super().__init__(m)


class Ffxiv(commands.Cog):
    """The cog for all things FFXIV (Final Fantasy 14).
    This mostly allows you to get info about characters, items, etc.
    """

    servers: List[str]

    def __init__(self, bot: Bot):
        self.bot = bot
        self.datacenters = [
            "_dc_Elemental",
            "_dc_Gaia",
            "_dc_Mana",
            "_dc_Aether",
            "_dc_Primal",
            "_dc_Crystal",
            "_dc_Chaos",
            "_dc_Light",
        ]
        self.client = pyxivapi.XIVAPIClient(
            self.bot.config["ffxiv_key"], self.bot.session
        )
        self.bot.loop.create_task(self.get_server_data())

    async def get_server_data(self):
        """Gets a list of valid FFXIV servers for use in the server converter."""
        self.servers = await self.client.get_server_list()

        self.servers.extend(self.datacenters)

    @commands.group()
    async def ffxiv(self, ctx):
        """The base group for the ffxiv commands."""
        pass

    @ffxiv.group()
    async def search(self, ctx: commands.Context):
        pass

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @search.command()
    async def name(
        self,
        ctx: commands.Context,
        first: str,
        last: str,
        server: ServerConverter,
    ):
        """
        Search for a player in a given server. Any of the datacenter's servers are valid.
        This will only display up to 50 users.
        You can also use a datacenter, though this has the format ``_dc_<center>``.

        Use ``ffxiv ls`` to list all valid servers.

        This also has a server-wide cooldown so I don't get banned from the api :P

        NOTE:
            The datacenter / server is case sensitive.
        """
        res: Dict[str, Any] = await self.client.character_search(server, first, last)  # type: ignore (library is untyped)

        await ViewMenuPages(FormatCharacterResponse(res["Results"])).start(ctx)

    @ffxiv.command(aliases=["ls"])
    async def list_servers(self, ctx: commands.Context):
        """Lists the valid servers in an interactive pagination session."""
        await ViewMenuPages(
            FormatList(self.servers, per_page=10, enumerate=True)
        ).start(ctx)


def setup(bot):
    bot.add_cog(Ffxiv(bot))
