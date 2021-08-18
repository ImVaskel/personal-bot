from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional

    from utils import Bot

import discord
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages
from utils import Embed


class FormatCharacterResponse(menus.ListPageSource):
    def __init__(
        self,
        entries,
    ):
        super().__init__(entries, per_page=1)

    async def format_page(self, menu: ViewMenuPages, entry: Dict[str, Any]):
        embed = Embed(title=f"{entry['Name']}")

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


class FormatList(menus.ListPageSource):
    """Formats a list like
    ```
    1. A
    2. B
    3. C
    ```
    Or
    ```
    A
    B
    C
    ```
    depending on whether ``number`` is passed.
    """

    def __init__(self, entries, *, per_page: Optional[int] = 5, number: bool = False):
        super().__init__(entries, per_page=per_page)
        self.number = number

    async def format_page(self, menu: ViewMenuPages, entries: List[str]):
        embed = Embed(description="")

        if self.get_max_pages() > 1:
            embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")

        if self.number:

            for index, entry in enumerate(
                entries, start=self.per_page * menu.current_page + 1
            ):
                embed.description += f"{index}: {entry}\n"

        else:
            embed.description = "\n".join(entries)

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

    BASE_URL = "https://xivapi.com"

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
        self.bot.loop.create_task(self.get_server_data())

    async def get_server_data(self):
        """Gets a list of valid FFXIV servers for use in the server converter."""
        self.servers = await self.request_api("https://xivapi.com/servers")
        self.servers.extend(self.datacenters)

    async def handle_api_error(self, ctx: commands.Context, res: Dict[str, Any]):
        raise ApiError(res.get("Subject"), res.get("Message"))

    async def request_api(self, url: str):
        """Makes a request to the api so that the api key can be added.

        Args:
            url (str): The url to request
        """
        if "?" in url:
            url += f"&private_key={self.bot.config['ffxiv_key']}"
        else:
            url += f"?private_key={self.bot.config['ffxiv_key']}"

        async with self.bot.session.get(url) as res:
            r = await res.json()
            if isinstance(r, dict):
                if r.get("Error"):
                    raise ApiError(r["Subject"], r["Message"])
            return r

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
        url = f"{self.BASE_URL}/character/search?name={first}+{last}&server={server}"

        res = await self.request_api(url)

        if res.get("Error") is True:
            await self.handle_api_error(ctx, res)
            return

        if not res.get("Results"):
            raise commands.BadArgument("Character not found! Please try again.")

        await ViewMenuPages(FormatCharacterResponse(res["Results"])).start(ctx)

    @ffxiv.command(aliases=["ls"])
    async def list_servers(self, ctx: commands.Context):
        """Lists the valid servers in an interactive pagination session."""
        await ViewMenuPages(FormatList(self.servers, per_page=10, number=True)).start(
            ctx
        )


def setup(bot):
    bot.add_cog(Ffxiv(bot))
