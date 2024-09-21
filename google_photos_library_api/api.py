"""API for Google Photos bound to Home Assistant OAuth.

Callers subclass this to provide an asyncio implementation that handles
refreshing authentication tokens. You then pass in the auth object to the
GooglePhotosLibraryApi object to make authenticated calls to the Google Photos
Library API.

Example usage:
```python
from aiohttp import ClientSession
from google_photos_library_api import api
from google_photos_library_api import auth

class GooglePhotosAuth(auth.AbstractAuth):
    '''Provide OAuth for Google Photos.'''

    async def async_get_access_token(self) -> str:
        # Your auth implementation details are here

# Create a client library
auth = GooglePhotosAuth()
api = api.GooglePhotosLibraryApi(auth)

# Upload content
with open("image.jpg", "rb") as fd:
    upload_result = await api.upload_content(fd.read(), "image/jpeg")

# Create a media item
await api.create_media_items([
    NewMediaItem(SimpleMediaItem(upload_token=upload_result.upload_token))
])

# List all media items created by this application
result = await api.list_media_items()
for item in result.media_items:
    print(item.id)
```

"""

import logging
from typing import Any


from aiohttp.client_exceptions import ClientError

from .exceptions import GooglePhotosApiError
from .auth import AbstractAuth
from .model import (
    MediaItem,
    ListMediaItemResult,
    CreateMediaItemsResult,
    UploadResult,
    NewMediaItem,
    UserInfoResult,
    _ListMediaItemResultModel,
    _ListAlbumResultModel,
    ListAlbumResult,
    Album,
    NewAlbum,
)

__all__ = [
    "GooglePhotosLibraryApi",
]


_LOGGER = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 20

# Only included necessary fields to limit response sizes
GET_MEDIA_ITEM_FIELDS = (
    "id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"
)
LIST_MEDIA_ITEM_FIELDS = f"nextPageToken,mediaItems({GET_MEDIA_ITEM_FIELDS})"
LIST_ALBUMS_FIELDS = (
    "nextPageToken,albums(id,title,coverPhotoBaseUrl,coverPhotoMediaItemId)"
)
USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"


class GooglePhotosLibraryApi:
    """The Google Photos library api client."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize GooglePhotosLibraryApi."""
        self._auth = auth

    async def get_media_item(
        self, media_item_id: str, fields: str | None = None
    ) -> MediaItem:
        """Get all MediaItem resources."""
        return await self._auth.get_json(
            f"v1/mediaItems/{media_item_id}",
            params={"fields": (fields or GET_MEDIA_ITEM_FIELDS)},
            data_cls=MediaItem,
        )

    async def list_media_items(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        album_id: str | None = None,
        fields: str | None = None,
    ) -> ListMediaItemResult:
        """Get all MediaItem resources."""

        async def get_next_page(
            next_page_token: str | None,
        ) -> _ListMediaItemResultModel:
            return await self._list_media_items_page(
                page_size=page_size,
                page_token=next_page_token,
                album_id=album_id,
                fields=fields,
            )

        page_result = await get_next_page(None)
        result = ListMediaItemResult(page_result, get_next_page)
        return result

    async def _list_media_items_page(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        album_id: str | None = None,
        fields: str | None = None,
    ) -> _ListMediaItemResultModel:
        """Get all MediaItem resources."""
        args: dict[str, Any] = {
            "pageSize": (page_size or DEFAULT_PAGE_SIZE),
        }
        if page_token is not None:
            args["pageToken"] = page_token
        if album_id is not None:
            args["albumId"] = album_id
        args["filters"] = {"excludeNonAppCreatedData": True}
        return await self._auth.post_json(
            "v1/mediaItems:search",
            params={"fields": (fields or LIST_MEDIA_ITEM_FIELDS)},
            json=args,
            data_cls=_ListMediaItemResultModel,
        )

    async def list_albums(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        fields: str | None = None,
    ) -> ListAlbumResult:
        """Get all Album resources."""

        async def get_next_page(
            next_page_token: str | None,
        ) -> _ListAlbumResultModel:
            return await self._list_albums_page(
                page_size=page_size,
                page_token=next_page_token,
                fields=fields,
            )

        page_result = await get_next_page(None)
        result = ListAlbumResult(page_result, get_next_page)
        return result

    async def _list_albums_page(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        fields: str | None = None,
    ) -> _ListAlbumResultModel:
        """Get all Albums resources."""
        params: dict[str, Any] = {
            "pageSize": (page_size or DEFAULT_PAGE_SIZE),
            "fields": (fields or LIST_ALBUMS_FIELDS),
            "excludeNonAppCreatedData": "true",
        }
        if page_token is not None:
            params["pageToken"] = page_token
        return await self._auth.get_json(
            "v1/albums",
            params=params,
            data_cls=_ListAlbumResultModel,
        )

    async def create_album(
        self,
        album: NewAlbum,
    ) -> Album:
        """Create an album and return the result Album."""
        request: dict[str, Any] = {
            "album": album.to_dict(),
        }
        return await self._auth.post_json(
            "v1/albums",
            json=request,
            data_cls=Album,
        )

    async def update_album(
        self,
        album: NewAlbum,
    ) -> Album:
        """Update an album and return the updated album."""
        request: dict[str, Any] = {
            "album": album.to_dict(),
        }
        return await self._auth.post_json(
            "v1/albums",
            json=request,
            data_cls=Album,
        )

    async def upload_content(self, content: bytes, mime_type: str) -> UploadResult:
        """Upload media content to the API and return an upload token."""
        try:
            result = await self._auth.post(
                "v1/uploads", headers=_upload_headers(mime_type), data=content
            )
            result.raise_for_status()
            return UploadResult(upload_token=await result.text())
        except ClientError as err:
            raise GooglePhotosApiError(f"Failed to upload content: {err}") from err

    async def create_media_items(
        self,
        new_media_items: list[NewMediaItem],
        album_id: str | None = None,
    ) -> CreateMediaItemsResult:
        """Create a batch of media items and return the ids."""
        request: dict[str, Any] = {
            "newMediaItems": [
                new_media_item.to_dict() for new_media_item in new_media_items
            ],
        }
        if album_id is not None:
            request["albumId"] = album_id
        return await self._auth.post_json(
            "v1/mediaItems:batchCreate",
            json=request,
            data_cls=CreateMediaItemsResult,
        )

    async def get_user_info(self) -> UserInfoResult:
        """Get the user profile info.

        This call requires the userinfo.email scope.
        """
        return await self._auth.get_json(USERINFO_API, data_cls=UserInfoResult)


def _upload_headers(mime_type: str) -> dict[str, Any]:
    """Create the upload headers."""
    return {
        "Content-Type": "application/octet-stream",
        "X-Goog-Upload-Content-Type": mime_type,
        "X-Goog-Upload-Protocol": "raw",
    }
