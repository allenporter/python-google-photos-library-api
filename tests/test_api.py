"""Tests for Google Photos library API."""

from typing import Any

import pytest
import aiohttp

from google_photos_library_api.api import GooglePhotosLibraryApi
from google_photos_library_api.model import (
    CreateMediaItemsResult,
    NewMediaItemResult,
    UploadResult,
    NewMediaItem,
    SimpleMediaItem,
    Status,
)
from google_photos_library_api.model import MediaItem, Album


from .conftest import AuthCallback


FAKE_MEDIA_ITEM = {
    "id": "media-item-id-1",
    "description": "Photo 1",
}
FAKE_MEDIA_ITEM2 = {
    "id": "media-item-id-2",
    "description": "Photo 2",
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


@pytest.fixture(name="list_albums")
async def mock_list_albums() -> list[dict[str, Any]]:
    """Fixture for fake list albums responses."""
    return []


@pytest.fixture(name="upload_media_items")
async def mock_upload_media_items() -> list[str]:
    """Fixture for fake list upload endpoint responses."""
    return []


@pytest.fixture(name="create_media_items")
async def mock_create_media_items() -> list[dict[str, Any]]:
    """Fixture for fake create media items responses."""
    return []


@pytest.fixture(name="requests")
async def mock_requests() -> list[aiohttp.web.Request]:
    """Fixture for fake create media items responses."""
    return []

@pytest.fixture(name="api")
async def mock_api(
    auth_cb: AuthCallback,
    requests: list[aiohttp.web.Request],
    get_media_items: list[dict[str, Any]],
    list_media_items: list[dict[str, Any]],
    search_media_items: list[dict[str, Any]],
    list_albums: list[dict[str, Any]],
    upload_media_items: list[str],
    create_media_items: list[dict[str, Any]],
) -> GooglePhotosLibraryApi:
    """Fixture for fake API object."""

    async def get_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(get_media_items.pop(0))

    async def list_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(list_media_items.pop(0))

    async def search_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(search_media_items.pop(0))

    async def list_albums_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(list_albums.pop(0))

    async def upload_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.Response(body=upload_media_items.pop(0))

    async def create_media_items_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(create_media_items.pop(0))

    auth = await auth_cb(
        [
            ("/v1/mediaItems", list_media_items_handler),
            ("/v1/mediaItems/{media_item_id}", get_media_items_handler),
            ("/v1/mediaItems:search", search_media_items_handler),
            ("/v1/albums", list_albums_handler),
            ("/v1/uploads", upload_media_items_handler),
            ("/v1/mediaItems:batchCreate", create_media_items_handler),
        ]
    )
    return GooglePhotosLibraryApi(auth)


async def test_list_media_items(
    api: GooglePhotosLibraryApi, list_media_items: list[dict[str, Any]], requests: list[aiohttp.web.Request],

) -> None:
    """Test list media_items API."""

    list_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items()
    assert result.media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1")
    ]
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].path == "/path-prefix/v1/mediaItems"
    assert requests[0].query_string == "pageSize=20&fields=id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"


async def test_list_items_in_album(
    api: GooglePhotosLibraryApi, search_media_items: list[dict[str, Any]], requests: list[aiohttp.web.Request],
) -> None:
    """Test list media_items API."""

    search_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items(album_id="album-id-1")
    assert result.media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1")
    ]
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].path == "/path-prefix/v1/mediaItems:search"
    assert requests[0].query_string == "fields=id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"


async def test_list_favorites(
    api: GooglePhotosLibraryApi, search_media_items: list[dict[str, Any]], requests: list[aiohttp.web.Request],
) -> None:
    """Test list media_items API."""

    search_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items(favorites=True)
    assert result.media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1")
    ]
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].path == "/path-prefix/v1/mediaItems:search"
    assert requests[0].query_string == "fields=id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"


async def test_list_media_items_paging(
    api: GooglePhotosLibraryApi,
    list_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
) -> None:
    """Test list media_items API."""

    list_media_items.append(
        {
            "mediaItems": [FAKE_MEDIA_ITEM],
            "nextPageToken": "next-page-token-1",
        }
    )
    list_media_items.append(
        {
            "mediaItems": [FAKE_MEDIA_ITEM2],
        }
    )
    result = await api.list_media_items()
    media_items = []
    async for result_page in result:
        media_items.extend(result_page.media_items)
    assert media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1"),
        MediaItem(id="media-item-id-2", description="Photo 2"),
    ]
    assert len(requests) == 2
    assert requests[0].method == "GET"
    assert requests[0].path == "/path-prefix/v1/mediaItems"
    assert requests[0].query_string == "pageSize=20&fields=id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"
    assert requests[1].method == "GET"
    assert requests[1].path == "/path-prefix/v1/mediaItems"
    assert requests[1].query_string == "pageSize=20&pageToken=next-page-token-1&fields=id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"


