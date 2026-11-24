# Spec: Restore Tolerant Handling of an Empty `If-Modified-Since` Header

## Assumptions

1. **Project identity.** The issue wording and the commit-hash style suggest this is the Django web framework. The issue does not say so; this needs confirmation.
2. **Prior behavior.** Before commit `d6aff369ad3`, an empty-string `If-Modified-Since` value was treated as if the header were absent. In practice that meant the "resource has been modified" path ran and a full response was served. The phrase "used to be ignored" implies this, but I have not checked it against code.
3. **Regression source.** Commit `d6aff369ad3` changed how `If-Modified-Since` is parsed or validated. Its exact contents, and the function or module it touched, are unknown because I have no repository access.
4. **Exception type.** The exception is an unhandled error raised while parsing the header, probably a `TypeError`, `AttributeError` or `ValueError` from a failed regex match or date parse. The exact type and traceback are not in the issue.
5. **Intended semantics.** An empty `If-Modified-Since` header should be treated as absent or invalid. That matches RFC 9110 §13.1.3, which says a recipient must ignore the header if the field value is not a valid HTTP-date.
6. **Scope.** The fix should restore the previous behavior only. It should not redesign conditional-request handling or touch `If-None-Match`, `If-Unmodified-Since` and similar headers, unless they share the same broken code path.
7. **Single capability.** This is one independently testable capability, so no capability map (Phase 0) is needed.

## Objective

**What:** Restore the behavior where an empty-string `If-Modified-Since` request header is silently ignored. Since commit `d6aff369ad3`, it raises an exception instead.

**Why:** Clients, proxies or test clients can send `If-Modified-Since: ` with an empty value. A server-side exception there turns a harmless malformed header into a server error (probably HTTP 500). That is a regression from earlier behavior and violates the HTTP rule that an invalid conditional date is ignored.

**Users affected:**
- End users whose browsers or intermediaries send an empty header.
- Application developers serving static files or conditional responses through the affected code path.
- Test suites that pass `HTTP_IF_MODIFIED_SINCE=""` or an equivalent value.

**Acceptance criteria (user-story form):**
- As a client sending `If-Modified-Since` with an empty value, I get the same response as if I had omitted the header, with no server error.
- As a maintainer, I have a regression test that fails on the code at `d6aff369ad3` and passes after the fix.

## Tech Stack

- **Language:** Python (assumed from the likely Django context; version unknown)
- **Framework:** Django is assumed; this is unconfirmed and the version or branch is unknown.
- **Key dependencies:** Unknown

## Commands

The issue does not show any project commands. All are unknown:

```
Build: UNKNOWN
Test:  UNKNOWN (likely the project's own test runner; exact invocation not visible)
Lint:  UNKNOWN
Dev:   UNKNOWN
```

## Project Structure

Unknown. The module or function that parses `If-Modified-Since` and was changed by `d6aff369ad3` is not identified in the issue. It must be located by inspecting that commit.

```
<source module touched by d6aff369ad3>  → UNKNOWN: where the header is parsed/compared
<corresponding test module>             → UNKNOWN: where regression tests should live
```

## Code Style

Unknown, since no code is visible. Follow the conventions of the module modified by `d6aff369ad3` and its existing tests.

## Testing Strategy

- **Framework:** Unknown. Use the project's existing test framework and runner.
- **Location:** Put the tests next to the existing tests for the affected function or view. The exact path is unknown.
- **Test levels:**
  - **Unit test** on the header-checking function with an empty-string header value. It should return the "modified / serve full response" result and must not raise.
  - **Integration or view-level test**, if such tests already exist for this path. A request with `If-Modified-Since: ""` should return a normal successful response (e.g. 200), not a 304 and not an error.
- **Regression property:** The new test must fail against the code at or after `d6aff369ad3` without the fix, and pass with it.
- **Non-regression:** Existing tests for valid, missing and malformed `If-Modified-Since` values must keep passing.
- **Coverage expectation:** Unknown project-wide. At minimum, the empty-string branch must be covered.

## Boundaries

- **Always:**
  - Keep the fix minimal and limited to the code path changed by `d6aff369ad3`.
  - Add a regression test for the empty-string case.
  - Run the existing related test suite before finalizing.
  - Preserve the behavior for valid dates, a missing header, and other already-handled malformed values.
- **Ask first:**
  - Changing the public signature or return contract of the affected function.
  - Widening the fix to other conditional headers.
  - Changing how other malformed (non-empty) header values are handled.
  - Reverting `d6aff369ad3` wholesale rather than patching it.
- **Never:**
  - Swallow broad exceptions in a way that hides unrelated bugs.
  - Remove or weaken existing tests.
  - Change response semantics for valid `If-Modified-Since` values.

## Success Criteria

1. A request with an empty-string `If-Modified-Since` header no longer raises an exception in the affected code path.
2. That request gets the same response as a request without the header, i.e. a full response rather than 304 Not Modified.
3. A regression test covering the empty-string case exists and passes. It fails without the fix.
4. All pre-existing tests for the affected function or view still pass.
5. Behavior for valid HTTP-date values, a missing header, and previously handled invalid values is unchanged.

## Open Questions

1. Is this the Django project? If so, which branch or version should get the fix, and does it need backporting?
2. Which function or module did `d6aff369ad3` change, and what exactly did it change about parsing `If-Modified-Since`?
3. What exception type and traceback does the empty string trigger?
4. Should other malformed values be handled the same way in this fix, or does only the empty string need restoring? Examples: whitespace-only values, garbage strings, or a header with a size/length suffix but an empty date.
5. Does `d6aff369ad3` affect other conditional headers (`If-Unmodified-Since`, `If-None-Match`, `If-Match`) in the same way, and should they be in scope?
6. What are the project's exact test, lint and build commands, and where do the tests for this code path live?
7. Is a release note or changelog entry required for this regression fix?