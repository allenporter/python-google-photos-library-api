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

# List all media items
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
USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"


class GooglePhotosLibraryApi:
    """The Google Photos library api client."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize GooglePhotosLibraryApi."""
        self._auth = auth

    async def get_media_item(self, media_item_id: str) -> MediaItem:
        """Get all MediaItem resources."""
        return await self._auth.get_json(
            f"v1/mediaItems/{media_item_id}",
            params={"fields": GET_MEDIA_ITEM_FIELDS},
            data_cls=MediaItem,
        )

    async def list_media_items(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        album_id: str | None = None,
        favorites: bool = False,
    ) -> ListMediaItemResult:
        """Get all MediaItem resources."""

        async def get_next_page(
            next_page_token: str | None,
        ) -> _ListMediaItemResultModel:
            return await self._list_media_items_page(
                page_size=page_size,
                page_token=next_page_token,
                album_id=album_id,
                favorites=favorites,
            )

        page_result = await get_next_page(None)
        result = ListMediaItemResult(page_result, get_next_page)
        return result

    async def _list_media_items_page(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        album_id: str | None = None,
        favorites: bool = False,
    ) -> _ListMediaItemResultModel:
        """Get all MediaItem resources."""
        args: dict[str, Any] = {
            "pageSize": (page_size or DEFAULT_PAGE_SIZE),
            "pageToken": page_token,
        }
        if album_id is not None or favorites:
            if album_id is not None:
                args["albumId"] = album_id
            if favorites:
                args["filters"] = {"featureFilter": {"includedFeatures": "FAVORITES"}}
            return await self._auth.post_json(
                "v1/mediaItems:search",
                params={"fields": GET_MEDIA_ITEM_FIELDS},
                json=args,
                data_cls=_ListMediaItemResultModel,
            )
        return await self._auth.get_json(
            "v1/mediaItems",
            params={"fields": GET_MEDIA_ITEM_FIELDS},
            json=args,
            data_cls=_ListMediaItemResultModel,
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
