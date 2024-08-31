A python client library for Google Photos Library API. This is a thin wrapper
around the API used for a very lightweight abstraction.

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
