# Spec: AxesGrid support for axes classes without a subscriptable `axis` attribute

## Objective

**Problem.** Building an `mpl_toolkits.axes_grid1.AxesGrid` with an `axes_class` other than the toolkit's default raises an error during construction:

```
TypeError: 'method' object is not subscriptable
```

The reporter's example uses cartopy's `GeoAxes` as `axes_class`. Here is the failing path from the traceback:

1. `AxesGrid.__init__` calls `self.set_label_mode(label_mode)`.
2. `set_label_mode` calls `_tick_only(ax, bottom_on=False, left_on=False)`.
3. `_tick_only` runs `ax.axis["bottom"].toggle(...)`, which fails.

**Root cause, as reported.** The default `mpl_toolkits.axes_grid1.mpl_axes.Axes` exposes `axis` as a subscriptable mapping of axis artists. Other axes classes, such as `GeoAxes`, expose `axis` only as the standard callable `Axes.axis()` method. `_tick_only` assumes the mapping form.

**Users.**
- Matplotlib users who build `AxesGrid` (and possibly `ImageGrid` or `Grid`) with a custom `axes_class`.
- Downstream libraries that pass their own axes subclasses into axes_grid1, such as cartopy.

**What success looks like.**
- Constructing a grid with an `axes_class` whose `axis` attribute is a method no longer raises.
- Tick-label and axis-label visibility follows the requested `label_mode` as closely as the axes class allows.
- Behavior for the default axes class is unchanged.

**Acceptance criteria (user-level).**
- The reproduction snippet from the issue runs without error.
- A grid built with plain `matplotlib.axes.Axes` as `axes_class` can be constructed for every supported `label_mode`.
- Existing behavior and output for the default `mpl_axes.Axes` is unchanged.

## Assumptions

1. The defect is in Matplotlib's `mpl_toolkits.axes_grid1`, not in cartopy. Cartopy is only the trigger.
2. The bug also reproduces with plain `matplotlib.axes.Axes` as `axes_class`, because its `axis` is also a method. This lets us reproduce and test without cartopy. *This needs confirmation.*
3. The reported version is 3.1.2. The bug is assumed to still be present on the development branch; this is unverified.
4. Passing `axes_class` as a `(class, kwargs)` tuple is supported, documented usage.
5. The fix must not change the public API of `AxesGrid`, `ImageGrid` or `Grid`, and must not change behavior for the default axes class.
6. For axes without the axis-artist mapping, the standard Matplotlib tick and label APIs are an acceptable way to show or hide tick labels and axis labels. Examples are `tick_params` and label visibility.
7. `_tick_only` is a private helper, so its signature and internals may change.

## Tech Stack

- **Language:** Python. The report uses 3.7.6; supported versions for the fix are unknown.
- **Library:** Matplotlib (`mpl_toolkits.axes_grid1`).
- **Trigger dependency (not required for the fix):** cartopy 0.17.0 (`GeoAxes`, `PlateCarree`).
- **Other versions and constraints:** unknown.

## Commands

All unknown, because the issue does not show them:

