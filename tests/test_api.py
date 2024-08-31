"""Tests for Google Photos library API."""

from typing import Any

import pytest
import aiohttp

from google_photos_library_api.api import (
    GooglePhotosLibraryApi,
)


from .conftest import AuthCallback


@pytest.fixture(name="list_media_items")
async def mock_list_media_items() -> list[dict[str, Any]]:
    """Fixture for fake list media items responses."""
    return []


@pytest.fixture(name="api")
async def mock_api(
    auth_cb: AuthCallback, list_media_items: list[dict[str, Any]]
) -> GooglePhotosLibraryApi:
    """Fixture for fake API object."""

    async def list_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.json_response(list_media_items.pop(0))

    auth = await auth_cb([("/v1/mediaItems", list_media_items_handler)])
    return GooglePhotosLibraryApi(auth)


async def test_list_media_items(
    api: GooglePhotosLibraryApi, list_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    list_media_items.append(
        {
            "mediaItems": [
                {
                    "id": "calendar-id-1",
                    "description": "Calendar 1",
                }
            ]
        },
    )
    result = await api.list_media_items()
    assert result == {
        "mediaItems": [
            {
                "id": "calendar-id-1",
                "description": "Calendar 1",
            }
        ]
    }
