"""Tests for Google Photos library API."""

from typing import Any

import pytest
import aiohttp

from google_photos_library_api.api import GooglePhotosLibraryApi
from google_photos_library_api.model import (
    ListMediaItemResult,
    CreateMediaItemsResult,
    NewMediaItemResult,
    UploadResult,
    NewMediaItem,
    SimpleMediaItem,
)
from google_photos_library_api.model import MediaItem


from .conftest import AuthCallback


FAKE_MEDIA_ITEM = {
    "id": "media-item-id-1",
    "description": "Photo 1",
}
FAKE_LIST_MEDIA_ITEMS = {
    "mediaItems": [FAKE_MEDIA_ITEM],
}


@pytest.fixture(name="get_media_items")
async def mock_get_media_item() -> list[dict[str, Any]]:
    """Fixture for fake list media items responses."""
    return []


@pytest.fixture(name="list_media_items")
async def mock_list_media_items() -> list[dict[str, Any]]:
    """Fixture for fake list media items responses."""
    return []


@pytest.fixture(name="search_media_items")
async def mock_search_media_items() -> list[dict[str, Any]]:
    """Fixture for fake search media items responses."""
    return []


@pytest.fixture(name="upload_media_items")
async def mock_upload_media_items() -> list[str]:
    """Fixture for fake list upload endpoint responses."""
    return []


@pytest.fixture(name="create_media_items")
async def mock_create_media_items() -> list[dict[str, Any]]:
    """Fixture for fake create media items responses."""
    return []


@pytest.fixture(name="api")
async def mock_api(
    auth_cb: AuthCallback,
    get_media_items: list[dict[str, Any]],
    list_media_items: list[dict[str, Any]],
    search_media_items: list[dict[str, Any]],
    upload_media_items: list[str],
    create_media_items: list[dict[str, Any]],
) -> GooglePhotosLibraryApi:
    """Fixture for fake API object."""

    async def get_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.json_response(get_media_items.pop(0))

    async def list_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.json_response(list_media_items.pop(0))

    async def search_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.json_response(search_media_items.pop(0))

    async def upload_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.Response(body=upload_media_items.pop(0))

    async def create_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        return aiohttp.web.json_response(create_media_items.pop(0))

    auth = await auth_cb(
        [
            ("/v1/mediaItems", list_media_items_handler),
            ("/v1/mediaItems/{media_item_id}", get_media_items_handler),
            ("/v1/mediaItems:search", search_media_items_handler),
            ("/v1/uploads", upload_media_items_handler),
            ("/v1/mediaItems:batchCreate", create_media_items_handler),
        ]
    )
    return GooglePhotosLibraryApi(auth)


async def test_list_media_items(
    api: GooglePhotosLibraryApi, list_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    list_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items()
    assert result == ListMediaItemResult(
        media_items=[MediaItem(id="media-item-id-1", description="Photo 1")]
    )


async def test_list_items_in_album(
    api: GooglePhotosLibraryApi, search_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    search_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items(album_id="album-id-1")
    assert result == ListMediaItemResult(
        media_items=[MediaItem(id="media-item-id-1", description="Photo 1")]
    )


async def test_list_favorites(
    api: GooglePhotosLibraryApi, search_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    search_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items(favorites=True)
    assert result == ListMediaItemResult(
        media_items=[MediaItem(id="media-item-id-1", description="Photo 1")]
    )


async def test_get_media_item(
    api: GooglePhotosLibraryApi, get_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    get_media_items.append(FAKE_MEDIA_ITEM)
    result = await api.get_media_item("media-item-id-1")
    assert result == MediaItem(id="media-item-id-1", description="Photo 1")


async def test_upload_items(
    api: GooglePhotosLibraryApi, upload_media_items: list[str]
) -> None:
    """Test list media_items API."""

    upload_media_items.append("fake-upload-token-1")
    result = await api.upload_content(b"content", "image/jpeg")
    assert result == UploadResult(upload_token="fake-upload-token-1")


async def test_create_media_items(
    api: GooglePhotosLibraryApi, create_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    create_media_items.append(
        {
            "newMediaItemResults": [
                {
                    "uploadToken": "new-upload-token-1",
                    "mediaItem": FAKE_MEDIA_ITEM,
                }
            ]
        }
    )
    result = await api.create_media_items(
        [
            NewMediaItem(SimpleMediaItem(upload_token="new-upload-token-1"))
        ]
    )
    assert result == CreateMediaItemsResult(
        new_media_item_results=[
            NewMediaItemResult(
                upload_token="new-upload-token-1",
                media_item=MediaItem(id="media-item-id-1", description="Photo 1"),
            )
        ]
    )
