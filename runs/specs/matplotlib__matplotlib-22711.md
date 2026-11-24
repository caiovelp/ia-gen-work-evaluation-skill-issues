# Spec: Fix `RangeSlider` initialization when `valinit` has equal endpoints

## Objective

A `RangeSlider` created with an initial value whose two endpoints are equal (e.g. `valinit=[0.0, 0.0]`) raises `IndexError` during construction:

```
File ".../matplotlib/widgets.py", line 778, in __init__
    self.set_val(valinit)
File ".../matplotlib/widgets.py", line 915, in set_val
    xy[4] = val[0], .25
IndexError: index 4 is out of bounds for axis 0 with size 4
```

`set_val` writes five vertices (`xy[0]` through `xy[4]`) into `self.poly.xy`. In the failing case the polygon has only four vertices.

**Goal:** Any valid two-element `valinit`, including equal endpoints, constructs a working slider. Later `set_val` calls must keep the slider's polygon, value text and callbacks consistent, whatever the current or new values are.

**Users:** Matplotlib users who build interactive widgets with `matplotlib.widgets.RangeSlider`. The issue's example is threshold selection on an image histogram.

**User stories**
- As a user, I can pass `valinit=[a, a]` (a zero-width range) and get a slider showing that range, with no exception.
- As a user, I can pass any `valinit` within `[valmin, valmax]` and the slider shows it.
- As a user, I can later call `set_val` to move from a zero-width range to a non-zero-width range, and back, in both orientations.

**Reporter's proposed fix (not adopted as-is):** Comment out the `xy[4] = ...` lines. This hides the symptom. It may also break the polygon's closing vertex in the normal case where the polygon has five vertices, because the first vertex is updated but the closing vertex is not. The fix must address why the vertex count differs. It must not simply remove the assignment unless that is shown to be correct.

**Suspected root cause (hypothesis, to verify):** The selection polygon is built from `valinit` before `set_val` runs. When the two endpoints are equal, the generated vertex list may already have its first and last points equal. The automatic polygon closing step then may not add a fifth vertex. The result is 4 vertices instead of 5, and `set_val` assumes a fixed vertex count. See Open Questions.

## Tech Stack

- Python. The reporter used 3.8.
- Matplotlib. The bug was reported on 3.5.1. The target branch is unknown.
- NumPy (`np.sort`, `np.asanyarray` in `set_val`).
- Affected module: `matplotlib/widgets.py`, class `RangeSlider` (`__init__`, `set_val`). The exact repository path is unknown; it is likely `lib/matplotlib/widgets.py`, which is unverified.

## Commands

- Build: unknown
- Test: unknown. A pytest-based suite is likely but not confirmed.
- Lint: unknown
- Dev / reproduce: run the reproduction script from the issue with `python <script>.py`.

## Project Structure

- `.../matplotlib/widgets.py` → `RangeSlider` implementation. The location is confirmed by the traceback; the repo-relative path is unknown.
- Widget tests → location unknown.
- Changelog / release notes → location and convention unknown.

## Code Style

These are the existing conventions visible in the issue's `set_val` excerpt:

```python
val = np.sort(np.asanyarray(val))
if val.shape != (2,):
    raise ValueError(
        f"val must have shape (2,) but has shape {val.shape}"
    )
```

- NumPy-style docstrings (`Parameters` / `----------`).
- f-strings for error messages.
- Orientation is handled with `if self.orientation == "vertical": ... else: ...`.
- Follow the project's linting rules. The tool is unknown.

## Testing Strategy

- Framework: unknown. Pytest is assumed.
- Add regression tests in the existing widget test module (location unknown) that cover:
  - Construction with `valinit` equal endpoints, at `valmin`, at `valmax` and at an interior value, for both `orientation="horizontal"` and `orientation="vertical"`.
  - After construction, `slider.val` equals the clipped and sorted `valinit`.
  - The polygon's vertices match the expected rectangle for the given values. If the polygon is meant to be closed, the closing vertex equals the first vertex.
  - `set_val` transitions: zero-width → non-zero-width → zero-width, in both orientations, with no exception and with correct vertices after each call.
  - A non-regression check: a normal construction such as `valinit=(min+δ, max-δ)` still produces the same vertices as before the fix.
  - `on_changed` callbacks still fire with the sorted value tuple when `eventson` is true.
- Test level: unit tests using a non-interactive backend. No image comparison is needed unless the project's convention requires it (unknown).

## Boundaries

- **Always:**
  - Keep the public `RangeSlider` API and signature unchanged.
  - Handle both orientations.
  - Add regression tests.
  - Keep the `ValueError` for wrong-shaped values.
- **Ask first:**
  - Changing the type of `self.poly` (for example, from the object returned by span creation to a different artist).
  - Changing what `slider.val` returns (array vs tuple).
  - Backporting to maintenance branches.
  - Changing how the default `valinit` is computed.
- **Never:**
  - Fix by only commenting out `xy[4]` without verifying that polygon closure is still correct in the normal case.
  - Silently change a user-supplied `valinit` to avoid a degenerate range, for example by adding an epsilon.
  - Change unrelated widgets.

## Success Criteria

1. The issue's reproduction script runs without exception and displays a slider initialized at `(0.0, 0.0)`.
2. `RangeSlider(ax, label, vmin, vmax, valinit=[x, x])` succeeds for any `x` within bounds, in both orientations.
3. `slider.val` after construction equals `valinit`, sorted and clipped to the bounds.
4. The polygon's vertices always describe the rectangle `[val[0], val[1]] × [.25, .75]` (horizontal) or `[.25, .75] × [val[0], val[1]]` (vertical). This holds after construction and after every `set_val`, including transitions between zero and non-zero width.
5. Existing `RangeSlider` and widget tests pass unchanged.
6. New regression tests fail before the fix and pass after it.

## Assumptions

1. The bug is caused by `valinit` having equal endpoints. The issue does not say this explicitly, but `[0.0, 0.0]` is the only unusual input in the reproduction. `img.min() < 0 < img.max()` for the seeded random data, so the value is within bounds.
2. A zero-width range (`val[0] == val[1]`) is a valid, supported state for `RangeSlider`. It is not an input to reject.
3. The polygon is normally a closed 5-vertex shape, which is why `set_val` writes `xy[4]`.
4. The bug may still exist on the current main branch. This is unverified against the current source.
5. The fix belongs inside `RangeSlider`, in polygon construction and/or `set_val`, rather than in the generic polygon/patch classes.
6. A non-interactive backend is enough to test this behavior.

## Open Questions

1. Is the hypothesis correct that the polygon ends up with 4 vertices because equal endpoints make the first and last generated vertices coincide, so automatic closing is skipped? This needs confirmation against the current source.
2. Which fix direction should we take?
   - (a) Make `set_val` independent of the vertex count.
   - (b) Make the polygon always have a fixed vertex count, for example by constructing it explicitly rather than via span creation.
   - (c) Replace the polygon with a different artist, such as a `Rectangle`, which is a possible API-visible change.
3. Does the bug reproduce on the current main branch, or has it already been fixed? Which branch should the fix target, and should it be backported?
4. Are there other degenerate inputs that hit the same path? Examples: both endpoints clipped to the same bound (e.g. `valinit=[valmax+1, valmax+2]`), or `valmin == valmax`.
5. Should a zero-width range be drawn visibly (for example as a thin line or handle), or is an invisible zero-area polygon acceptable?
6. What are the repository's test, lint and build commands, and where do the widget tests live?
7. Is a changelog or "API changes / bug fixes" entry required for this kind of fix?