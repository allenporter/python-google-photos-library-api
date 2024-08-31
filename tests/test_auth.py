"""Tests for the request client library."""

from typing import Awaitable, Callable

from aiohttp.web import Application
from aiohttp import ClientSession
import aiohttp
import pytest

from google_photos_library_api.auth import AbstractAuth
from google_photos_library_api.exceptions import (
    ApiException,
    ApiForbiddenException,
)


class FakeAuth(AbstractAuth):
    """Implementation of AbstractAuth for use in tests."""

    async def async_get_access_token(self) -> str:
        """Return an OAuth credential for the calendar API."""
        return "some-token"


async def test_get_response(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test post that returns json."""

    async def handler(request: aiohttp.web.Request) -> aiohttp.web.Response:
        body = await request.json()
        assert body == {"client_id": "some-client-id"}
        return aiohttp.web.json_response(
            {
                "some-key": "some-value",
            }
        )

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")
    data = await auth.get("some-path", json={"client_id": "some-client-id"})
    assert await data.json() == {"some-key": "some-value"}


async def test_get_json_response_unexpected(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test json response with wrong response type."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.json_response(["value1", "value2"])

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")
    with pytest.raises(ApiException):
        await auth.get_json("some-path")


async def test_get_json_response(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test post that returns json."""

    async def handler(request: aiohttp.web.Request) -> aiohttp.web.Response:
        body = await request.json()
        assert body == {"client_id": "some-client-id"}
        return aiohttp.web.json_response(
            {
                "some-key": "some-value",
            }
        )

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")
    data = await auth.get_json("some-path", json={"client_id": "some-client-id"})
    assert data == {"some-key": "some-value"}


async def test_post_json_response(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test post that returns json."""

    async def handler(request: aiohttp.web.Request) -> aiohttp.web.Response:
        body = await request.json()
        assert body == {"client_id": "some-client-id"}
        return aiohttp.web.json_response(
            {
                "some-key": "some-value",
            }
        )

    app = Application()
    app.router.add_post("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")
    data = await auth.post_json("some-path", json={"client_id": "some-client-id"})
    assert data == {"some-key": "some-value"}


async def test_post_json_response_unexpected(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test post that returns wrong json type."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.json_response(["value1", "value2"])

    app = Application()
    app.router.add_post("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")

    with pytest.raises(ApiException):
        await auth.post_json("some-path")


async def test_post_json_response_unexpected_text(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test post that returns unexpected format."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.Response(text="body")

    app = Application()
    app.router.add_post("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")
    with pytest.raises(ApiException):
        await auth.post_json("some-path")


async def test_get_json_response_bad_request(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test error handling with detailed json response."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.json_response(
            {
                "error": {
                    "errors": [
                        {
                            "domain": "calendar",
                            "reason": "timeRangeEmpty",
                            "message": "The specified time range is empty.",
                            "locationType": "parameter",
                            "location": "timeMax",
                        }
                    ],
                    "code": 400,
                    "message": "The specified time range is empty.",
                }
            },
            status=400,
        )

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)
    app.router.add_post("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")

    with pytest.raises(
        ApiException,
        match=r"Error from API: 400: The specified time range is empty.: Bad Request",
    ):
        await auth.get("some-path")

    with pytest.raises(
        ApiException,
        match=r"Error from API: 400: The specified time range is empty.: Bad Request",
    ):
        await auth.get_json("some-path")

    with pytest.raises(
        ApiException,
        match=r"Error from API: 400: The specified time range is empty.: Bad Request",
    ):
        await auth.post("some-path")

    with pytest.raises(
        ApiException,
        match=r"Error from API: 400: The specified time range is empty.: Bad Request",
    ):
        await auth.post_json("some-path")


async def test_unavailable_error(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test of basic request/response handling."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.Response(status=500)

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")

    with pytest.raises(ApiException):
        await auth.get_json("some-path")


async def test_forbidden_error(
    aiohttp_client: Callable[[Application], Awaitable[ClientSession]],
) -> None:
    """Test request/response handling for 403 status."""

    async def handler(_: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.Response(status=403)

    app = Application()
    app.router.add_get("/path-prefix/some-path", handler)

    client = await aiohttp_client(app)
    auth = FakeAuth(client, "/path-prefix")

    with pytest.raises(ApiForbiddenException):
        await auth.get_json("some-path")
