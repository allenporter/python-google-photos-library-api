"""Google Photos Library API Data Model."""

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Self

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import DataClassJSONMixin

__all__ = [
    "ListMediaItemResult",
    "MediaItem",
    "MediaMetadata",
    "Photo",
    "Video",
    "ContributorInfo",
    "UploadResult",
    "NewMediaItem",
    "SimpleMediaItem",
    "CreateMediaItemsResult",
    "NewMediaItemResult",
    "Status",
    "UserInfoResult",
]


@dataclass
class Photo(DataClassDictMixin):
    """Metadata for a photo media item."""

    camera_make: str | None = field(
        metadata=field_options(alias="cameraMake"), default=None
    )
    """Make of the camera that took the photo."""

    camera_model: str | None = field(
        metadata=field_options(alias="cameraModel"), default=None
    )
    """Model of the camera that took the photo."""

    focal_length: float | None = field(
        metadata=field_options(alias="focalLength"), default=None
    )
    """Focal length of the camera lens used to take the photo."""

    aperture_f_number: float | None = field(
        metadata=field_options(alias="apertureFNumber"), default=None
    )
    """Aperture f number of the camera lens used to take the photo."""

    iso_equivalent: int | None = field(
        metadata=field_options(alias="isoEquivalent"), default=None
    )
    """ISO value that the camera used to take the photo."""

    exposure_time: str | None = field(
        metadata=field_options(alias="exposureTime"), default=None
    )
    """Exposure time (duraton like '3.5s') of the camera lens aperture when the photo was taken."""


@dataclass
class Video(DataClassDictMixin):
    """Metadata for a video media item."""

    camera_make: str | None = field(
        metadata=field_options(alias="cameraMake"), default=None
    )
    """Make of the camera that took the video."""

    camera_model: str | None = field(
        metadata=field_options(alias="cameraModel"), default=None
    )
    """Model of the camera that took the video."""

    fps: str | None = None
    """Frames per second of the video."""

    status: str | None = None
    """Status of the video."""


@dataclass
class MediaMetadata(DataClassDictMixin):
    """Metadata for a media item."""

    creation_time: str | None = field(
        metadata=field_options(alias="creationTime"), default=None
    )
    """Creation time of the media item."""

    width: int | None = None
    """Width of the media item in pixels."""

    height: int | None = None
    """Height of the media item in pixels."""

    photo: Photo | None = None
    """Metadata for a photo media item."""

    video: Video | None = None
    """Metadata for a video media item."""


@dataclass
class ContributorInfo(DataClassDictMixin):
    """Information about the user who contributed this media item."""

    profile_picture_base_url: str = field(
        metadata=field_options(alias="profilePictureBaseUrl")
    )
    """Base URL for the user's profile picture."""

    display_name: str = field(metadata=field_options(alias="displayName"))
    """Display name of the user."""


@dataclass
class MediaItem(DataClassJSONMixin):
    """Representation of a media item (such as a photo or video) in Google Photos."""

    id: str
    """Identifier for the media item, used between sessions to identify this media item."""

    description: str | None = None
    """Description of the media item, shown to the user in the item's info section in the Google Photos app."""

    product_url: str | None = field(
        metadata=field_options(alias="product_url"), default=None
    )
    """Google Photos URL for the media item."""

    base_url: str | None = field(metadata=field_options(alias="baseUrl"), default=None)
    """A URL to the media item's bytes."""

    mime_type: str | None = field(
        metadata=field_options(alias="mimeType"), default=None
    )
    """MIME type of the media item."""

    media_metadata: MediaMetadata | None = field(
        metadata=field_options(alias="mediaMetadata"), default=None
    )
    """Metadata related to the media item, such as, height, width, or creation time."""

    contributor_info: ContributorInfo | None = field(
        metadata=field_options(alias="contributorInfo"), default=None
    )
    """Information about the user who created the media item."""

    filename: str | None = None
    """Filename of the media item."""


@dataclass
class Album(DataClassDictMixin):
    """Representation of an album in Google Photos."""

    id: str
    """Identifier for the album, used between sessions to identify this album."""

    title: str
    """Title of the album."""

    product_url: str | None = field(metadata=field_options(alias="productUrl"), default=None)
    """Google Photos URL for the album."""

    media_items_count: int | None = field(
        metadata=field_options(alias="mediaItemsCount"), default=None
    )
    """Number of media items in the album."""

    cover_photo_base_url: str | None = field(
        metadata=field_options(alias="coverPhotoBaseUrl"), default=None
    )
    """Base URL for the cover photo of the album."""

    cover_photo_media_item_id: str | None = field(
        metadata=field_options(alias="coverPhotoMediaItemId"),
        default=None,
    )
    """Identifier for the cover photo of the album."""

    is_writeable: bool | None = field(
        metadata=field_options(alias="isWriteable"), default=None
    )
    """Whether the album is writable."""


@dataclass
class UserInfoResult(DataClassJSONMixin):
    """Response from getting user info."""

    id: str
    """User ID."""

    email: str
    """User email."""

    name: str
    """User name."""