@pytest.mark.parametrize(
    "list_args",
    [
        {"favorites": True},
        {"album_id": "album-id-1"},
    ],
)
async def test_search_items_paging(
    api: GooglePhotosLibraryApi,
    search_media_items: list[dict[str, Any]],
    list_args: dict[str, Any],
) -> None:
    """Test list media_items API."""

    search_media_items.append(
        {
            "mediaItems": [FAKE_MEDIA_ITEM],
            "nextPageToken": "next-page-token-1",
        }
    )
    search_media_items.append(
        {
            "mediaItems": [FAKE_MEDIA_ITEM2],
        }
    )
    result = await api.list_media_items(**list_args)
    media_items = []
    async for result_page in result:
        media_items.extend(result_page.media_items)
    assert media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1"),
        MediaItem(id="media-item-id-2", description="Photo 2"),
    ]


async def test_get_media_item(
    api: GooglePhotosLibraryApi, get_media_items: list[dict[str, Any]]
) -> None:
    """Test list media_items API."""

    get_media_items.append(FAKE_MEDIA_ITEM)
    result = await api.get_media_item("media-item-id-1")
    assert result == MediaItem(id="media-item-id-1", description="Photo 1")


async def test_list_albums(
    api: GooglePhotosLibraryApi,
    list_albums: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
) -> None:
    """Test list media_items API."""

    list_albums.append(
        {
            "albums": [
                {
                    "id": "album-id-1",
                    "title": "Album 1",
                    "productUrl": "http://photos.google.com/album/album-id-1",
                }
            ],
            "nextPageToken": "next-page-token-1",
        }
    )
    list_albums.append(
        {
            "albums": [
                {
                    "id": "album-id-2",
                    "title": "Album 2",
                    "productUrl": "http://photos.google.com/album/album-id-2",
                }
            ],
        }
    )
    result = await api.list_albums()
    albums = []
    async for result_page in result:
        albums.extend(result_page.albums)
    assert albums == [
        Album(
            id="album-id-1",
            title="Album 1",
            product_url="http://photos.google.com/album/album-id-1",
        ),
        Album(
            id="album-id-2",
            title="Album 2",
            product_url="http://photos.google.com/album/album-id-2",
        ),
    ]

    assert len(requests) == 2
    assert requests[0].method == "GET"
    assert requests[0].path == "/path-prefix/v1/albums"
    assert requests[0].query_string == "pageSize=20&fields=nextPageToken,albums(id,title,coverPhotoBaseUrl,coverPhotoMediaItemId)"
    assert requests[1].method == "GET"
    assert requests[1].path == "/path-prefix/v1/albums"
    assert requests[1].query_string == "pageSize=20&fields=nextPageToken,albums(id,title,coverPhotoBaseUrl,coverPhotoMediaItemId)&pageToken=next-page-token-1"


async def test_upload_items(
    api: GooglePhotosLibraryApi, upload_media_items: list[str]
) -> None:
    """Test list media_items API."""

    upload_media_items.append("fake-upload-token-1")
    result = await api.upload_content(b"content", "image/jpeg")
    assert result == UploadResult(upload_token="fake-upload-token-1")


@pytest.mark.parametrize(
    "status",
    [
        {
            "code": 200,
            "message": "Success",
        },
        {
            "code": 200,
        },
    ],
)
async def test_create_media_items(
    api: GooglePhotosLibraryApi,
    create_media_items: list[dict[str, Any]],
    status: dict[str, Any],
) -> None:
    """Test list media_items API."""

    create_media_items.append(
        {
            "newMediaItemResults": [
                {
                    "uploadToken": "new-upload-token-1",
                    "status": status,
                    "mediaItem": FAKE_MEDIA_ITEM,
                }
            ]
        }
    )
    result = await api.create_media_items(
        [NewMediaItem(SimpleMediaItem(upload_token="new-upload-token-1"))]
    )
    assert result == CreateMediaItemsResult(
        new_media_item_results=[
            NewMediaItemResult(
                upload_token="new-upload-token-1",
                status=Status(**status),
                media_item=MediaItem(id="media-item-id-1", description="Photo 1"),
            )
        ]
    )
