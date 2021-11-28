from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional

    from utils import Bot

import discord
import pyxivapi
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages
from utils import Embed, FormatList, Context, Timer, XIVCharacterCardsClient


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

    value: str

    async def convert(self, ctx: Context, arg: str) -> str:
        ffxiv: Optional[Ffxiv] = ctx.bot.get_cog("Ffxiv")  # type: ignore

        if not ffxiv:
            raise commands.BadArgument(
                "The FFXIV cog is currently not loaded, please try again later."
            )

        servers = ffxiv.servers
        raw_datacenters = ffxiv.raw_datacenters
        datacenters = ffxiv.datacenters

        if arg in raw_datacenters:
            arg = f"_dc_{arg}"

        if arg in servers or arg in datacenters:
            self.value = arg
            return arg

        raise commands.BadArgument("The given server is not valid.")


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
        self.raw_datacenters = [
            "Elemental",
            "Gaia",
            "Mana",
            "Aether",
            "Primal",
            "Crystal",
            "Chaos",
            "Light",
        ]
        self.client = pyxivapi.XIVAPIClient(
            self.bot.config["bot"]["keys"]["ffxiv_key"], self.bot.session
        )
        self.card_client = XIVCharacterCardsClient(bot.session)
        self.bot.loop.create_task(self.get_server_data())

    async def get_server_data(self):
        """Gets a list of valid FFXIV servers for use in the server converter."""
        self.servers = await self.client.get_server_list()

    @commands.group()
    async def ffxiv(self, ctx):
        """The base group for the ffxiv commands."""
        pass

    @ffxiv.group()
    async def search(self, ctx: commands.Context):
        """Base group for all the user search commands.
        Powered by XIVApi"""
        pass

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @search.command()
    async def name(
        self,
        ctx: commands.Context,
        server: ServerConverter,
        first: str,
        last: str,
    ):
        """
        Search for a player in a given server. Any of the datacenter's servers are valid.
        This will only display up to 50 users.
        You can also use a datacenter.

        Use ``ffxiv ls`` to list all valid servers.

        This also has a server-wide cooldown so I don't get banned from the api :P

        NOTE:
            The datacenter / server is case sensitive.
        """
        res = await self.client.character_search(server, first, last)  # type: ignore

        await ViewMenuPages(FormatCharacterResponse(res["Results"])).start(ctx)

    @ffxiv.command(aliases=["ls"])
    async def list_servers(self, ctx: commands.Context):
        """Lists the valid servers in an interactive pagination session."""
        await ViewMenuPages(
            FormatList(self.servers + self.raw_datacenters, per_page=10, enumerate=True)
        ).start(ctx)

    @ffxiv.group()
    async def whois(self, ctx: commands.Context):
        """The base group for character cards.

        Powered by https://github.com/ArcaneDisgea/XIV-Character-Cards"""
        pass

    @whois.command(name="name")
    async def whois_name(self, ctx: commands.Context, world: str, *, name: str):
        """Gets a character card via a name & world."""
        async with ctx.typing():
            with Timer() as timer:
                res = await self.card_client.prepare_name(world, name)

        url = res["url"]
        await ctx.send(
            f"Finished in {timer.elapsed} seconds.", embed=Embed().set_image(url=url)
        )

    @whois.command(name="id")
    async def whois_id(self, ctx: commands.Context, id: int):
        """Gets a character card via a loadstone id."""
        async with ctx.typing():
            with Timer() as timer:
                res = await self.card_client.prepare_id(id)

        url = res["url"]
        await ctx.send(
            f"Finished in {timer.elapsed} seconds.", embed=Embed().set_image(url=url)
        )


def setup(bot):
    bot.add_cog(Ffxiv(bot))
