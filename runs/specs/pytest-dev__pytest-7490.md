# Spec: Restore dynamic `xfail` markers added during test execution (pytest 6 regression)

## Objective

**Problem.** In pytest 5.x, a test could add an `xfail` marker to itself at runtime with `request.node.add_marker(pytest.mark.xfail(...))`. If the test then failed, it was reported as **xfailed**, just like a test with a static `@pytest.mark.xfail`. In pytest 6.0.0rc0/rc1 the same test is reported as **failed** (`F`). This is a behavioral regression.

**Reproducer (from the issue):**

```python
# file: test_foo.py
import pytest


def test_xfail_test(request):
    mark = pytest.mark.xfail(reason="xfail")
    request.node.add_marker(mark)
    assert 0
```

| Version | `pytest -rsx test_foo.py` result |
|---|---|
| 5.4.3 | `x`, summary line `XFAIL test_foo.py::test_xfail_test` with reason `xfail`, `1 xfailed` |
| 6.0.0rc1 | `F`, `AssertionError` at `assert 0`, test counted as failed |

**Users.** Test authors, for example in pandas, who decide at runtime whether a test is expected to fail. Typical inputs for that decision are parametrization values, fixture values, or the environment. They do this by adding an `xfail` marker from inside the test body or from a fixture.

**Goal.** An `xfail` marker added dynamically to a test item before or during its call phase controls the test outcome the same way a statically applied `xfail` marker does, matching pytest 5.x behavior.

## Assumptions

1. The regression comes from pytest 6 evaluating `xfail` markers once, early (at setup or before the call), and caching the result. Markers added later, inside the test body, are therefore never seen. This is inferred from the symptoms and has not been verified against the source.
2. The supported API is `node.add_marker(...)`, called on `request.node` or on an item reached in a hook or fixture. Other ways of mutating markers are out of scope.
3. A dynamic `xfail` should honor the same arguments as a static one: `reason`, `condition`, `raises`, `strict`, and `run`. The issue only exercises `reason`.
4. `run=False` cannot apply retroactively once the test body is already executing. For a marker added inside the body, only the outcome-reporting arguments matter.
5. A dynamic `xfail` added during the call phase applies to the call-phase outcome. Whether it should also affect setup or teardown outcomes is not required here (see Open Questions).
6. The `--runxfail` option should treat dynamic `xfail` markers like static ones, meaning they are ignored.
7. The fix targets the pytest 6.0.x line, before or at the final 6.0.0 release, and is covered by a changelog entry.
8. OS and Python version do not matter. The report used macOS 10.14.5 and Python 3.7.6.

## Tech Stack

- Project: pytest (Python). Supported Python versions for the 6.0 line: **unknown**, not given in the issue.
- Related package from the report: pluggy 0.13.0.
- Affected area: the `xfail` / skipping marker evaluation and reporting logic. The exact module is **unknown** because the repository is not visible.

## Commands

All **unknown**, since the repository is not visible. Only the user-level reproduction command is known:

```
Reproduce: pytest -rsx test_foo.py
Build:     unknown
Test:      unknown (presumably the project's own pytest/tox setup)
Lint:      unknown
```

## Project Structure

**Unknown.** The locations of the source module that handles `xfail` evaluation, the matching test file, and the changelog directory or format must be confirmed from the repository.

## Code Style

**Unknown.** Follow the existing conventions of the pytest codebase, including type annotations if the surrounding code uses them. No in-repo snippet is available to quote.

## Testing Strategy

- **Level:** in-process functional tests that run a generated test file through pytest and assert on the outcomes. The existing helper for this (pytest's `pytester`/`testdir`-style fixture) is assumed to be available; its exact name in this version is unknown.
- **Required regression tests:**
  1. A dynamic `xfail` added in the test body, followed by a failing assertion, gives 1 xfailed and 0 failed. The reason is shown with `-rx`/`-rsx`.
  2. A dynamic `xfail(strict=True)` on a test that then **passes** gives a failed result (`[XPASS(strict)]`), matching static strict behavior.
  3. A dynamic non-strict `xfail` on a test that passes gives xpassed.
  4. A dynamic `xfail(raises=SomeError)` where the test raises a different exception gives a regular failure.
  5. A dynamic `xfail` added from a fixture during setup gives xfailed when the test fails. This behaved correctly before and must not regress.
  6. With `--runxfail`, a dynamic `xfail` on a failing test gives a normal failure.
  7. Existing static `xfail` tests all still pass unchanged.
- **Coverage expectation:** all new branches in the `xfail` evaluation and reporting path are exercised by the tests above. The numeric coverage target is unknown.

## Boundaries

- **Always:**
  - Add regression tests reproducing the issue before or alongside the fix.
  - Keep static `xfail` semantics unchanged.
  - Add a changelog entry in the project's format (format unknown).
- **Ask first:**
  - Changing public APIs or hook signatures.
  - Changing when `xfail(run=False)` is evaluated.
  - Changing behavior for markers added during teardown.
  - Changing the outcome of `skip`/`skipif` markers added dynamically.
  - Adding dependencies.
- **Never:**
  - Turn dynamic-marker usage into an error or deprecation without maintainer approval.
  - Weaken or delete existing skipping/xfail tests.
  - Modify vendored code.

## Success Criteria

- [ ] Running `pytest -rsx test_foo.py` on the reproducer with the fixed pytest reports `x`, `XFAIL test_foo.py::test_xfail_test` with reason `xfail`, and `1 xfailed`. Exit code is 0.
- [ ] Dynamic `xfail` honors `strict`, `raises`, and `reason` the same way a static `xfail` does (tests 2–4).
- [ ] `--runxfail` disables dynamic `xfail` the same way it disables static `xfail` (test 6).
- [ ] Dynamic `xfail` added in fixtures during setup still works (test 5).
- [ ] The full existing pytest test suite passes with no changes to existing expectations.
- [ ] A changelog entry references this regression.

## Open Questions

1. Should an `xfail` marker added during the **call** phase be re-evaluated only for the call report, or also for teardown? What about a marker added during teardown?
2. When both a static and a dynamic `xfail` are present, which one's `reason`/`strict`/`raises` wins? The proposal is to keep the existing "first matching marker" semantics. Is that right?
3. Was the pytest 6 change to evaluate `xfail` early intentional, for example for performance or to fix another bug? If so, the fix must not reintroduce whatever that change addressed. Which issue or PR introduced it?
4. Should `skip`/`skipif` markers added dynamically during the call phase be addressed in the same change, or left as they are?
5. Should the dynamic-marker pattern be documented explicitly as supported, given that this regression shows it is relied upon?
6. What are the repository's test, lint, and changelog commands and paths? All are unknown here.