@dataclass
class _ListMediaItemResultModel(DataClassJSONMixin):
    """Api response containing a list of events."""

    media_items: list[MediaItem] = field(metadata=field_options(alias="mediaItems"))
    """List of media items."""

    next_page_token: str | None = field(
        metadata=field_options(alias="nextPageToken"), default=None
    )
    """Token for the next page of results."""


class ListMediaItemResult:
    """Response from listing media items."""

    def __init__(
        self,
        response: _ListMediaItemResultModel,
        get_next_page: (
            Callable[[str | None], Awaitable[_ListMediaItemResultModel]] | None
        ) = None,
    ):
        self._response = response
        self._get_next_page = get_next_page

    @property
    def media_items(self) -> list[MediaItem]:
        """List of media items."""
        return self._response.media_items

    @property
    def next_page_token(self) -> str | None:
        """Token for the next page of results."""
        return self._response.next_page_token

    async def __aiter__(self) -> AsyncIterator[Self]:
        """Async iterator to traverse through pages of responses."""
        response = self
        while response is not None:
            yield response
            if not response.next_page_token or not self._get_next_page:
                break
            page_result = await self._get_next_page(response.next_page_token)
            response = self.__class__(page_result)


@dataclass
class _ListAlbumResultModel(DataClassJSONMixin):
    """Api response containing a list of albums requested."""

    albums: list[Album] = field(default_factory=list)
    """List of albums shown in the Albums tab of the user's Google Photos app."""

    next_page_token: str | None = field(
        metadata=field_options(alias="nextPageToken"), default=None
    )
    """Token to use to get the next set of albums."""


class ListAlbumResult:
    """Api response containing a list of albums requested."""

    def __init__(
        self,
        response: _ListAlbumResultModel,
        get_next_page: (
            Callable[[str | None], Awaitable[_ListAlbumResultModel]] | None
        ) = None,
    ):
        self._response = response
        self._get_next_page = get_next_page

    @property
    def albums(self) -> list[Album]:
        """List of albums shown in the Albums tab of the user's Google Photos app."""
        return self._response.albums

    @property
    def next_page_token(self) -> str | None:
        """Token to use to get the next set of albums."""
        return self._response.next_page_token

    async def __aiter__(self) -> AsyncIterator[Self]:
        """Async iterator to traverse through pages of responses."""
        response = self
        while response is not None:
            yield response
            if not response.next_page_token or not self._get_next_page:
                break
            page_result = await self._get_next_page(response.next_page_token)
            response = self.__class__(page_result)


@dataclass
class Status(DataClassJSONMixin):
    """Status of the media item."""

    code: int
    """The status code, which should be an enum value of google.rpc.Code"""

    message: str | None = None
    """A developer-facing error message, which should be in English"""

    details: list[dict[str, Any]] = field(default_factory=list)
    """A list of messages that carry the error details"""


@dataclass
class SimpleMediaItem:
    """Simple media item."""

    upload_token: str = field(metadata=field_options(alias="uploadToken"))
    """Upload token for the media item."""

    file_name: str | None = field(
        metadata=field_options(alias="fileName"), default=None
    )
    """Filename of the media item."""


@dataclass
class NewMediaItem(DataClassDictMixin):
    """New media item to create."""

    simple_media_item: SimpleMediaItem = field(
        metadata=field_options(alias="simpleMediaItem")
    )
    """Simple media item to create."""

    description: str | None = None
    """Description of the media item."""


@dataclass
class NewMediaItemResult(DataClassJSONMixin):
    """Result of creating a new media item."""

    upload_token: str = field(metadata=field_options(alias="uploadToken"))
    """Upload token for the media item."""

    status: Status | None = None
    """If an error occurred during the creation of this media item, this field is populated with information related to the error."""

    media_item: MediaItem | None = field(
        metadata=field_options(alias="mediaItem"), default=None
    )
    """Media item created with the upload token."""


@dataclass
class UploadResult:
    """Response from uploading media items."""

    upload_token: str
    """Upload token for the media item."""


@dataclass
class CreateMediaItemsResult(DataClassJSONMixin):
    """Response from creating media items."""

    new_media_item_results: list[NewMediaItemResult] = field(
        metadata=field_options(alias="newMediaItemResults")
    )
    """List of created media items."""


@dataclass
class Error:
    """Error details from the API response."""

    status: str | None = None
    code: int | None = None
    message: str | None = None
    details: list[dict[str, Any]] | None = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the error details."""
        error_message = ""
        if self.status:
            error_message += self.status
        if self.code:
            if error_message:
                error_message += f" ({self.code})"
            else:
                error_message += str(self.code)
        if self.message:
            if error_message:
                error_message += ": "
            error_message += self.message
        if self.details:
            error_message += f"\nError details: ({self.details})"
        return error_message


@dataclass
class ErrorResponse(DataClassJSONMixin):
    """A response message that contains an error message."""

    error: Error | None = None
