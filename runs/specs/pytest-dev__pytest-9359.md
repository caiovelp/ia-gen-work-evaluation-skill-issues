# Spec: Fix assertion failure excerpt that includes trailing decorator lines (Python 3.8+)

## Objective

When an `assert` fails, pytest prints the source of the failing statement. If the next statement after the `assert` is a **decorated** function or class, the excerpt on Python 3.9 also includes the blank line and the decorator line(s) (`@t`) that follow the assert. On Python 3.7 the excerpt correctly stops at the end of the `assert`.

**Users:** anyone whose failing test has an `assert` followed by a decorated nested definition. The issue reports pytest 6.2.5 on Windows 10 with Python 3.9.6.

**Success means:** the failure excerpt for an `assert` covers exactly that statement's lines on every supported Python version. Lines that belong to the following statement, including its decorators, are not shown.

### Observed vs. expected (from the issue)

Input test:

```python
def test_right_statement(foo):
    assert foo == (3 + 2) * (6 + 9)

    @t
    def inner():
        return 2

    assert 2 == inner
```

Observed on Python 3.9.6:

```
    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
    
        @t
E       assert 1 == 75
```

Expected, matching Python 3.7.10:

```
    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
E       assert 1 == 75
```

### User stories / acceptance

- As a test author, when an `assert` fails, I see only the lines of that `assert`, whatever statement follows it.
- As a test author on Python 3.7 and 3.9+, I get the same excerpt for the same code.

## Assumptions

1. The bug is in how pytest computes the line range of the failing statement, as the reporter suggests. It is not in the assertion rewriting or in the comparison message, because the `E` lines are correct.
2. **Unverified hypothesis:** starting with Python 3.8, the AST `lineno` of a decorated `FunctionDef`/`ClassDef` points at the `def`/`class` line instead of the first decorator. If pytest ends the current statement at the start of the next statement node, it would end at the `def` line and pull in the decorator lines. This must be confirmed against the actual source before any fix.
3. Under the same hypothesis, a decorated `class` and multiple stacked decorators would trigger the same behaviour. The issue only shows a single function decorator.
4. The blank line between the `assert` and `@t` is part of the same leak. It is not a separate bug.
5. The OS (Windows) is not a factor. The `allure-pytest` plugin in the 3.9 run is not a factor either, since it is absent from the 3.7 run but has no plausible effect on source excerpts. This should still be confirmed.
6. The fix targets the current development line of pytest, not a backport to 6.2.x, unless maintainers decide otherwise.
7. Module-level decorated definitions, such as `outer` in the example, are not involved here. The failing statement is inside the test function.

## Tech Stack

- Language: Python. The affected versions reported are 3.9.6 (bug present) and 3.7.10 (bug absent).
- Project: pytest. Reported against 6.2.5.
- Exact supported Python range for the target branch: **unknown**.
- Relevant module / function computing statement ranges: **unknown** (not visible in the issue).

## Commands

All unknown. No repository access, and the issue shows no project commands.

```
Build: unknown
Test:  unknown (likely a pytest/tox invocation; exact command and env names not visible)
Lint:  unknown
Dev:   unknown
```

Reproduction, derived from the issue:

```
pytest -v test_statement.py   # with the test file from the issue, on Python 3.9
```

## Project Structure

Unknown. No repository layout is visible in the issue. Needed:
- the location of the source-excerpt and statement-range code
- the location of the existing tests for that code
- whether a changelog-fragment directory exists

## Code Style

Unknown. Follow the existing conventions of the surrounding pytest code and its configured linters and formatters, once those are identified.

## Testing Strategy

- **Framework:** pytest itself (self-tests). The exact test file locations are unknown.
- **Regression tests (required):**
  1. **Unit level:** for source like the issue's example, the computed statement range for the line `assert foo == ...` contains only that line.
  2. **Integration level:** run a test file equivalent to the issue's example and check that the failure output does **not** contain the decorator line `@t` in the source excerpt, and does contain the `>` line for the assert.
- **Variants to cover:**
  - a single decorator on a nested function
  - multiple stacked decorators
  - a decorated nested class
  - a decorator with arguments that spans multiple lines
  - a multi-line `assert` followed by a decorated definition, to check that the full assert is still shown
  - an `assert` followed by a comment and then a decorated definition
- **Non-regression:** existing source / traceback-excerpt tests must still pass.
- **Python versions:** the tests must pass on every Python version the target branch supports. The behaviour must be identical on versions before and after 3.8.

## Boundaries

- **Always:**
  - Reproduce the bug with a failing test before changing behaviour.
  - Keep the excerpt behaviour for statements not followed by decorated definitions unchanged.
  - Run the full existing test suite.
- **Ask first:**
  - Changing the public or semi-public API of the source/code-excerpt utilities.
  - Dropping support for any Python version.
  - Backporting to a maintenance branch.
  - Adding dependencies.
- **Never:**
  - Change assertion-rewriting output (the `E` lines).
  - Suppress or delete existing failing tests.
  - Special-case the literal decorator name or the issue's exact example.

## Success Criteria

1. Running the issue's example on Python 3.9+ shows exactly this excerpt: the `def test_right_statement(foo):` line, then the `>` assert line, then the `E` lines. There is no blank line and no `@t` line.
2. Each variant in the Testing Strategy shows only the failing statement's lines.
3. The new regression tests fail before the fix and pass after it, on all supported Python versions.
4. The full existing test suite passes with no changes to unrelated expected outputs.
5. Output for the issue's example is identical on Python versions before and after 3.8.

## Open Questions

1. Which pytest branch or version should receive the fix, and should it be backported to 6.2.x?
2. What is the minimum supported Python version on the target branch? This decides whether pre-3.8 AST behaviour still needs to be handled.
3. Which module or function computes the statement range for failure excerpts, and where are its tests?
4. Are other consumers of the same statement-range logic affected and in scope? Examples: traceback entries for non-assert failures, and `--tb` styles other than the default.
5. Can the reporter confirm the bug reproduces without `allure-pytest` installed?
6. Does the project require a changelog entry for bug fixes, and in what format and location?
7. Are the test, lint, and CI commands defined in tox or another runner, and what are the exact invocations?