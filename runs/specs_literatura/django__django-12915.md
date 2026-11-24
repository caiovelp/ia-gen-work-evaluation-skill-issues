## Summary

Using `ASGIStaticFilesHandler` (`django/contrib/staticfiles/handlers.py`) to serve a request raises `TypeError: 'NoneType' object is not callable`. The reporter believes the cause is that `StaticFilesHandlerMixin` has no async response function (`get_response_async`).

## Steps to reproduce

1. Use `ASGIStaticFilesHandler` as the ASGI application. The traceback shows it running under Daphne.
2. Send a request to the application.
3. The exception below is raised.

The report does not give the exact configuration, settings or request used.

## Observed behavior

The request fails with `Exception inside application: 'NoneType' object is not callable`. `ASGIStaticFilesHandler.__call__` delegates to `ASGIHandler.__call__`. That calls `get_response_async()` in `django/core/handlers/base.py`, which awaits `self._middleware_chain(request)`. At that point `_middleware_chain` is `None`.

## Expected behavior

`ASGIStaticFilesHandler` should handle the request and return a response without raising an exception.

## Stack trace / error output

```
Exception inside application: 'NoneType' object is not callable
Traceback (most recent call last):
 File ".../lib/python3.7/site-packages/daphne/cli.py", line 30, in asgi
	await self.app(scope, receive, send)
 File ".../src/django/django/contrib/staticfiles/handlers.py", line 86, in __call__
	return await super().__call__(scope, receive, send)
 File ".../src/django/django/core/handlers/asgi.py", line 161, in __call__
	response = await self.get_response_async(request)
 File ".../src/django/django/core/handlers/base.py", line 148, in get_response_async
	response = await self._middleware_chain(request)
TypeError: 'NoneType' object is not callable
```

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

- Python 3.7 (from the `lib/python3.7/site-packages` path in the traceback)
- Daphne as the ASGI server (from the traceback)
- Django installed from a source checkout (`.../src/django/`); exact version/commit not provided in the original report.
- OS: Not provided in the original report.