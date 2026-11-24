# Spec: `ax.bar` must not raise when all x positions are NaN (regression in 3.6.1)

## Assumptions

1. The regression comes from the 3.6.1 change that made `Axes._convert_dx` call `cbook._safe_first_finite(x0)`. The release note says "Fix barplot being empty when first element is NaN", and the traceback ends in that function.
2. `cbook._safe_first_finite` raises `StopIteration` when no element is finite. `_convert_dx` catches only `(TypeError, IndexError, KeyError)`, so the `StopIteration` escapes to the caller.
3. The correct behaviour is the 3.6.0 behaviour. Bars are created with NaN geometry, and no exception is raised. The fix for "first element is NaN" from 3.6.1 must keep working.
4. The same code path (`_convert_dx`) also handles `xerr` in `bar`, and probably `barh` (y/height and `xerr`/`yerr`). Any other caller of `_convert_dx` is assumed to be affected in the same way.
5. The fix belongs inside matplotlib. No change is expected in seaborn.
6. The scope is a bug fix. No public API changes, deprecations, or new parameters.

## Objective

Restore the 3.6.0 behaviour so that `Axes.bar` (and related callers of `Axes._convert_dx`) do not raise when every x position passed is non-finite (NaN). The 3.6.1 fix that handles a NaN in the *first* position must keep working.

**User:** Downstream libraries (seaborn's histogram, which draws and removes a "phantom" all-NaN bar to advance the color cycle) and end users who plot data that may be entirely NaN.

**Acceptance criteria (user stories):**
- As a seaborn user, calling `histplot` no longer fails on matplotlib with this fix.
- As a matplotlib user, `ax.bar([np.nan], [np.nan])` returns a `BarContainer` with one `Rectangle` whose x and height are NaN. This matches 3.6.0.
- `ax.bar([np.nan], [0])` does not raise. It currently raises.
- `ax.bar([0], [np.nan])` continues to work.
- `ax.bar([np.nan, 1, 2], [1, 2, 3])`, the case fixed in 3.6.1, still produces non-empty bars at the finite positions.

## Tech Stack

- Python library: matplotlib. Affected version 3.6.1, last good version 3.6.0.
- NumPy (NaN inputs).
- Affected code, from the traceback:
  - `matplotlib/axes/_axes.py`: `Axes.bar`, `Axes._convert_dx`
  - `matplotlib/cbook/__init__.py`: `_safe_first_finite`
- Supported Python and NumPy versions: unknown.

## Commands

Unknown. No repository access. Exact build, test, and lint commands must be confirmed from the project.
- Build: unknown
- Test: unknown (probably pytest-based; to be confirmed)
- Lint: unknown
- Repro (from issue):
  ```python
  import numpy as np
  import matplotlib.pyplot as plt
  f, ax = plt.subplots()
  ax.bar([np.nan], [np.nan])
  ```

## Project Structure

Only these paths are known from the traceback:
```
lib?/matplotlib/axes/_axes.py      → Axes.bar, Axes._convert_dx (exact source root unknown)
lib?/matplotlib/cbook/__init__.py  → _safe_first_finite
```
- Test locations: unknown (to be confirmed; likely the existing axes and cbook test modules).
- Changelog / release-notes location: unknown.

## Code Style

Unknown beyond the snippets in the traceback. Follow the existing style of `_axes.py` and `cbook`. Relevant existing pattern from the traceback:

```python
try:
    x0 = cbook._safe_first_finite(x0)
except (TypeError, IndexError, KeyError):
    pass
```

Formatting and lint rules are unknown.

## Testing Strategy

- Framework: unknown (assumed pytest).
- Add regression tests for:
  1. `ax.bar([np.nan], [np.nan])` returns one bar, and its `get_x()` and `get_height()` are NaN.
  2. `ax.bar([np.nan], [0])` does not raise.
  3. `ax.bar([0], [np.nan])` does not raise (guards existing behaviour).
  4. A mixed case where the first element is NaN and later ones are finite still draws the finite bars (guards the 3.6.1 fix).
  5. `barh` equivalents of cases 1–2, if `barh` shares the path.
  6. `bar` with all-NaN x and non-`None` `xerr` does not raise.
- If `_safe_first_finite` changes behaviour, add a unit test for it with an all-non-finite input. The expected behaviour is an open question.
- Existing unit/units tests (datetime + timedelta widths, unit-wrapped arrays such as `pint`) must still pass.

## Boundaries

- **Always:** Keep the 3.6.0 return shape for all-NaN input (a container with NaN rectangles). Keep the 3.6.1 first-NaN fix. Add regression tests that reproduce the issue first.
- **Ask first:** Changing the public or semi-public contract of `cbook._safe_first_finite`, since other callers may depend on it. Changing how units or datetime widths are converted. Adding a release note or API-change note.
- **Never:** Drop the NaN bars silently, which would change the number of artists returned. Revert the 3.6.1 fix wholesale. Introduce public API changes for a bugfix release.

## Success Criteria

- [ ] The reproduction script from the issue runs without exception and returns a `BarContainer` of length 1 with NaN x and height.
- [ ] `ax.bar([np.nan], [0])` and `ax.bar([0], [np.nan])` both run without exception.
- [ ] Bar plots whose first x is NaN but with later finite x still render the finite bars, as in 3.6.1.
- [ ] No `StopIteration` escapes from `_convert_dx` for any all-non-finite input (x, `xerr`, and the `barh` variants if applicable).
- [ ] Existing test suite passes. New regression tests are added and pass.
- [ ] seaborn's histogram path, which draws and removes a phantom NaN bar, works. This can be verified with a minimal equivalent of the phantom-bar call.

## Open Questions

1. Where should the fix go? Options:
   - (a) `_convert_dx` also catches `StopIteration`, or falls back to the first element.
   - (b) `_safe_first_finite` returns a fallback, such as the first element or NaN, when no finite value exists.
   
   Option (b) affects every caller of `_safe_first_finite`. Which callers exist, and what do they expect?
2. When there is no finite x, what fallback value should `x0` take in `_convert_dx`? The first raw element, or should the width be passed through unconverted?
3. Which PR introduced the "Fix barplot being empty when first element is NaN" change? Linking it would confirm the intended behaviour and its tests. The reporter also asked whether release notes could link to PRs.
4. Should `_safe_first_finite` keep its current semantics (raise when no finite value exists) for other callers, or is raising `StopIteration` from it considered a bug in general?
5. Is this targeted for a 3.6.x patch release? If so, are there backport constraints?
6. Do other plotting functions call `_convert_dx` or `_safe_first_finite` (for example `errorbar`, `broken_barh`, `fill_between`)? Should all-NaN input be covered for them in this change?
7. What are the exact test commands, test file locations, and changelog conventions for the repository?