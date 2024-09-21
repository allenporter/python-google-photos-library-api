"""Constants for Google Photos Library API."""

LIBRARY_API_URL = "https://photoslibrary.googleapis.com"
USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"


class LibraryApiScope:
    """Google Photos OAuth scopes.

    Note that other scopes that access the entire library are deprecated.
    """

    APPEND_ONLY = "https://www.googleapis.com/auth/photoslibrary.appendonly"
    READONLY_APP_CREATED_DATA = (
        "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"
    )
    EDIT_APP_CREATED_DATA = (
        "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata"
    )
