# Spec: Correct `__repr__` for `RepeatedKFold` and `RepeatedStratifiedKFold`

## Assumptions

1. The fix targets the current development branch of scikit-learn. The reporter's version (0.21.2) is used only to reproduce the bug.
2. The two classes live in the module `sklearn.model_selection._split`. The default repr in the issue's Actual Results shows this path.
3. Other cross-validation splitters in the same module (e.g. `KFold`, `StratifiedKFold`) already produce a `ClassName(param=value, ...)` repr. The two repeated splitters should match that existing convention rather than introduce a new one.
4. The expected strings in the issue were typed at a REPL without the surrounding quotes. The requirement is about the *content* of the string returned by `repr(...)`, not about quoting.
5. The defaults are `n_splits=5`, `n_repeats=10` and `random_state=None`, as shown in the issue's Expected Results. The constructor signatures themselves are not changed.
6. Parameter order follows the issue's expected output: `n_splits`, `n_repeats`, `random_state`. If the existing splitter-repr convention orders parameters differently (e.g. alphabetically), that convention wins. See Open Questions.
7. The repr should show the values the user actually passed, not only the defaults. For example, `RepeatedKFold(n_splits=3, n_repeats=2, random_state=0)` should repr as exactly that.
8. This is a display-only change. Splitting behaviour (`split`, `get_n_splits`) and public attributes must not change.

## Objective

`repr()` on `RepeatedKFold` and `RepeatedStratifiedKFold` currently returns Python's default object repr, e.g. `<sklearn.model_selection._split.RepeatedKFold object at 0x...>`. Users who print or log CV configurations cannot see how these splitters were configured, and the output is inconsistent with other scikit-learn splitters.

**User:** anyone inspecting, logging or debugging a scikit-learn cross-validation setup. This includes reprs nested inside other objects, such as a `GridSearchCV` whose `cv` is one of these splitters.

**Acceptance (from the issue):**

```text
repr(RepeatedKFold())            == "RepeatedKFold(n_splits=5, n_repeats=10, random_state=None)"
repr(RepeatedStratifiedKFold())  == "RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=None)"
```

## Tech Stack

- Python and the scikit-learn library, `sklearn.model_selection` subpackage.
- Supported Python, NumPy and SciPy versions for the target branch are unknown and not given in the issue.
- The reporter's environment was Python 3.7.4, sklearn 0.21.2 and numpy 1.16.4 on Windows 10. This is for reproduction only.

## Commands

The project's build, test and lint commands are unknown because they cannot be seen from the issue.

- Build: unknown
- Test: unknown. The relevant test file for `model_selection._split` is also unknown.
- Lint: unknown
- Reproduce (taken directly from the issue):
  ```python
  from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
  repr(RepeatedKFold())
  repr(RepeatedStratifiedKFold())
  ```

## Project Structure

- `sklearn/model_selection/_split.py` is the module that defines both classes. This is inferred from the repr module path shown in the issue.
- The location of the test file is unknown.
- Whether a changelog or "what's new" entry is required, and where it goes, is unknown.

## Code Style

- Follow the existing conventions in `sklearn.model_selection._split`. The repr mechanism used by sibling splitters should be reused, not reimplemented. The exact helper is unknown here.
- No new public API or new constructor parameters.

## Testing Strategy

- Unit tests asserting the exact repr string for:
  - `RepeatedKFold()` and `RepeatedStratifiedKFold()` with defaults, matching the strings in Objective.
  - Both classes constructed with non-default `n_splits`, `n_repeats` and an integer `random_state`.
  - Optionally, a `random_state` that is a `RandomState` instance. The expected rendering follows existing convention; see Open Questions.
- A regression check that `split` / `get_n_splits` outputs are unchanged for a fixed `random_state`.
- Where the existing test suite has a generic "all splitters have a proper repr" check, include both classes in it rather than excluding them.
- The test framework and command are unknown.

## Boundaries

- **Always:**
  - Keep `split` and `get_n_splits` behaviour identical.
  - Keep constructor signatures and defaults identical.
  - Add tests for both classes.
  - Match the repr format of sibling splitters.
- **Ask first:**
  - Renaming or adding public attributes, e.g. exposing `n_splits` as a new attribute only to support the repr.
  - Changing repr behaviour of any other splitter.
  - Changing parameter order away from the issue's expected output.
- **Never:**
  - Change splitting results or random-number consumption.
  - Change default parameter values.
  - Remove or weaken existing tests.

## Success Criteria

1. `repr(RepeatedKFold())` returns exactly `RepeatedKFold(n_splits=5, n_repeats=10, random_state=None)`.
2. `repr(RepeatedStratifiedKFold())` returns exactly `RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=None)`.
3. With non-default arguments, e.g. `n_splits=3, n_repeats=2, random_state=0`, the repr shows those values.
4. The repr no longer contains `object at 0x`.
5. Splits generated with a fixed `random_state` are identical before and after the change.
6. All existing tests pass, and new tests covering items 1–5 are added.

## Open Questions

1. Should parameter order be `n_splits, n_repeats, random_state`, as in the issue, or whatever order the existing splitter-repr convention produces? If the two differ, which wins?
2. How should a non-`None`, non-int `random_state` (a `RandomState` instance) be rendered? Is the existing convention for other splitters acceptable?
3. Are there other splitters with the same defect, e.g. other "repeated" or wrapper splitters, that should be fixed in the same change? Or is the scope strictly these two classes?
4. Is a changelog entry required, and for which release?
5. Which branch or version is the target, and should this be backported?