# Spec: `format_cursor_data` must not crash for artists using `BoundaryNorm`

## Objective

In Matplotlib 3.5.0 (and `main` at the time of the report), hovering the mouse over a `ScalarMappable` artist (e.g. an `AxesImage` from `imshow`) whose norm is a `matplotlib.colors.BoundaryNorm` raises an exception. Cursor-data formatting stops, and so does interactive feedback.

**Root cause, as shown in the traceback:**

- `Artist.format_cursor_data` (`lib/matplotlib/artist.py`, ~line 1282) calls `self.norm.inverse(...)` to find neighboring data values. It uses those neighbors to choose how many significant digits to display.
- `BoundaryNorm.inverse` (`lib/matplotlib/colors.py`, ~line 1829) unconditionally raises `ValueError("BoundaryNorm is not invertible")`.

**Goal:** Hovering over a `BoundaryNorm`-normalized artist shows a sensible formatted data value in the status bar. No exception is raised and interaction continues.

**Users:** Anyone using interactive backends with discrete or binned colormaps via `BoundaryNorm`. This includes `imshow`, `pcolormesh`, and similar artists that inherit `format_cursor_data`.

**User story:** As a user hovering over a `BoundaryNorm`-colored image, I see the pixel's data value, formatted to a reasonable precision. Mouse interaction keeps working.

**Reproduction (from the issue):**

```python
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

fig, ax = plt.subplots()
norm = mpl.colors.BoundaryNorm(np.linspace(-4, 4, 5), 256)
X = np.random.randn(10, 10)
pc = ax.imshow(X, cmap='RdBu_r', norm=norm)
# mouse over the image -> ValueError: BoundaryNorm is not invertible
```

**Candidate approaches named in the issue.** These need a decision; see Open Questions.

1. Special-case `BoundaryNorm` inside `format_cursor_data`.
2. Wrap the `norm.inverse` call in a try/except and fall back to a default precision.
3. Make `BoundaryNorm` approximately invertible.

## Assumptions

1. The crash happens for any `ScalarMappable` artist that relies on `Artist.format_cursor_data` with a `BoundaryNorm`, not only `AxesImage`.
2. The neighbor/inverse computation exists only to determine display precision. The displayed value itself is the raw data value, which is always available without inverting the norm.
3. The fix targets `main` and may be backported to the 3.5.x bugfix line.
4. Other norms (`Normalize`, `LogNorm`, etc.) currently behave correctly. Their cursor output must not change.
5. Other non-invertible norms, such as custom user norms whose `inverse` raises, may hit the same crash. A robust fix should ideally not crash for them either.
6. A test can call `format_cursor_data` directly with a data value, without simulating real mouse events.
7. The project uses pytest with tests under `lib/matplotlib/tests/`. This is inferred convention only; it is not confirmed by the issue.

## Tech Stack

- Python, NumPy, Matplotlib (affected version: 3.5.0 / `main`).
- Exact supported Python and NumPy versions: **unknown**.

## Commands

All unknown; none are given in the issue.

- Build/install: **unknown**
- Test: **unknown** (likely pytest, unconfirmed)
- Lint: **unknown**
- Docs build: **unknown**

## Project Structure

Only these files are known from the traceback:

```
lib/matplotlib/artist.py   → Artist.format_cursor_data (calls norm.inverse, ~line 1282)
lib/matplotlib/colors.py   → BoundaryNorm.inverse (raises ValueError, ~line 1829)
```

- Test file location for the regression test: **unknown** (possibly `lib/matplotlib/tests/test_artist.py` or `test_image.py`, unconfirmed).
- Changelog / API-change note location: **unknown**.

## Code Style

**Unknown** from the issue; follow existing conventions in `artist.py` and `colors.py`. No code snippet is available beyond the reproduction above.

## Testing Strategy

- **Regression test:** Create an artist with `BoundaryNorm(np.linspace(-4, 4, 5), 256)`. Call `format_cursor_data` for several data values and assert that no exception is raised and a string is returned.
- **Value correctness:** Assert the expected formatted strings for representative values, including:
  - a value inside a bin
  - a value exactly on a boundary
  - values below the lowest and above the highest boundary
  - values within the first and last bins
  - The exact expected precision depends on the chosen approach (Open Question 1).
- **`extend` variants:** Cover `BoundaryNorm` with `extend='neither' | 'min' | 'max' | 'both'` and with `ncolors` both equal to and greater than the number of bins.
- **Masked/NaN data:** Cursor formatting of masked or NaN values still behaves as before (no crash).
- **Non-regression:** Existing `format_cursor_data` tests for other norms still pass unchanged.
- **Inverse behavior:** If `BoundaryNorm.inverse` changes, add direct unit tests for it. If it does not change, keep or confirm the test that it still raises `ValueError`.
- Coverage requirement: **unknown**.

## Boundaries

**Always:**
- Keep cursor output for all other norms identical to the current output.
- Add a regression test that reproduces the issue scenario.
- Run the existing test suite before committing.

**Ask first:**
- Changing the public behavior of `BoundaryNorm.inverse`, e.g. making it return values instead of raising. This is an API change.
- Adding a generic try/except that silently swallows errors from arbitrary norms.
- Changing the significant-digits algorithm for all norms.

**Never:**
- Change how `BoundaryNorm` maps data to colors (`__call__`).
- Remove or weaken existing tests.
- Let `format_cursor_data` propagate exceptions into the event loop for this scenario.

## Success Criteria

1. Running the reproduction and hovering over the image produces no exception, and the status bar shows a formatted data value.
2. `format_cursor_data` returns a string for every data value tested with `BoundaryNorm`, across all `extend` modes and including values outside the boundaries.
3. Displayed precision for `BoundaryNorm` is reasonable and deterministic. Expected outputs are fixed in tests once Open Question 1 is resolved.
4. Cursor output for `Normalize`, `LogNorm`, and other existing norms is unchanged; existing tests pass.
5. A regression test for this issue exists and fails on the unfixed code.
6. Any public API change is documented. Whether one is needed is pending Open Question 2.

## Open Questions

1. **Which approach is preferred?**
   - Special-case `BoundaryNorm`: for example, derive precision from the spacing of neighboring boundaries.
   - A generic try/except fallback.
   - Making `BoundaryNorm` approximately invertible.
2. **Should `BoundaryNorm.inverse` remain raising?** Making it approximately invertible changes public API semantics, and callers may rely on the `ValueError`.
3. **What precision should `BoundaryNorm` values get?** Options are a fixed default (e.g. 3 significant digits), precision based on bin width, or something else.
4. **What precision applies outside the boundaries?** For data below `boundaries[0]` or above `boundaries[-1]`, especially with `extend`, there is no finite neighboring bin.
5. **Should the fix also protect against any other non-invertible norm** (e.g. user-defined norms), or be scoped strictly to `BoundaryNorm`?
6. **Should this be backported to the 3.5.x bugfix branch?**
7. **Do other `format_cursor_data` overrides need the same fix?** Some subclasses may compute neighbors differently.
8. **Where should the regression test live, and what are the exact test and lint commands?**