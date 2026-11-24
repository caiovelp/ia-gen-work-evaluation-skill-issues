# Spec: Skip location reporting is correct under `--runxfail`

## Objective

When `--runxfail` is passed, pytest reports the wrong location for tests skipped via `@pytest.mark.skip` or `@pytest.mark.skipif`.

The reported location should point at the test item. With `--runxfail`, it points at pytest's own internals instead.

**Expected (`pytest -rs`):**
```
SKIPPED [1] test_it.py:3: unconditional skip
```

**Actual (`pytest -rs --runxfail`):**
```
SKIPPED [1] src/_pytest/skipping.py:238: unconditional skip
```

`--runxfail` exists only to make xfail-marked tests run and report as if they were not marked. It must have no effect on how skip/skipif marks are reported.

**Users:** pytest users who combine `-rs` (or other skip reporting) with `--runxfail`, such as CI pipelines that audit xfails while still relying on skip summaries.

**Acceptance criteria:**
- With `--runxfail`, a test skipped by `@pytest.mark.skip` reports its location as the test item's file and line, not a line in `src/_pytest/skipping.py`.
- The same holds for `@pytest.mark.skipif` with a true condition.
- Skip location reporting without `--runxfail` is unchanged.
- `--runxfail` behavior for xfail-marked tests is unchanged:
  - xfail tests still run.
  - Their outcomes are reported as if they were unmarked.

**Affected versions (per issue):** pytest 5.4.x and current master.

## Assumptions

1. The fault is in the `pytest_runtest_makereport` hook in `src/_pytest/skipping.py`, as the hint says. The `--runxfail` branch probably bypasses or short-circuits the logic that rewrites the skip location from pytest's internal raise site to the item's location.
2. The location rewrite applies only to skips that originate from skip/skipif *marks*. Imperative `pytest.skip()` calls inside a test body keep reporting their own call site, regardless of `--runxfail`.
3. "Location of the item" means the same value already reported when `--runxfail` is absent, i.e. the test definition's file and line as shown in the issue (`test_it.py:3`).
4. Line 238 in the issue reflects the version that was tested. The exact line number is not significant.
5. No change to public API, CLI options, or the report output format is intended.
6. The fix should be small and local to `src/_pytest/skipping.py`. No new dependencies.

## Tech Stack

- Python, pytest's own codebase (`src/_pytest/`).
- Supported Python versions, dependency versions: **unknown** (not visible from the issue).

## Commands

All unknown; the repository is not visible.

```
Build: unknown
Test:  unknown (pytest's own test suite; exact invocation/tox env not visible)
Lint:  unknown
Dev:   n/a
```

Reproduction, taken from the issue:
```
pytest -rs test_it.py              # expected location: test_it.py:3
pytest -rs --runxfail test_it.py   # currently wrong: src/_pytest/skipping.py:<line>
```

## Project Structure

- `src/_pytest/skipping.py`: implements skip/skipif/xfail marks and the `pytest_runtest_makereport` hook. This is where the bug lives.
- Test location for skipping behavior: **unknown**. A dedicated skipping test module likely exists under the repo's test directory, but its path has not been confirmed.
- Changelog/news fragment conventions: **unknown**.

## Code Style

Unknown. Not visible from the issue. Follow the existing conventions in `src/_pytest/skipping.py` and the existing skipping tests.

## Testing Strategy

- **Level:** integration-style tests that run an inner pytest session on a generated test file and assert on the `-rs` summary output. This assumes the repo's existing test-harness fixture for this (exact fixture name unknown; likely the one used by existing skipping tests).
- **New regression cases:**
  1. `@pytest.mark.skip` with `-rs --runxfail`: the summary line contains the test file and the test's line number, and does not contain `skipping.py`.
  2. `@pytest.mark.skipif(True, reason=...)` with `-rs --runxfail`: same assertion.
  3. Optionally, parametrize both cases over with and without `--runxfail` to lock in that the output is identical either way.
- **Regression guard:** the existing skipping and xfail tests, especially any that cover `--runxfail`, must still pass.
- **Coverage requirement:** unknown. At minimum, the new tests must fail before the fix and pass after it.

## Boundaries

- **Always:**
  - Keep the change confined to the skip-location handling in `pytest_runtest_makereport`.
  - Add regression tests that fail before the fix.
  - Run the existing skipping/xfail test suite.
- **Ask first:**
  - Changing `--runxfail` semantics for xfail tests.
  - Changing the report output format.
  - Touching files other than `src/_pytest/skipping.py` and its tests (and a changelog entry, if the project requires one).
- **Never:**
  - Alter location reporting for imperative `pytest.skip()` calls.
  - Remove or weaken existing tests.
  - Add dependencies.

## Success Criteria

- [ ] `pytest -rs --runxfail` on the issue's example prints `SKIPPED [1] test_it.py:3: unconditional skip`.
- [ ] Equivalent correct location for `skipif` under `--runxfail`.
- [ ] Output for skip/skipif with and without `--runxfail` is identical.
- [ ] Existing skipping, xfail, and `--runxfail` tests pass unchanged.
- [ ] New regression tests for skip and skipif under `--runxfail` are added and pass.

## Open Questions

1. Should `pytest.skip()` called from within a fixture or setup (not a mark) be covered here? Assumption: no, and its behavior stays as-is.
2. Does the project require a changelog/news fragment for bug fixes, and what is the naming convention?
3. What is the exact test command and environment (e.g. tox env) for running pytest's own skipping tests?
4. Should this fix be backported to the 5.4.x maintenance line, or land on master only?
5. Are there other `--runxfail` interactions (e.g. `xfail(strict=True)`, `xfail(run=False)`) that should be audited in the same change, or kept strictly out of scope?