- Build: unknown
- Test: unknown (the environment lists pytest 5.3.4, but the project's test invocation is not shown)
- Lint: unknown (flake8 is installed in the reporter's environment; project config is unknown)
- Dev: N/A

## Project Structure

Only the following are known from the issue and traceback:

```
mpl_toolkits/axes_grid1/axes_grid.py  → AxesGrid / Grid, set_label_mode, _tick_only (failure site)
mpl_toolkits/axes_grid1/mpl_axes.py   → default Axes class with subscriptable `axis`
```

Unknown:
- the test directory location for axes_grid1
- whether baseline images are used
- the location of the changelog or API notes

## Code Style

- Conventions are unknown; the repository is not visible.
- Follow the existing style of `axes_grid.py`.
- Reproduction from the issue, which serves as the canonical failing example:

```python
import matplotlib.pyplot as plt
from cartopy.crs import PlateCarree
from cartopy.mpl.geoaxes import GeoAxes
from mpl_toolkits.axes_grid1 import AxesGrid

fig = plt.figure()
axes_class = (GeoAxes, dict(map_projection=PlateCarree()))
gr = AxesGrid(fig, 111, nrows_ncols=(1,1),
              axes_class=axes_class)
```

## Testing Strategy

- **Framework:** presumed pytest; the project's exact setup is unknown.
- **Regression test.** Construct `AxesGrid` with `axes_class=matplotlib.axes.Axes`, or a `(class, kwargs)` tuple form, so no cartopy dependency is needed. Assert that construction succeeds.
- **Label-mode coverage.** Parametrize over every supported `label_mode`. Assert, as far as the agreed behavior defines it, which axes show tick labels and axis labels.
- **Non-regression.** Existing axes_grid1 tests, including any image comparison tests, must pass unchanged for the default axes class.
- **Optional.** A cartopy-based check, only if cartopy is an available optional test dependency. Whether it is available is unknown.
- **Coverage expectations:** unknown.

## Boundaries

**Always:**
- Keep default-axes-class behavior identical.
- Add a regression test that fails before the fix and passes after it.
- Keep public signatures stable.

**Ask first:**
- Adding cartopy (or any new dependency) to the test requirements.
- Changing the public API of `AxesGrid`, `ImageGrid` or `Grid`.
- Changing documented `label_mode` semantics.
- Emitting new warnings.

**Never:**
- Fix this by changing cartopy.
- Silently swallow arbitrary exceptions in `_tick_only`, for example with a broad `try/except`.
- Remove or loosen existing tests.

## Success Criteria

1. **No error with cartopy.** `AxesGrid(fig, 111, nrows_ncols=(1, 1), axes_class=(GeoAxes, dict(map_projection=PlateCarree())))` completes without exception.
2. **No error with plain Matplotlib axes.** `AxesGrid(..., axes_class=matplotlib.axes.Axes)` completes without exception for every supported `label_mode`.
3. **Label visibility honored.** For non-default axes classes, tick-label and axis-label visibility matches the `label_mode` contract. The exact mapping is pending Open Question 1.
4. **Default class unchanged.** For the default `mpl_axes.Axes`, the rendered output and the `axis[...]` toggle state are unchanged.
5. **Regression test added.** A test covering criterion 2 is added and passes.
6. **Other call sites covered.** Any other code path in axes_grid1 that indexes `ax.axis[...]` during grid construction is also safe with non-default axes classes, or is listed as out of scope.

## Open Questions

1. **Expected `label_mode` behavior.** The issue's "Expected outcome" section is empty. For axes without the axis-artist mapping, should tick and axis labels be hidden through the standard tick APIs, so that `label_mode` is honored? Or should label handling simply be skipped?
2. **Partial capability.** Should the axes class be detected by capability (does `ax.axis` support indexing?) or by type (is it an `mpl_axes.Axes` instance)? Which one handles subclasses and duck-typed axes correctly?
3. **Other call sites.** Are there other places in axes_grid1 that index `ax.axis[...]` and would fail the same way? Possible examples are colorbar axes in `ImageGrid`, `cbar_mode`, `Grid` versus `AxesGrid`, and `mpl_axes.Axes.toggle_axisline`. Are they in scope?
4. **Cartopy specifics.** Do `GeoAxes` honor standard tick-label visibility APIs in a meaningful way? Cartopy may draw gridline labels separately. Is "no error" sufficient for GeoAxes, or is visible-label correctness also required?
5. **Target branch.** Which branch or version should receive the fix, and is a backport to a 3.x maintenance branch expected?
6. **Changelog.** Is a changelog or API-change note required for this fix?
7. **Commands and test layout.** What are the project's test, lint and build commands, and where do the axes_grid1 tests live?