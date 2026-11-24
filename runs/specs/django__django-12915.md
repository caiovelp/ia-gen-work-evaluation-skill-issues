# Spec: Async response support for `ASGIStaticFilesHandler`

## Objective

Make `ASGIStaticFilesHandler` serve static files when Django runs under an ASGI server.

**The problem.** The issue reports that `StaticFilesHandlerMixin` provides no async counterpart to its response method. When a request reaches `ASGIStaticFilesHandler` (seen with daphne), the inherited `get_response_async` from `django/core/handlers/base.py` calls `self._middleware_chain(request)`. On this handler `_middleware_chain` is `None`, so the request fails:

```
File ".../django/contrib/staticfiles/handlers.py", line 86, in __call__
    return await super().__call__(scope, receive, send)
File ".../django/core/handlers/asgi.py", line 161, in __call__
    response = await self.get_response_async(request)
File ".../django/core/handlers/base.py", line 148, in get_response_async
    response = await self._middleware_chain(request)
TypeError: 'NoneType' object is not callable
```

**Who is affected.** Developers serving static files through `ASGIStaticFilesHandler`, for example when running under an ASGI server in development.

**Acceptance criteria:**

- A request for an existing static file through `ASGIStaticFilesHandler` returns a successful response with the file's contents, and no `TypeError` is raised.
- A request for a missing static file under the static URL prefix behaves like the WSGI `StaticFilesHandler` in the same case (for example, a 404 response that includes debug information when `DEBUG` is on).
- Requests outside the static URL prefix still go to the wrapped ASGI application, as they do now.
- The synchronous WSGI `StaticFilesHandler` behaves exactly as before.

## Assumptions

1. The fix belongs in `StaticFilesHandlerMixin`, or in a closely related part of `django/contrib/staticfiles/handlers.py`, by adding an async response path (`get_response_async`) that mirrors the existing sync `get_response`.
2. The error occurs because the static files handler never loads the middleware chain, which leaves `_middleware_chain` set to `None`. The base class's `get_response_async` therefore cannot be used as it is.
3. Serving static files is synchronous work (file I/O through the existing serve logic). Calling it from async code through Django's usual sync-to-async bridge is acceptable.
4. Exceptions such as `Http404` during static serving should be converted into responses the same way the sync path does.
5. The Python version in the traceback (3.7) is only the reporter's environment. Supported versions follow whatever this Django branch supports.
6. Behavior only needs to change for the ASGI handler. No public API changes are needed beyond the new method.

## Tech Stack

- Python (the reporter uses 3.7; supported versions for this branch are unknown)
- Django: `django.contrib.staticfiles.handlers`, `django.core.handlers.asgi`, `django.core.handlers.base`
- ASGI server in the report: daphne (only used to reproduce the bug, not a dependency of the fix)
- Exact Django version or branch: **unknown**

## Commands

- Build: **unknown** (not stated in the issue)
- Test: **unknown** (Django's test runner invocation is not given in the issue)
- Lint: **unknown**
- Dev/reproduce: run an ASGI server (e.g., daphne) against an app wrapped in `ASGIStaticFilesHandler` and request a static file. The exact command is **unknown**.

## Project Structure

Only these paths appear in the issue:

```
django/contrib/staticfiles/handlers.py → StaticFilesHandlerMixin, StaticFilesHandler, ASGIStaticFilesHandler
django/core/handlers/asgi.py           → ASGIHandler.__call__ (calls get_response_async)
django/core/handlers/base.py           → BaseHandler.get_response_async (uses _middleware_chain)
```

Test locations for staticfiles handlers: **unknown**.

## Code Style

- Follow the existing conventions in `django/contrib/staticfiles/handlers.py`. Its contents are not visible here, so no snippet is given.
- The new async method should mirror the structure and naming of the existing sync `get_response` in the mixin (`get_response` → `get_response_async`).

## Testing Strategy

- Framework: Django's own test suite (the exact runner command and test module location are **unknown**).
- Required tests:
  - **Regression test.** Send an ASGI request for an existing static file through `ASGIStaticFilesHandler` and assert a successful response with the expected body. This test must fail before the fix with `TypeError: 'NoneType' object is not callable`.
  - **Not-found case.** Request a missing file under the static prefix and assert the response matches the sync handler's behavior.
  - **Pass-through case.** Request a path outside the static prefix and assert it reaches the wrapped application.
  - Existing tests for the sync `StaticFilesHandler` must keep passing without changes.

## Boundaries

- **Always:** keep the sync and async paths equivalent in behavior. Add a regression test that reproduces the traceback. Run the existing staticfiles and handlers tests.
- **Ask first:** changing `BaseHandler` or `ASGIHandler` in `django/core/handlers/` rather than the staticfiles mixin. Changing how middleware is loaded for static file handlers. Adding any dependency.
- **Never:** change the sync `StaticFilesHandler` behavior. Make static serving bypass existing path or security checks. Add an ASGI server such as daphne as a dependency.

## Success Criteria

- The traceback in the issue no longer occurs when a static file is requested through `ASGIStaticFilesHandler`.
- The new tests for the static file hit, the missing file, and pass-through all pass under the ASGI handler.
- The full existing test suite for staticfiles and core handlers passes with no regressions.

## Open Questions

1. Which Django branch or version should the fix target, and should it be backported?
2. Should a missing static file under ASGI produce exactly the same response as WSGI, including the debug 404 page when `DEBUG=True`?
3. Is calling the synchronous serve logic through a sync-to-async bridge acceptable, or is a natively async file-serving path expected?
4. Should the fix stay in `StaticFilesHandlerMixin`? Or should `BaseHandler.get_response_async` be hardened against `_middleware_chain` being `None`, which could benefit other handlers that skip middleware loading?
5. Where should the new tests live, and what command runs them in this repository?
6. Is a release note or documentation update required for this bug fix?