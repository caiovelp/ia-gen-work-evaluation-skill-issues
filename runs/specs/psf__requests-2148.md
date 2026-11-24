# Spec: Wrap socket errors raised while streaming a response body in a requests exception

## Assumptions

1. The fix belongs in the requests library. The traceback shows requests 2.3.0 with its vendored urllib3 at `requests/packages/urllib3/`. It does not belong in the user's application.
2. The error happens **after** response headers were received, while the body is being read. The path is `Response.content` → `Response.iter_content` → `generate()` → `urllib3 HTTPResponse.stream()` → `read()` → `httplib` → `socket.recv`. It does not happen during `Session.send()` / adapter connect, where connection errors are presumably already wrapped.
3. The intended wrapper is `requests.exceptions.ConnectionError`, which the reporter suggests. The fact that `ConnectionError` exists suggests this is the established mapping for network-level failures.
4. gevent is incidental. The same `socket.error` (errno 104, `ECONNRESET`) would surface with the standard-library socket, because gevent's `recv` only re-raises the OS error.
5. Python 2.7 is in scope, since that is the reporter's environment. Whether Python 3 is also in scope is unknown. On Python 3, `socket.error` is an alias of `OSError` and `ConnectionResetError` is a subclass of it.
6. Other exceptions already handled in `generate()` should keep their current behavior. The exact set of those exceptions is unknown because the code is not visible.
7. Existing callers who catch `socket.error` directly should not break, if possible. Whether that is a hard requirement is an open question.

## Objective

**Problem:** A consumer of requests receives a raw `socket.error: [Errno 104] Connection reset by peer` when the peer resets the connection during body streaming. This happens when accessing `response.text`, `response.content`, or iterating `iter_content()`. The consumer must then know about low-level transport exceptions to handle a routine network failure.

**User:** Application developers using requests. They expect every network failure that occurs within requests' public API to arrive as a subclass of `requests.exceptions.RequestException`.

**User story:** As a requests user, I can write `except requests.exceptions.RequestException` (or `ConnectionError`) around both the request call and the body access. A connection reset mid-body is then caught there, without my also needing `except socket.error`.

**Success looks like:** A socket-level error raised while reading the response body surfaces as `requests.exceptions.ConnectionError`. The original error stays available for debugging.

## Tech Stack

- Language: Python. The reported version is 2.7.6; the full supported matrix is unknown.
- Library: requests. The reported version is 2.3.0; the target branch and version are unknown.
- Vendored dependency: urllib3 under `requests/packages/urllib3/`. Its version is unknown.
- Stdlib involved: `httplib` (Py2) / `http.client` (Py3), `socket`.
- Optional, seen in the report: gevent 1.0.1.

## Commands

Unknown. The repository is not visible, so no build, test, or lint commands can be stated.

```
Build: unknown
Test:  unknown
Lint:  unknown
```

## Project Structure

Only the paths visible in the traceback are known. Line numbers refer to requests 2.3.0 and may differ on the target branch.

```
requests/models.py                     → Response.text (~l.721), Response.content (~l.694),
                                          iter_content / inner generate() (~l.627)
requests/exceptions.py                 → presumed location of ConnectionError (not seen; unknown)
requests/packages/urllib3/response.py  → HTTPResponse.stream() (~l.240), read() (~l.187)
tests/                                 → unknown location/layout
```

## Code Style

Unknown. No project code beyond traceback lines is visible, so the change should follow the existing conventions in `requests/models.py`.

## Testing Strategy

- The framework and test location are unknown. The change should use whatever the repository's existing test suite uses.
- **Unit level (required):** Simulate the response's raw stream raising `socket.error` (errno `ECONNRESET`) while `iter_content` / `content` / `text` is reading. Assert that `requests.exceptions.ConnectionError` is raised. This needs no network.
- **Regression level:** Existing tests for exceptions already translated in `iter_content` (for example decoding or incomplete-read errors, if present) must keep passing unchanged.
- **Optional integration level:** A local server sends headers plus a partial chunked body and then resets the socket. This is optional because it may be flaky or platform-dependent.
- Coverage expectations are unknown.

## Boundaries

- **Always:**
  - Preserve the original exception for debugging, either as an argument or message of the wrapper or via chaining where the Python version supports it.
  - Keep the existing handling of other exceptions in the streaming path intact.
  - Add a test reproducing the reset-during-body case.
- **Ask first:**
  - Modifying vendored urllib3 under `requests/packages/` rather than handling the error in `requests/models.py`.
  - Wrapping additional exception types beyond socket-level errors, such as all `IOError`/`OSError`.
  - Changing the exception hierarchy in `requests/exceptions.py`, for example making `ConnectionError` also subclass `socket.error` for backward compatibility.
  - Any change to public API signatures.
- **Never:**
  - Silently swallow the error or return truncated content as if it were successful.
  - Discard the original exception information.
  - Add new third-party dependencies.
  - Depend on gevent-specific behavior.

## Success Criteria

1. If the underlying socket raises `socket.error` / `OSError` while `Response.iter_content()` is iterating, the caller receives `requests.exceptions.ConnectionError`. This covers a connection reset (errno 104) during a chunked body read.
2. Criterion 1 also holds when the body is accessed via `Response.content` and `Response.text`, since both go through `iter_content`.
3. The raised `ConnectionError` is catchable as `requests.exceptions.RequestException`.
4. The original socket error, including its errno and message, can be recovered from the raised exception, for example in its args or message.
5. Behavior for successfully read bodies is unchanged. Previously translated exceptions are still raised as before.
6. A new automated test covers criterion 1 without requiring network access, and it passes alongside the existing suite.
7. If `stream=True` reads via `iter_lines()` exist and go through `iter_content`, they inherit the same behavior. This needs confirmation; see Open Questions.

## Open Questions

1. **Accident or design?** Is leaking raw socket errors from body reads intentional, as the reporter asks? If it is intended, is the outcome a documentation change instead of a code change?
2. **Which exception class?** Should a mid-body reset be `ConnectionError`? Or would a different or new `RequestException` subclass better express "connection lost while reading the body"?
3. **Backward compatibility:** Users may already catch `socket.error` around `response.content`. Is breaking them acceptable? Should the new exception also be an instance of `socket.error`/`IOError`? Is `RequestException` already an `IOError` subclass? That cannot be verified here.
4. **Where to fix:** In `requests/models.py` (`generate()` in `iter_content`), or upstream in urllib3's `HTTPResponse.read()`/`stream()`, mapping to a urllib3 exception that requests then translates? Does the requests project patch vendored urllib3 directly?
5. **Scope of exception types:** Only `socket.error`? Or also related errors such as `httplib.IncompleteRead`, `ssl.SSLError` during body read, and socket timeouts? Should a read timeout map to a timeout exception instead of `ConnectionError`?
6. **Direct `response.raw` use:** Should errors from reading `response.raw` directly also be wrapped, or is raw access documented as low-level and exempt?
7. **Target versions:** Which requests branch/version and which Python versions (2.x and/or 3.x) must the fix support?
8. **Repository details:** What are the test framework, test locations, and run/lint commands? All are unknown from the issue.