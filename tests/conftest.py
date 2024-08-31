"""Libraries used in tests."""

from typing import Awaitable, Callable

from aiohttp.web import Application
from aiohttp import ClientSession
import aiohttp
import pytest

from google_photos_library_api.auth import AbstractAuth

PATH_PREFIX = "/path-prefix"

AuthCallback = Callable[
    [
        list[
            tuple[str, Callable[[aiohttp.web.Request], Awaitable[aiohttp.web.Response]]]
        ]
    ],
    Awaitable[AbstractAuth],
]


class FakeAuth(AbstractAuth):
    """Implementation of AbstractAuth for use in tests."""

    async def async_get_access_token(self) -> str:
        """Return an OAuth credential for the calendar API."""
        return "some-token"


@pytest.fixture(name="auth_cb")
def mock_auth_fixture(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]]
) -> AuthCallback:

    async def create_auth(
        handlers: list[
            tuple[str, Callable[[aiohttp.web.Request], Awaitable[aiohttp.web.Response]]]
        ]
    ) -> AbstractAuth:
        """Create a test authentication library with the specified handler."""
        app = Application()
        for path, handler in handlers:
            app.router.add_get(f"{PATH_PREFIX}{path}", handler)
            app.router.add_post(f"{PATH_PREFIX}{path}", handler)

        client = await aiohttp_client(app)
        return FakeAuth(client, PATH_PREFIX)

    return create_auth
