"""API for Google Photos bound to Home Assistant OAuth."""

import logging
from typing import Any


from aiohttp.client_exceptions import ClientError

from .exceptions import GooglePhotosApiError
from .auth import AbstractAuth

_LOGGER = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 20

# Only included necessary fields to limit response sizes
GET_MEDIA_ITEM_FIELDS = (
    "id,baseUrl,mimeType,filename,mediaMetadata(width,height,photo,video)"
)
LIST_MEDIA_ITEM_FIELDS = f"nextPageToken,mediaItems({GET_MEDIA_ITEM_FIELDS})"
UPLOAD_API = "https://photoslibrary.googleapis.com/v1/uploads"
USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"


class GooglePhotosLibraryApi:
    """The Google Photos library api client."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize GooglePhotosLibraryApi."""
        self._auth = auth

    async def get_user_info(self) -> dict[str, Any]:
        """Get the user profile info."""
        return await self._auth.get_json(USERINFO_API)

    async def get_media_item(self, media_item_id: str) -> dict[str, Any]:
        """Get all MediaItem resources."""
        return await self._auth.get_json(
            f"v1/mediaItems/{media_item_id}", params={"fields": GET_MEDIA_ITEM_FIELDS}
        )

    async def list_media_items(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        album_id: str | None = None,
        favorites: bool = False,
    ) -> dict[str, Any]:
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
                "v1/mediaItems/search",
                params={"fields": GET_MEDIA_ITEM_FIELDS},
                body=args,
            )
        return await self._auth.get_json(
            "v1/mediaItems",
            params={"fields": GET_MEDIA_ITEM_FIELDS},
            json=args,
        )

    async def upload_content(self, content: bytes, mime_type: str) -> str:
        """Upload media content to the API and return an upload token."""
        try:
            result = await self._auth.post(
                UPLOAD_API, headers=_upload_headers(mime_type), body=content
            )
            result.raise_for_status()
            return await result.text()
        except ClientError as err:
            raise GooglePhotosApiError(f"Failed to upload content: {err}") from err

    async def create_media_items(self, upload_tokens: list[str]) -> list[str]:
        """Create a batch of media items and return the ids."""
        result = await self._auth.post_json(
            "v1/mediaItems:batchCreate",
            body={
                "newMediaItems": [
                    {
                        "simpleMediaItem": {
                            "uploadToken": upload_token,
                        }
                        for upload_token in upload_tokens
                    }
                ]
            },
        )
        return [
            media_item["mediaItem"]["id"]
            for media_item in result["newMediaItemResults"]
        ]


def _upload_headers(mime_type: str) -> dict[str, Any]:
    """Create the upload headers."""
    return {
        "Content-Type": "application/octet-stream",
        "X-Goog-Upload-Content-Type": mime_type,
        "X-Goog-Upload-Protocol": "raw",
    }
