# Spec: HttpResponse support for `memoryview` content

## Assumptions

1. The bug is in Django's `HttpResponse`, imported via `from django.http import HttpResponse` as shown in the issue. The source file and function that convert content to bytes are not visible in the issue and are **unknown**.
2. A `memoryview` is currently treated as an unrecognized object and passed through `str()`. That produces `b'<memory at 0x...>'`. This is inferred from the observed output, not confirmed in source.
3. The expected result for `HttpResponse(memoryview(b"My Content")).content` is `b"My Content"`. That means it should behave the same as passing the equivalent `bytes` object.
4. The fix belongs in `HttpResponse` itself, not in the PostgreSQL backend or `BinaryField`. Having PostgreSQL return a `memoryview` for binary data is expected driver behavior.
5. Code that is already correct must keep working unchanged:
   - `str` content is encoded using the response charset.
   - `bytes` content is passed through.
   - Other objects are handled as they are today.
6. A `memoryview` should be treated as a single bytes-like value. It should not be treated as an iterable of chunks, even though it is iterable and iterating it yields ints.
7. The supported Python and Django versions for this change are **unknown**. The fix is assumed to target the current development branch.

## Objective

**Problem.** A developer reads a `BinaryField` from the database and writes the value into an `HttpResponse`.

- With SQLite the value is `bytes`, and the response body is correct.
- With PostgreSQL the value is a `memoryview`, and the response body becomes the object's repr, for example `b'<memory at 0x7fcc47ab2648>'`. This silently corrupts the output.

**Goal.** `HttpResponse` must accept `memoryview` content and produce the underlying bytes. Application code should then behave the same whichever database backend is used.

**Users.** Django application developers who serve binary data, such as files or images stored in a `BinaryField`, especially on PostgreSQL.

**Acceptance criteria (user stories):**

- When I pass a `memoryview` to the `HttpResponse` constructor, `response.content` equals `bytes(view)`.
- When I assign a `memoryview` to `response.content` after construction, `response.content` equals `bytes(view)`.
- When I pass `str` or `bytes`, the behavior is exactly as before.

## Tech Stack

- Language: Python. The supported versions are unknown.
- Framework: Django, specifically the `django.http.HttpResponse` component.
- Data source in the scenario: a PostgreSQL `BinaryField`, which yields `memoryview`. No specific database driver or version is given in the issue.

## Commands

- Build: unknown. Not stated in the issue.
- Test: unknown. Not stated in the issue. Expected to be the project's standard test runner, scoped to HTTP response tests.
- Lint: unknown.
- Dev: not applicable.

## Project Structure

- Location of the `HttpResponse` implementation: unknown. It is not visible in the issue.
- Location of the existing `HttpResponse` tests: unknown.
- Release notes or documentation location: unknown.

## Code Style

- No source code from the project is visible in the issue, so no style snippet can be given.
- Follow the existing conventions of the surrounding module. These are unknown here.
- The only observable behavior contract, taken from the issue:

```python
from django.http import HttpResponse

HttpResponse("My Content").content              # b'My Content'  (correct today)
HttpResponse(b"My Content").content             # b'My Content'  (correct today)
HttpResponse(memoryview(b"My Content")).content # expected b'My Content'
                                                # actual   b'<memory at 0x...>'
```

## Testing Strategy

- **Level.** Unit tests on `HttpResponse`. No database is needed, because the bug reproduces with a plain `memoryview(b"...")`.
- **Required cases:**
  1. Constructor with `memoryview(b"My Content")` gives `content == b"My Content"`.
  2. Setting `response.content = memoryview(b"My Content")` gives `content == b"My Content"`.
  3. Regression check: `str` and `bytes` content keep their current results.
  4. An empty `memoryview(b"")` gives `content == b""`.
  5. Non-ASCII or arbitrary binary bytes, such as `bytes(range(256))`, round-trip exactly with no charset encoding applied.
- **Optional integration test.** Store a `BinaryField` value, read it back on PostgreSQL, and return it in an `HttpResponse`. Whether this is needed depends on the Open Questions below.
- **Framework, test file location and coverage expectations:** unknown.

## Boundaries

**Always:**
- Keep existing behavior for `str`, `bytes` and other already-supported content types.
- Add regression tests that fail before the fix and pass after it.
- Treat `memoryview` as raw bytes. Never encode it with the response charset.

**Ask first:**
- Extending the change to other response classes, such as streaming or file responses.
- Extending it to other bytes-like types such as `bytearray`.
- Changing how iterables of chunks are handled.
- Any change to database backends or `BinaryField` conversion. That is out of scope by default.
- Adding release notes or documentation changes, if the project's policy on this is unclear.

**Never:**
- Change the PostgreSQL backend so that it returns `bytes`, as a substitute for fixing `HttpResponse`.
- Iterate the `memoryview` element by element. That yields ints and is incorrect.
- Remove or weaken existing response tests.

## Success Criteria

- `HttpResponse(memoryview(b"My Content")).content == b"My Content"`.
- `r = HttpResponse(); r.content = memoryview(b"My Content"); r.content == b"My Content"`.
- `HttpResponse("My Content").content == b"My Content"` and `HttpResponse(b"My Content").content == b"My Content"` still hold.
- Arbitrary binary data in a `memoryview` round-trips byte-for-byte.
- The full existing `HttpResponse` test suite passes with no regressions.

## Open Questions

1. Should other bytes-like types also be handled explicitly in the same change? Examples are `bytearray` and objects that support the buffer protocol. Is `bytearray` currently affected in the same way?
2. Should the same handling apply to chunks yielded by streaming responses, such as an iterable of `memoryview` objects in a streaming response, and to `HttpResponse.write()`?
3. Should this be treated as a bug fix and backported to stable release branches, or only fixed on the development branch?
4. Is a PostgreSQL-specific integration test wanted, or is a unit test with a plain `memoryview` enough?
5. Does this need a release note or documentation entry? If so, where do they live in the repository? That location is unknown.
6. What are the exact test command and test module location for `HttpResponse`? Both are unknown from the issue.