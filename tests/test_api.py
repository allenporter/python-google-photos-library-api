"""Tests for Google Photos library API."""

from typing import Any
from unittest.mock import patch
from collections.abc import AsyncGenerator

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
    UserInfoResult,
    NewAlbum,
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


@pytest.fixture(name="get_user_info")
async def mock_get_user_info() -> list[dict[str, Any]]:
    """Fixture for returning fake user info responses."""
    return []


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


@pytest.fixture(name="albums")
async def mock_albums() -> list[dict[str, Any]]:
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


@pytest.fixture(name="create_album")
async def mock_create_album() -> list[dict[str, Any]]:
    """Fixture for fake create album responses."""
    return []


@pytest.fixture(name="requests")
async def mock_requests() -> list[aiohttp.web.Request]:
    """Fixture for fake create media items responses."""
    return []


@pytest.fixture(name="api")
async def mock_api(
    auth_cb: AuthCallback,
    requests: list[aiohttp.web.Request],
    get_user_info: list[dict[str, Any]],
    get_media_items: list[dict[str, Any]],
    list_media_items: list[dict[str, Any]],
    search_media_items: list[dict[str, Any]],
    albums: list[dict[str, Any]],
    upload_media_items: list[str],
    create_media_items: list[dict[str, Any]],
    create_album: list[dict[str, Any]],
) -> AsyncGenerator[GooglePhotosLibraryApi, None]:
    """Fixture for fake API object."""

    async def get_user_info_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(get_user_info.pop(0))

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

    async def albums_handler(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(albums.pop(0))

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

    async def async_create_album(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        requests.append(request)
        return aiohttp.web.json_response(create_album.pop(0))

    with patch("google_photos_library_api.api.USERINFO_API", "v1/userInfo"):
        auth = await auth_cb(
            [
                ("/v1/userInfo", get_user_info_handler),
                ("/v1/mediaItems", list_media_items_handler),
                ("/v1/mediaItems/{media_item_id}", get_media_items_handler),
                ("/v1/mediaItems:search", search_media_items_handler),
                ("/v1/albums", albums_handler),
                ("/v1/uploads", upload_media_items_handler),
                ("/v1/mediaItems:batchCreate", create_media_items_handler),
            ]
        )
        yield GooglePhotosLibraryApi(auth)


async def test_get_user_info(
    api: GooglePhotosLibraryApi,
    get_user_info: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
) -> None:
    """Test get user info API."""

    get_user_info.append(
        {
            "id": "user-id-1",
            "name": "User Name",
            "given_name": "User Given Name",
            "family_name": "User Full Name",
            "picture": "http://example.com/profile.jpg",
        }
    )
    result = await api.get_user_info()
    assert result == UserInfoResult(
        id="user-id-1",
        name="User Name",
    )


@pytest.mark.parametrize(
    ("list_media_items_requests", "expected_result", "expected_page_token"),
    [
        (
            [FAKE_LIST_MEDIA_ITEMS],
            [MediaItem(id="media-item-id-1", description="Photo 1")],
            None,
        ),
        ([{}], [], None),
        ([{"nextPageToken": "example-token-1"}], [], "example-token-1"),
    ],
)
async def test_list_media_items(
    api: GooglePhotosLibraryApi,
    list_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
    list_media_items_requests: list[dict[str, Any]],
    expected_result: list[MediaItem],
    expected_page_token: str | None,
) -> None:
    """Test list media_items API."""

    list_media_items.extend(list_media_items_requests)
    result = await api.list_media_items()
    assert result.media_items == expected_result
    assert result.next_page_token == expected_page_token
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].path == "/path-prefix/v1/mediaItems"
    assert (
        requests[0].query_string
        == "pageSize=20&fields=nextPageToken,mediaItems(id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video))"
    )


async def test_list_items_in_album(
    api: GooglePhotosLibraryApi,
    search_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
) -> None:
    """Test list media_items API limited to a specific album."""

    search_media_items.append(FAKE_LIST_MEDIA_ITEMS)
    result = await api.list_media_items(album_id="album-id-1")
    assert result.media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1")
    ]
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].path == "/path-prefix/v1/mediaItems:search"
    assert (
        requests[0].query_string
        == "fields=nextPageToken,mediaItems(id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video))"
    )


