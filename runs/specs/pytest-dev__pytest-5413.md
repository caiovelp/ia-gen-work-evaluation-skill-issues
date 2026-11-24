# Spec: Make `str()` on the `pytest.raises` context variable stop hiding the exception message

## Objective

**Problem.** In pytest 4.6.2, `pytest.raises(...)` binds an exception-info object to `e` in `with pytest.raises(...) as e`. Calling `str()` on that object returns a location-style summary that contains only the first line of the message:

```
<console>:3: LookupError: A
```

Users expect the full message, which is what `str(exc)` returns after an ordinary `try/except`:

```
A
B
C
```

The documented way to get the message is `str(e.value)`. The reporter says the different behavior is a gotcha and asks for it to be removed.

**Who is affected.** Test authors who assert on exception messages through the `pytest.raises` context variable, for example `assert "B" in str(e)`. With the current behavior, an assertion on any line after the first fails. Worse, a substring assertion can pass because it matches the file or location prefix instead of the message.

**What success looks like.** `str()` on the context variable no longer returns a truncated, location-prefixed string that users mistake for the exception message. Two fixes are possible, and the maintainers must choose one (see Open Questions):

- **Option A (equivalence):** `str(e)` returns exactly `str(e.value)`.
- **Option B (no misleading `__str__`):** the custom string form is removed, so `str(e)` falls back to `repr(e)`. That output is clearly an info-object repr, not a message, and users are pushed toward `e.value`.

Either way, the result must be documented, and the behavior change must be handled according to the project's compatibility policy.

### User stories / acceptance criteria

- As a test author, when I call `str()` on the `pytest.raises` context variable, I never get a string that looks like the exception message but is silently truncated to its first line.
- As a test author, `str(e.value)` keeps returning the full exception message, unchanged.
- As a test author upgrading pytest, I can find this behavior change in the changelog and docs, along with the recommended idiom (`str(e.value)`, or `match=`).

## Assumptions

1. The object bound by `pytest.raises(...) as e` is pytest's exception-info object (`ExceptionInfo`). Its `__str__` produces the `path:lineno: ExcType: first-line` format shown in the issue.
2. The first-line truncation is caused by `__str__` using a short, location-based representation. It is not caused by f-strings, by the `LookupError` type, or by macOS. Any exception whose message spans multiple lines is affected.
3. The reporter's Python is 3.6 or later, since the example uses f-strings. The bug does not depend on the Python version.
4. `repr(e)` and `e.value`, and the other public attributes of the info object (`type`, `tb`, `match()`, `getrepr()`, etc.), must keep their current behavior unless the chosen option says otherwise.
5. Changing `str()` on a public object is a user-visible behavior change. It may require a deprecation period, or must land in a major release, under pytest's backward-compatibility policy.
6. The many unrelated packages in the reporter's `pip list` (moto, boto, pandas, pytest-cov, etc.) do not affect this behavior.
7. Other internal callers inside pytest may rely on the current `str()` output, for example in reporting or in `match()`. Those callers must be identified and kept working.

## Tech Stack

- Python (supported versions for the target pytest release: **unknown**)
- pytest, reported against 4.6.2. The target version/branch for the change is **unknown**.
- Relevant plugin/runtime deps from the report: pluggy 0.12.0, py 1.8.0. Their relevance is unconfirmed.

## Commands

The issue gives no commands. All of the following are **unknown** and must come from the pytest repository's contributor docs or CI config:

```
Build:  unknown
Test:   unknown
Lint:   unknown
Docs:   unknown
```

## Project Structure

Not visible from the issue. **Unknown**:

- Location of the `ExceptionInfo` implementation and its `__str__`/`__repr__`
- Location of the `pytest.raises` implementation
- Location of tests for `ExceptionInfo` / `pytest.raises`
- Location of the user docs that describe `pytest.raises` and `excinfo.value`
- Changelog mechanism, for example per-issue fragments (**unknown**)

## Code Style

The repository's style is not visible. Follow the conventions of the existing pytest codebase and its configured formatter/linter, both **unknown**.

The behavior to pin down, using only the reporter's example:

