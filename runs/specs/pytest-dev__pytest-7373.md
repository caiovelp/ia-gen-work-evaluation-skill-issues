# Spec: Remove incorrect caching of skipif/xfail string-condition evaluation

## Objective

pytest evaluates string conditions in `@pytest.mark.skipif("...")` and `@pytest.mark.xfail("...")`, and it caches the result. The cache is implemented by `cached_eval` in `_pytest/mark/evaluate.py`, and its key is **only the condition string**. The result, however, also depends on the globals the string is evaluated against, which are the test item's module globals. When two modules use the same condition string but bind different values, the first result is reused for the second. That second result is wrong.

**Reproduction (from the issue):**

```py
# test_module_1.py
import pytest

skip = True

@pytest.mark.skipif("skip")
def test_should_skip():
    assert False
```

```py
# test_module_2.py
import pytest

skip = False

@pytest.mark.skipif("skip")
def test_should_not_skip():
    assert False
```

Running `pytest test_module_1.py test_module_2.py`:
- **Expected:** `test_should_skip` is skipped. `test_should_not_skip` runs and fails.
- **Actual:** both tests are skipped.

**Affected versions:** pytest 5.4.3 and current master at the time of the report.

**Users:**
- pytest users who write string conditions in `skipif`/`xfail` markers that refer to module-level names.
- Plugin authors who rely on the same evaluation path.

**Proposed direction (from the reporter):** remove the caching entirely and inline the logic of `cached_eval` into `MarkEvaluator._istrue`. This spec records that direction. It does not prescribe the implementation.

**User stories / acceptance criteria:**
- As a test author, when two modules use the same `skipif` condition string, each module's condition is evaluated against its own globals.
- As a test author, the same applies to `xfail` string conditions, because they share `MarkEvaluator`.
- As a test author, existing skipif/xfail behaviour is unchanged for:
  - boolean conditions
  - conditions with a `reason`
  - strings that reference `sys`, `os`, `platform`, `config`
  - strings that raise errors during evaluation

## Assumptions

1. Both `skipif` and `xfail` string conditions go through `MarkEvaluator._istrue` → `cached_eval`. Fixing `cached_eval` or its call site therefore fixes both markers.
2. The globals used for evaluation include the item's module globals, plus names pytest injects (`os`, `sys`, `platform`, `config`). The bug comes only from the cache key leaving out these globals.
3. `cached_eval` is internal (`_pytest` is a private package). Removing it is not a public-API break. Third-party plugins may still import it; see Open Questions.
4. Removing the cache has a negligible performance cost, because each condition is compiled and evaluated once per item instead of once per unique string. The reporter believes this, but it is not measured.
5. The cache is stored in some config-level storage that `cached_eval` uses. The exact mechanism and any associated key/attribute are **unknown** (not visible in the issue). If the cache is removed, that storage should be removed too.
6. The fix targets current master. Whether it is backported to the 5.4.x line is a maintainer decision.
7. Like other behaviour changes in the project, the fix needs a regression test and a changelog entry.

## Tech Stack

- Language: Python. Supported version range for current master is **unknown**.
- Project: pytest itself (internal module `_pytest.mark.evaluate`).
- Key components named in the issue: `cached_eval`, `MarkEvaluator._istrue`.
- Other dependencies or versions: **unknown**.

## Commands

All commands are **unknown**, because the repository is not visible. To be confirmed from the repo's contributing docs or tox config:

```
Build:   unknown
Test:    unknown (reproduction only: `pytest test_module_1.py test_module_2.py`)
Lint:    unknown
Dev:     unknown
```

## Project Structure

Only the following is known from the issue:

```
_pytest/mark/evaluate.py   → defines cached_eval and MarkEvaluator (_istrue); location of the bug
```

The full path prefix (e.g. whether `_pytest` sits under a `src/` directory), the location of the test suite, and the location of changelog fragments are all **unknown**.

## Code Style

- Follow the existing conventions of `_pytest/mark/evaluate.py`. These are not visible here, so they are **unknown**.
- Keep the change minimal. Per the reporter's proposal, this means removing the caching rather than redesigning condition evaluation.
- No style snippet is provided, because none can be quoted from the issue.

## Testing Strategy

- **Framework:** pytest's own test suite. It most likely uses the in-repo testing fixtures for running pytest on generated files, but the exact fixture names and test file locations are **unknown**.
- **Regression test (required):** generate two test modules with the same `skipif("skip")` string and different module-level `skip` values. Run them in a single session and assert that the outcome is 1 skipped and 1 failed.
- **Additional regression test (recommended):** the same scenario using `xfail("...")`, to cover the second marker that shares the evaluator.
- **Ordering coverage:** also run the modules in reverse order. This catches any residual order-dependent caching.
- **Existing tests:** all existing skipif/xfail/mark-evaluation tests must still pass. That includes any tests that reference `cached_eval` directly. If such tests exist, they need updating or removal, and that must be called out explicitly.
- **Coverage requirements:** **unknown** (project policy not visible).

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue scenario.
  - Run the full existing test suite before proposing the change.
  - Add a changelog entry if the project requires one.
  - Preserve the evaluation globals (`os`, `sys`, `platform`, `config`, module globals) exactly as they are today.
- **Ask first:**
  - Keeping a cache with a corrected key (e.g. string plus globals identity) instead of removing it.
  - Removing `cached_eval` as a symbol versus keeping it as a deprecated shim.
  - Backporting to a maintenance branch.
  - Any change to how errors in condition strings are reported.
- **Never:**
  - Change the semantics of non-string (boolean) conditions.
  - Change public marker signatures or behaviour beyond fixing the incorrect reuse.
  - Delete or weaken existing tests without approval.

## Success Criteria

1. With the two-module reproduction run as `pytest test_module_1.py test_module_2.py`:
   - `test_should_skip` is reported as skipped.
   - `test_should_not_skip` runs and fails.
2. The same result holds when the module order on the command line is reversed.
3. An equivalent `xfail("<string>")` scenario across two modules with differing globals evaluates each condition against its own module's globals.
4. Within a single module, repeated use of the same condition string still evaluates correctly. There is no functional regression from removing the cache.
5. String conditions that reference `sys`, `os`, `platform`, and `config` behave as before.
6. Condition strings that fail to evaluate produce the same kind of error report as before.
7. No caching keyed only by the condition string remains in the skipif/xfail evaluation path.
8. The new regression test(s) fail on the unfixed code and pass on the fixed code.
9. The full existing test suite passes.

## Open Questions

1. **Remove versus re-key the cache.** Should caching be removed entirely, as the reporter proposes, or kept with a key that includes the evaluation globals? Is there any known performance reason the cache was introduced?
2. **Symbol removal.** Can `cached_eval` be deleted outright, or do maintainers want a deprecation path because third-party plugins might import it from `_pytest`?
3. **Cache storage cleanup.** What storage or key does `cached_eval` currently use on the config object? Should it be removed along with the function?
4. **Release target.** Is this fix for master only, or should it be backported to the 5.4.x maintenance line?
5. **Changelog.** What changelog fragment type and location should be used (e.g. bugfix)? Is there a linked issue number to reference?
6. **Other consumers.** Does anything else in pytest (e.g. other marks, or the `config`-level evaluation of strings) call `cached_eval` and need the same treatment?
7. **Commands and paths.** What are the exact test, lint, and build commands, and the test-file locations to use for the regression test?