@pytest.mark.parametrize(
    ("fields", "expected_fields"),
    [
        (
            None,
            "nextPageToken,mediaItems(id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video))",
        ),
        (
            "nextPageToken,mediaItems(id,description)",
            "nextPageToken,mediaItems(id,description)",
        ),
    ],
    ids=("default_fields", "custom_fields"),
)
async def test_list_media_items_paging(
    api: GooglePhotosLibraryApi,
    list_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
    fields: str | None,
    expected_fields: str,
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
    result = await api.list_media_items(fields=fields)
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
    assert requests[0].query_string == f"pageSize=20&fields={expected_fields}"
    assert requests[1].method == "GET"
    assert requests[1].path == "/path-prefix/v1/mediaItems"
    assert (
        requests[1].query_string
        == f"pageSize=20&pageToken=next-page-token-1&fields={expected_fields}"
    )


@pytest.mark.parametrize(
    "list_args",
    [
        {"album_id": "album-id-1"},
    ],
)
@pytest.mark.parametrize(
    ("fields", "expected_fields"),
    [
        (
            None,
            "nextPageToken,mediaItems(id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video))",
        ),
        (
            "nextPageToken,mediaItems(id,description)",
            "nextPageToken,mediaItems(id,description)",
        ),
    ],
    ids=("default_fields", "custom_fields"),
)
async def test_search_items_paging(
    api: GooglePhotosLibraryApi,
    search_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
    list_args: dict[str, Any],
    fields: str | None,
    expected_fields: str | None,
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
    result = await api.list_media_items(**list_args, fields=fields)
    media_items = []
    async for result_page in result:
        media_items.extend(result_page.media_items)
    assert media_items == [
        MediaItem(id="media-item-id-1", description="Photo 1"),
        MediaItem(id="media-item-id-2", description="Photo 2"),
    ]
    assert len(requests) == 2
    assert requests[0].method == "POST"
    assert requests[0].path == "/path-prefix/v1/mediaItems:search"
    assert requests[0].query_string == f"fields={expected_fields}"
    assert requests[1].method == "POST"
    assert requests[1].path == "/path-prefix/v1/mediaItems:search"
    assert requests[1].query_string == f"fields={expected_fields}"


@pytest.mark.parametrize(
    ("fields", "expected_fields"),
    [
        (None, "id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"),
        ("id,description", "id,description"),
    ],
    ids=("default_fields", "custom_fields"),
)
async def test_get_media_item(
    api: GooglePhotosLibraryApi,
    get_media_items: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
    fields: str | None,
    expected_fields: str | None,
) -> None:
    """Test get media_items API."""

    get_media_items.append(FAKE_MEDIA_ITEM)
    result = await api.get_media_item("media-item-id-1", fields=fields)
    assert result == MediaItem(id="media-item-id-1", description="Photo 1")

    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].path == "/path-prefix/v1/mediaItems/media-item-id-1"
    assert requests[0].query_string == f"fields={expected_fields}"


@pytest.mark.parametrize(
    ("fields", "expected_fields"),
    [
        (
            None,
            "nextPageToken,albums(id,title,coverPhotoBaseUrl,coverPhotoMediaItemId)",
        ),
        ("nextPageToken,albums(id,title)", "nextPageToken,albums(id,title)"),
    ],
    ids=("default_fields", "custom_fields"),
)
async def test_list_albums(
    api: GooglePhotosLibraryApi,
    albums: list[dict[str, Any]],
    requests: list[aiohttp.web.Request],
    fields: str | None,
    expected_fields: str,
) -> None:
    """Test list albums API."""

    albums.append(
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
    albums.append(
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
    result = await api.list_albums(fields=fields)
    result_albums: list[Album] = []
    async for result_page in result:
        result_albums.extend(result_page.albums)
    assert result_albums == [
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
    assert requests[0].query_string == f"pageSize=20&fields={expected_fields}"
    assert requests[1].method == "GET"
    assert requests[1].path == "/path-prefix/v1/albums"
    assert (
        requests[1].query_string
        == f"pageSize=20&fields={expected_fields}&pageToken=next-page-token-1"
    )


async def test_upload_items(
    api: GooglePhotosLibraryApi, upload_media_items: list[str]
) -> None:
    """Test list upload_items API."""

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
        {"message": "Success"},
    ],
)
async def test_create_media_items(
    api: GooglePhotosLibraryApi,
    create_media_items: list[dict[str, Any]],
    status: dict[str, Any],
) -> None:
    """Test create media items API."""

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


async def test_create_album(
    api: GooglePhotosLibraryApi,
    albums: list[dict[str, Any]],
) -> None:
    """Test create albums API."""

    albums.append(
        {
            "id": "new-album-id-1",
            "title": "New Album",
        }
    )
    result = await api.create_album(NewAlbum(title="New Album"))
    assert result == Album(id="new-album-id-1", title="New Album")
