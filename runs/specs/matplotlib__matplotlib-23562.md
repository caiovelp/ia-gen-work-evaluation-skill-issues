# Spec: `Poly3DCollection.get_facecolors()` Must Not Raise Before the Collection Is Drawn

## Assumptions

1. The bug is in the 3D toolkit (`mpl_toolkits/mplot3d/art3d.py`), in `Poly3DCollection.get_facecolors` / `get_facecolor`. The traceback shows `return self._facecolors2d`.
2. `_facecolors2d` is created only when the collection is projected or drawn, not at construction. So any access before the first draw raises `AttributeError`. This is inferred from the traceback and the reproducer, which never draws the figure. It is not verified against source.
3. The edge-color getters (`get_edgecolors` / `get_edgecolor`) probably have the same flaw if they read a draw-time attribute such as `_edgecolors2d`. This is unverified.
4. The fix targets the current development branch. The reported versions (1.3.1, 1.4.2, Python 2.7) are historical. The reproducer must be re-run on the current version first, and any API difference since then must be recorded.
5. The public contract is "getters return an Nx4 RGBA array and never raise `AttributeError`." The exact colors returned before any draw are a design decision; see Open Questions.
6. No new dependencies and no public API additions are needed.

## Objective

Users who create a 3D surface or polygon collection (for example with `ax.plot_surface(..., cmap=...)`) get an `AttributeError` when they call `get_facecolors()` / `get_facecolor()` before the figure has been rendered. They expect the standard `Collection` behavior: an RGBA array of face colors.

**User story:** As a matplotlib user, I can call `get_facecolor(s)` (and `get_edgecolor(s)`) on the object returned by `plot_surface` or on any `Poly3DCollection`, at any time after creation. I get a valid RGBA array whether or not the figure has been drawn.

**Reproducer (from the issue):**
```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

y, x = np.ogrid[1:10:100j, 1:10:100j]
z2 = np.cos(x)**3 - np.sin(y)**2
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
r = ax.plot_surface(x, y, z2, cmap='hot')
r.get_facecolors()   # currently: AttributeError: ... no attribute '_facecolors2d'
```

## Tech Stack

- Python, with NumPy. The supported version range is unknown.
- matplotlib core plus the `mpl_toolkits.mplot3d` toolkit (`art3d.Poly3DCollection`, `Axes3D.plot_surface`).
- Exact versions are unknown. The issue reports 1.3.1 and 1.4.2.

## Commands

All commands are **unknown**, because there is no repository access. They must be taken from the project's contributor docs or CI configuration.

- Build/install (dev): unknown
- Test: unknown. Pytest is likely, but the exact invocation and the path to the mplot3d tests are unconfirmed.
- Lint: unknown

## Project Structure

Known from the traceback:
```
mpl_toolkits/mplot3d/art3d.py   → Poly3DCollection, including get_facecolors / get_facecolor
```
Unknown:
- Location of the mplot3d test module(s)
- Location of `Axes3D.plot_surface` (presumably `mpl_toolkits/mplot3d/axes3d.py`, unconfirmed)
- Changelog / API-change note location, if a behavior note is required

## Code Style

Follow the existing conventions of `art3d.py` and the project's style rules. No snippet is available. The only visible pattern is the alias style `get_facecolor = get_facecolors` from the traceback, which should be preserved or kept equivalent.

## Testing Strategy

- **Framework:** unknown; presumably the project's existing test suite for mplot3d.
- **Regression tests (unit level):**
  - Create a surface with `plot_surface(..., cmap='hot')` and call `get_facecolors()` and `get_facecolor()` **without drawing**. They must not raise. The result must be an `(N, 4)` float array, where N is the number of polygons (or 1 if a single broadcast color is the established `Collection` convention).
  - The same check for `get_edgecolors()` / `get_edgecolor()`.
  - A directly constructed `Poly3DCollection(verts)` added to a 3D axes, with getters called before draw.
  - A `Poly3DCollection` **not** added to any axes, with getters called. Expected behavior is to be decided; see Open Questions.
  - After `fig.canvas.draw()`, the getters still return the projected/depth-sorted colors as they do today. The post-draw behavior must not regress.
- **Coverage expectation:** unknown. At minimum, the new tests fail on the current code and pass after the fix.
- Existing image-comparison tests for mplot3d must keep passing unchanged.

## Boundaries

- **Always:** Add a regression test that reproduces the issue. Run the full mplot3d test subset before submitting. Preserve post-draw getter output.
- **Ask first:** Changing what the getters return after draw. Changing depth-sorting or projection logic. Altering image-comparison baselines. Adding public API or deprecations.
- **Never:** Hide the error by catching `AttributeError` and returning an empty or meaningless array without an agreed contract. Trigger a full figure draw as a side effect of calling a getter (unless explicitly agreed). Modify unrelated collection classes.

## Success Criteria

1. Running the issue's reproducer on the target branch completes without exception. `r.get_facecolors()` returns an RGBA array of shape `(N, 4)` (or the agreed shape).
2. `get_facecolor`, `get_facecolors`, `get_edgecolor` and `get_edgecolors` on a `Poly3DCollection` never raise `AttributeError`, whether called before or after draw.
3. With a colormap (`cmap='hot'`), the pre-draw face colors reflect the agreed contract: either colormapped values or the base face color.
4. After `fig.canvas.draw()`, the getter results are identical to the current behavior.
5. All existing mplot3d tests, including image comparisons, pass.
6. The new regression tests fail on the unfixed code.

## Open Questions

1. **What should the getters return before the first draw?**
   - (a) the 3D face colors in original polygon order, without depth sorting;
   - (b) colors after applying the colormap/norm, which may require updating the scalar mapping eagerly;
   - (c) something else.

   Note that after draw the colors are depth-sorted, so the order would differ before and after draw. Is that acceptable, and should it be documented?
2. Should calling a getter trigger the colormap update (scalar mappable) so that `cmap` colors are returned pre-draw? Or is the base facecolor acceptable?
3. What is the expected behavior for a `Poly3DCollection` that has never been added to an `Axes3D` (no projection possible)?
4. Do other 3D collections (e.g. `Path3DCollection`, `Patch3DCollection`) have the same draw-time-only attribute pattern? Is fixing them in scope, or should they be a separate issue?
5. Does the reproducer still fail on the current development branch, or has the API changed since 1.4.2?
6. Is a changelog / API-behavior note required for this change?
7. What are the exact test, build and lint commands, and where are the test file locations? (Currently unknown.)