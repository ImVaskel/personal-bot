from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import aiohttp

if TYPE_CHECKING:
    from typing import Optional, Dict, Literal

__all__ = (
    "XIVCharacterCardsClient",
    "CardApiError",
    "ApiError",
    "Response",
    "CharacterNotFound",
)


class CardApiError(Exception):
    """The base exception class"""

    reason: str

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class ApiError(CardApiError):
    pass


class CharacterNotFound(CardApiError):
    """The character given was not found."""

    pass


class Response(TypedDict):
    status: str
    url: str


class XIVCharacterCardsClient:
    BASE_URL: str = "https://ffxiv-character-cards.herokuapp.com"

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        """Creates a new client.

        Args:
            session (Optional[aiohttp.ClientSession], optional): The aiohttp clientsession to use. This will create one
                if none is given. Defaults to None.
        """
        self._session = session or aiohttp.ClientSession()

    async def prepare_id(self, id: int) -> Response:
        """Makes a request to the /prepare/id endpoint to get the character card.

        Args:
            id (int): The lodestone id.

        Raises:
            ApiError: A generic error occured with the api.

        Returns:
            Response: The response of the request.
        """
        url = f"{self.BASE_URL}/prepare/{id}"

        async with self._session.get(url) as res:
            json = await res.json()

        if res.status == 400:
            raise CharacterNotFound(await res.text())

        if res.status == 500 or json.get("status") == "error":
            raise ApiError(json["reason"])

        return Response(status=json["status"], url=self.BASE_URL + json["url"])

    async def prepare_name(self, world: str, name: str) -> Response:
        url = f"{self.BASE_URL}/prepare/name/{world}/{name}"

        async with self._session.get(url) as res:
            # this can return json *or* text for some reason. only on /name/world endpoints though.
            if res.status == 404:
                raise CharacterNotFound(await res.text())
            json = await res.json()

        if json.get("status") == "error":
            raise ApiError(json["reason"])

        return Response(status=json["status"], url=self.BASE_URL + json["url"])

    async def get_id(self, id: int) -> str:
        """Return a link to the character card (if cached).

        Args:
            id (int): The lodestone id to use

        Returns:
            str: The url
        """
        return f"{self.BASE_URL}/characters/id/{id}.png"

    async def get_name(self, world: str, name: str) -> str:
        """Return a link to the character card (if cached).

        Args:
            world (str): The world
            name (str): The character's name

        Returns:
            str: The url
        """
        return f"{self.BASE_URL}/characters/name/{world}/{name}"