```python
# Reference behavior (plain Python)
try:
    raise LookupError("A\nB\nC")
except LookupError as exc:
    assert str(exc) == "A\nB\nC"

# Target behavior under Option A
with pytest.raises(LookupError) as e:
    raise LookupError("A\nB\nC")
assert str(e) == str(e.value) == "A\nB\nC"

# Target behavior under Option B
with pytest.raises(LookupError) as e:
    raise LookupError("A\nB\nC")
assert str(e) == repr(e)          # not the message, not a truncated location line
assert str(e.value) == "A\nB\nC"  # unchanged
```

## Testing Strategy

- **Framework:** pytest's own test suite. The exact layout and invocation are **unknown**.
- **Unit tests** on the exception-info object:
  - A multi-line message with `str(e)` follows the chosen option.
  - A single-line message with `str(e)` follows the chosen option. This is a regression guard for the common case.
  - `str(e.value)` is unchanged for single- and multi-line messages.
  - `repr(e)` is unchanged, unless Option B redefines what `str()` falls back to.
  - An exception with an empty message, and a non-`str` argument such as `LookupError(42)`, behave consistently under the chosen option.
- **Integration tests:**
  - The `pytest.raises(..., match=...)` behavior is unchanged for multi-line messages.
  - Failure reporting output for a test that raises is unchanged. This guards against internal callers of `str(excinfo)`.
- **Deprecation tests (if a deprecation path is chosen):** calling `str()` on the info object emits the agreed warning type and text.
- **Coverage expectation:** **unknown**, follow the project's existing policy. Every changed code path must be covered by a new or updated test.

## Boundaries

- **Always:**
  - Keep `e.value` semantics exactly as they are.
  - Add tests that reproduce the issue's example: multi-line message, `str()` on the context variable.
  - Add a changelog entry and update the `pytest.raises` docs to state the `str()` behavior and recommend `str(e.value)` / `match=`.
  - Run the full test suite before submitting.
- **Ask first:**
  - Which option to take (A, B, or keep and document only).
  - Whether to ship with a deprecation warning first or as a direct change in a major release.
  - Changing `repr()` of the info object.
  - Changing any internal pytest code that consumes `str(excinfo)`.
  - Adding dependencies.
- **Never:**
  - Change the exception object itself, or how exceptions are raised or caught.
  - Silently change failure-report formatting as a side effect.
  - Remove or weaken existing tests without approval.
  - Backport a breaking behavior change to a maintenance branch without a maintainer decision.

## Success Criteria

1. For `pytest.raises(LookupError) as e` around `raise LookupError("A\nB\nC")`, `str(e)` no longer returns `"<location>: LookupError: A"`. It returns either `"A\nB\nC"` (Option A) or `repr(e)` (Option B), per the decision.
2. `str(e.value) == "A\nB\nC"` still holds.
3. `match=` on multi-line messages behaves exactly as before.
4. pytest's own failure/traceback output for raised exceptions is byte-identical to before, for the existing test cases in the suite.
5. The documentation for `pytest.raises` explicitly describes what `str(e)` returns and points to `e.value` for the exception and its message.
6. A changelog entry references this issue and describes the behavior change. If a deprecation is chosen, it also gives the deprecation timeline.
7. All existing tests pass, and the new tests from the Testing Strategy pass.

## Open Questions

1. **Which fix should we make?** Option A (`str(e) == str(e.value)`), Option B (drop the custom `__str__` so `str()` falls back to `repr()`), or no code change, only clearer docs? Option A matches user intuition but makes the info object partially impersonate the exception. Option B removes the gotcha without implying equivalence.
2. **Compatibility path:** must this go through a deprecation warning in a minor release first, or can it land directly in the next major release? Which release or branch is the target?
3. Do any **internal pytest callers** or known plugins depend on the current `path:lineno: ExcType: first-line` output of `str(excinfo)`? If so, should they move to an explicit method rather than `str()`?
4. Should the current location-style summary stay available through an explicitly named method for users who rely on it? Does such a method already exist on the object (**unknown**)?
5. If Option A is chosen, should `repr(e)` also change, or stay as is?
6. What are the repository's build, test, lint, and docs commands, and where do the relevant source, test, doc, and changelog files live? All are unknown from the issue.