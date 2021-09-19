from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from discord.ext.commands.errors import CommandError

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional, Union

    from utils import Bot

import discord
import pyxivapi
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages
from utils import Embed, FormatList, Context, Timer


class CardApiResponse(TypedDict):
    status: str
    url: str


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

    async def convert(self, ctx: Context, arg: str) -> str:

        servers: List[str] = ctx.command.cog.servers  # type: ignore

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
    card_base_url = "https://ffxiv-character-cards.herokuapp.com"

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

    async def prepare_card(
        self, user: Union[str, int], world: Optional[str] = None
    ) -> CardApiResponse:
        """Prepares a user's card

        Args:
            user (Union[str, int]): The user to use, can be a loadstone id or a player name.
            world (Optional[str], optional): The world to use, this is only required if :param:`user` is :class:`str`. This is silently ignored
                if :param:`user` is :class:`int`  Defaults to None.

        Raises:
            ValueError: Raised if :param:`user` is passed as :class:`str` and :param:`world` isn't passed.
            CommandError: A generic error occured with the api.

        Returns:
            dict[str, Any]: The api response.
        """
        if isinstance(user, str) and world is None:
            raise ValueError(
                "User was passed as type `str`, but `world` was not passed."
            )

        if isinstance(user, int):
            url = f"{self.card_base_url}/prepare/id/{user}"
        else:
            url = f"{self.card_base_url}/prepare/name/{world}/{user}"

        async with self.bot.session.get(url) as res:
            if res.content_type == "text/html":
                raise CommandError(f"{await res.text()}")

            json = await res.json()
            if (
                json.get("status") == "error"
            ):  # idk, can return json or html, weird api.
                raise CommandError(f"{json['reason']}")

            return CardApiResponse(**json)

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

    @ffxiv.group()
    async def whois(self, ctx: commands.Context):
        """The base group for character cards.

        Powered by https://github.com/ArcaneDisgea/XIV-Character-Cards"""
        pass

    @whois.command(name="name")
    async def whois_name(self, ctx: commands.Context, world: str, *, name: str):
        """Gets a character card via a name & world."""
        with Timer() as timer:
            res = await self.prepare_card(name, world)

        url = self.card_base_url + res["url"]
        await ctx.send(
            f"Finished in {timer.elapsed} seconds.", embed=Embed().set_image(url=url)
        )

    @whois.command(name="id")
    async def wgois_id(self, ctx: commands.Context, id: int):
        """Gets a character card via a loadstone id."""
        with Timer() as timer:
            res = await self.prepare_card(id)

        url = self.card_base_url + res["url"]
        await ctx.send(
            f"Finished in {timer.elapsed} seconds.", embed=Embed().set_image(url=url)
        )


def setup(bot):
    bot.add_cog(Ffxiv(bot))
