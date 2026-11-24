# Spec: Assertion rewriting must not treat a non-string leading constant as a module docstring

## Objective

When pytest's assertion rewriter processes a test module whose first statement is an expression with a numeric constant (for example a bare `0` or `123`), collection fails with:

```
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:695: in run
    if self.is_rewrite_disabled(doc):
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:760: in is_rewrite_disabled
    return "PYTEST_DONT_REWRITE" in docstring
E   TypeError: argument of type 'int' is not iterable
```

The rewriter takes the value of the module's first expression statement as the docstring and checks it for the `PYTEST_DONT_REWRITE` marker. It does this even when the value is not a string. Python itself only treats a string literal as a module docstring. A numeric constant is an ordinary expression statement.

**Users:** anyone whose test modules start with a non-string constant expression. Such modules may be generated, legacy, or written that way by accident. The reporter hit this while running `pytest -k xxx` over a large suite.

**Goal:** these modules collect and run normally, with assertion rewriting applied as usual. Only a real string docstring can disable rewriting through `PYTEST_DONT_REWRITE`.

**Acceptance criteria:**
- A test module whose first statement is an integer literal is collected without error, and its tests run.
- In that module, `assert` statements are still rewritten and give pytest's detailed assertion failure output.
- A module whose real string docstring contains `PYTEST_DONT_REWRITE` still has rewriting disabled.
- A module with a normal string docstring that lacks the marker is still rewritten.

## Assumptions

1. The bug is in pytest's assertion rewriting module (`_pytest/assertion/rewrite.py`), specifically in `AssertionRewriter.run` and `is_rewrite_disabled`, as the traceback shows.
2. The reporter is on pytest 7.4.0 and Python 3.8, according to the pip output and the traceback paths. The defect probably also exists on the current main branch, but that is not verified.
3. The trigger is a module whose first statement is a numeric constant expression. The reporter did not provide the file contents, so this is inferred from the error and the title.
4. Other non-string constants in docstring position may hit the same code path. Examples are floats, complex numbers, `None`, `True`/`False`, `...`, and bytes. Most of these would fail the same way, and bytes would be checked with incorrect semantics. All of them should be treated as "not a docstring".
5. `-k` is incidental. Any collection of the affected module triggers the error.
6. The operating system is not stated. Paths suggest Linux (`/usr/local/lib/python3.8`), but `pywinauto` and `comtypes` are installed. The bug is assumed to be OS-independent.
7. The non-ASCII directory names in the test path are unrelated to the bug.

## Tech Stack

- Language: Python. The reporter uses 3.8; the set of supported Python versions in the target branch is unknown.
- Project: pytest, using the `ast` module from the standard library.
- Reported version: pytest 7.4.0.
- Other dependencies: unknown and not relevant to this fix.

## Commands

Unknown, since there is no repository access. The following need to be filled in from the repository:
- Test: unknown (likely an invocation of pytest's own test suite on the assertion-rewrite tests)
- Lint: unknown
- Build: unknown
- Changelog entry procedure: unknown

## Project Structure

Only what the traceback shows is known:
- `_pytest/assertion/rewrite.py` → assertion rewriter (`AssertionRewriter.run`, `is_rewrite_disabled`, `_rewrite_test`, `rewrite_asserts`)
- `_pytest/python.py`, `_pytest/runner.py`, `_pytest/pathlib.py` → collection and import path (context only, should not need changes)

These locations are unknown: the test file for assertion rewriting, and the changelog directory or format.

## Code Style

Unknown. Follow the existing conventions in `_pytest/assertion/rewrite.py`. No snippet can be shown without repository access.

## Testing Strategy

- Framework: pytest's own test suite (exact file and location unknown).
- Add regression tests at the level of the assertion rewriter:
  - Module source starting with an integer constant expression. Expect rewriting to succeed with no exception, and asserts to be rewritten.
  - Optionally, parametrize over other non-string constants in first position (float, `None`, `True`, `...`, bytes).
  - Keep or confirm existing tests for a string docstring with `PYTEST_DONT_REWRITE` (rewrite disabled) and a string docstring without it (rewrite enabled).
- Optionally add an integration-level test: a test file starting with a number is collected and passes or fails with rewritten assertion output.
- Coverage expectations: unknown. At minimum, the new branch must be covered.

## Boundaries

- **Always:** keep `PYTEST_DONT_REWRITE` behavior unchanged for real string docstrings. Add a regression test that reproduces the `TypeError`. Follow existing code style and changelog conventions.
- **Ask first:** changing the signature or public behavior of `is_rewrite_disabled`, which plugins might call. Changing how docstrings are detected beyond the "must be a string" rule. Changing the supported Python versions.
- **Never:** disable rewriting for modules that start with non-string constants. Swallow the exception without fixing the detection. Change unrelated collection or import logic.

## Success Criteria

- Collecting a module whose first statement is `0` (or any integer literal) no longer raises `TypeError` and produces no collection error.
- Tests in that module run, and a failing `assert` shows rewritten, introspected output.
- Behavior is unchanged for modules with a real string docstring, with or without `PYTEST_DONT_REWRITE`, and for modules with no docstring.
- New regression tests fail before the change and pass after it.
- The full existing assertion-rewrite test suite passes.

## Open Questions

1. Can the reporter share the first lines of `test_socks_user_011.py` to confirm what the leading expression is: an integer, another constant, or something else?
2. Does the defect reproduce on the current main branch, or only on 7.4.0? Which branches should get the fix (backport policy)?
3. Should every non-string constant in docstring position be handled (float, `None`, bool, `...`, bytes), or only the reported int case? The recommendation is all of them.
4. Should a bytes constant in first position be explicitly treated as "not a docstring", given that `"PYTEST_DONT_REWRITE" in b"..."` raises a different `TypeError`?
5. Is `is_rewrite_disabled` considered public API? Should it also defend against non-string input, or should only the caller filter?
6. What are the project's exact test and lint commands, its changelog format, and the location of the assertion-rewrite tests?