# Spec: Technical 404 Response When a Path Converter's `to_python()` Raises `Http404`

## Assumptions

1. The project is Django. The affected areas are URL resolution (path converters, the URL resolver) and the DEBUG-mode technical 404 debug view. The issue does not name exact module paths, so they are listed as unknown below.
2. The reported plain-text response ("A server error occurred. Please contact the administrator.") comes from the WSGI server's fallback handler. That would mean an exception escapes Django's own request/exception handling, rather than Django rendering a 500 page.
3. The likely mechanism is this: the DEBUG 404 rendering path itself performs URL resolution, or relies on resolver-specific exception types. An `Http404` that is not a resolver-specific "not found" exception is then raised inside the error-rendering code and is not handled. This is a hypothesis to verify, not a confirmed root cause.
4. Raising `ValueError` in `to_python()` must keep its current documented meaning: "this pattern does not match, try the next one."
5. The fix should make raising `Http404` from `to_python()` produce a normal 404 response:
   - with `DEBUG = True`, the technical 404 page;
   - with `DEBUG = False`, the standard 404 handling (`handler404`).
   It should not produce a server error.
6. Whether `Http404` should *stop* resolution, rather than fall through to later patterns, is a design question. It is raised under Open Questions. The baseline requirement is only "no unhandled server error; a proper 404 is returned."
7. Normal behaviour must remain unchanged for views that raise `Http404` and for URLs that match no pattern.

## Objective

**Problem.** A developer writes a custom path converter whose `to_python()` raises `Http404`, for example by calling `get_object_or_404`. With `DEBUG = True`, a request matching that pattern does not return a 404. Instead, the server returns the generic plain-text message "A server error occurred. Please contact the administrator." This gives the developer no useful debugging information.

**Users.** Django developers writing custom path converters, especially those who intuitively reach for `Http404`, or who intentionally use it to mean "this is the right route, but the object does not exist."

**Goal.** Raising `Http404` in a converter's `to_python()` results in a proper 404 response:
- With `DEBUG = True`: the technical 404 page, including the exception message when one was provided.
- With `DEBUG = False`: the standard 404 response.
- In no configuration: a crash or a generic server error.

**User stories**
- As a developer using DEBUG mode, when my converter raises `Http404("No Foo with id 42")`, I see Django's technical 404 page showing that message. I do not see a generic server error.
- As a developer in production (`DEBUG = False`), when my converter raises `Http404`, the client receives a 404 response rendered by the configured 404 handler.
- As a developer, when my converter raises `ValueError`, resolution continues to the next URL pattern exactly as it does today.

## Tech Stack

- Python / Django. Exact versions are unknown and not stated in the issue.
- Components involved:
  - path converters (`to_python()`)
  - the URL resolver
  - the `Http404` / resolver "not found" exception types
  - the DEBUG technical 404 view
- Exact module/file paths are **unknown** (not visible in the issue).

## Commands

All commands are **unknown**; the issue does not include repository or tooling details.
- Build: unknown
- Test: unknown (presumably Django's own test runner; exact invocation unknown)
- Lint: unknown
- Dev: unknown

## Project Structure

**Unknown.** No repository access. The relevant locations are:
- the URL resolution / converters code
- the DEBUG views code (technical 404 rendering)
- the corresponding test suites for URL resolution and debug views

## Code Style

**Unknown.** Follow the existing conventions of the surrounding code in the project. No example is available from the issue.

## Testing Strategy

The framework and locations are unknown. The test levels required are:

- **Regression test (DEBUG = True).** Define a URL pattern using a custom converter whose `to_python()` raises `Http404` with a message. Request a matching URL and assert all of the following:
  - the status code is 404, not 500;
  - the response is the technical 404 page;
  - the response contains the `Http404` message.
- **Regression test (DEBUG = False).** Use the same setup and assert that the status code is 404 and that the standard 404 handling is used.
- **Non-regression: `ValueError`.** A converter raising `ValueError` still causes fall-through to the next matching pattern. When nothing else matches, the existing "Django tried these URL patterns" technical 404 is shown.
- **Non-regression: unmatched URL.** The existing technical 404 output for an unmatched URL is unchanged.
- **Non-regression: view-raised `Http404`.** A view raising `Http404` still renders the technical 404 (DEBUG) or the standard 404 (non-DEBUG).
- **Unit test.** If the root cause is in the technical 404 rendering, add a direct test that the rendering code handles an `Http404` raised during its internal resolution without propagating it.

Coverage expectations are unknown. At minimum, each success criterion below should have a test.

## Boundaries

**Always**
- Preserve `ValueError` semantics in `to_python()` (no match, try the next pattern).
- Add regression tests for both `DEBUG = True` and `DEBUG = False`.
- Keep the change minimal and local to where the unhandled exception originates.

**Ask first**
- Changing resolver semantics so that `Http404` from a converter halts resolution instead of falling through. This is a behavioural or API change.
- Updating documentation to officially endorse raising `Http404` from `to_python()`.
- Changing the content or layout of the technical 404 template.

**Never**
- Swallow `Http404` so that it silently becomes a 200 or a different error.
- Convert the situation into a 500 response or a generic server error.
- Change the behaviour of view-raised `Http404` or unmatched-URL 404s.

## Success Criteria

1. With `DEBUG = True`, a request whose matching pattern's converter raises `Http404("msg")` returns HTTP 404 with the technical 404 page, and `msg` appears in the response.
2. With `DEBUG = False`, the same request returns HTTP 404 via the standard 404 handling.
3. In neither configuration does the server return "A server error occurred. Please contact the administrator." or any 5xx response.
4. A converter raising `ValueError` behaves exactly as before: fall-through to the next pattern.
5. Existing technical 404 output for unmatched URLs and for view-raised `Http404` is unchanged. The existing test suite passes.
6. Root cause confirmed: the location where the `Http404` escapes unhandled is identified and documented in the change description.

## Open Questions

1. **Intended semantics of `Http404` in `to_python()`.** Should it:
   - (a) simply be rendered as a proper 404, with whatever resolution behaviour results; or
   - (b) explicitly halt URL resolution, meaning "this is the right route, but the object doesn't exist," and skip later patterns?

   The issue argues for (b). This affects resolver behaviour and needs a decision.
2. Should the documentation be updated to state that raising `Http404` in `to_python()` is supported, for example for `get_object_or_404`-style converters? Alternatively, should the documentation continue to recommend only `ValueError`?
3. Which Django version(s) should the fix target, and is a backport expected?
4. Should the technical 404 page show the converter's `Http404` message in place of the "Django tried these URL patterns" list, alongside it, or both?
5. Is the failure also reproducible with `DEBUG = False`, or is it specific to the DEBUG technical 404 path? The issue only reports `DEBUG = True`.
6. What are the exact test, lint, and build commands and the file locations in the repository? These are unknown from the issue.