A python client library for Google Photos Library API.

The Google Photos Library API allows your app to upload photos and videos to
Google Photos. See [Google Photos APIs](https://developers.google.com/photos)
for more details on how to integrate Google Photos with your application.

This library does not currently support the [picker API](https://developers.google.com/photos/picker/guides/get-started-picker).

See [Updates to the Google Photos APIs](https://developers.google.com/photos/support/updates) for
additional detail on the latest changes to the API.

## Background

This is a thin wrapper around the API used for a very lightweight abstraction. The
primary use case is for Home Assistant though can be used for other usages. This
is redundant with Google Photos APIs however they are very generic. This library
provides a simpler API that is easier to read, supports `asyncio`, and also
includes content uploading APIs which don't have a standard client library.

## Usage

See the [API Documentation](https://allenporter.github.io/python-google-photos-library-api/) for more details.

## Development

Set up pre-requisites:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements_dev.txt
```

Run tests and view coverage:
```bash
$ py.test --cov-report=term-missing --cov=google_photos_library_api
```
