"""API for Google Photos bound to Home Assistant OAuth."""

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

    async def get_user_info(self) -> UserInfoResult:
        """Get the user profile info."""
        return await self._auth.get_json(USERINFO_API, data_cls=UserInfoResult)

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
                data_cls=ListMediaItemResult,
            )
        return await self._auth.get_json(
            "v1/mediaItems",
            params={"fields": GET_MEDIA_ITEM_FIELDS},
            json=args,
            data_cls=ListMediaItemResult,
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


def _upload_headers(mime_type: str) -> dict[str, Any]:
    """Create the upload headers."""
    return {
        "Content-Type": "application/octet-stream",
        "X-Goog-Upload-Content-Type": mime_type,
        "X-Goog-Upload-Protocol": "raw",
    }
