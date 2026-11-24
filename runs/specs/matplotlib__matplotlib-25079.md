# Spec: Assigning a new norm to a mappable with an existing colorbar (3.6.3 regression)

## Objective

**Problem.** In matplotlib 3.6.3, this sequence fails on the next draw with `ValueError: Invalid vmin or vmax`:

1. Create a `ScalarMappable`, such as a `QuadMesh` from `pcolormesh`.
2. Attach a colorbar to it.
3. Assign a `LogNorm(vmin, vmax)` to the mappable's `.norm`.
4. Call `.autoscale()`.

The same code works in 3.6.2. The data is strictly positive (1 to 5). The explicit `vmin=1` and `vmax=5` are valid for `LogNorm`.

**Users affected.** Anyone who changes a mappable's normalization after creating a colorbar. Interactive and GUI code does this routinely. The failure happens on every tested backend (Qt5Agg, TkAgg, agg), so it is not backend-specific.

**What success looks like.**
- Setting `mappable.norm = LogNorm(vmin, vmax)` on a mappable that already has a colorbar no longer raises an error.
- Calling `mappable.autoscale()` afterwards also no longer raises an error.
- The next draw succeeds.
- Both the mappable and the colorbar render with the new log normalization.
- 3.6.2 behaviour is restored for this scenario.

**Where the error is raised (from the traceback):**
`Figure.draw` → `Axes.draw` → `Collection.draw` (collections.py) → `update_scalarmappable` → `ScalarMappable.to_rgba` (cm.py) → `LogNorm.__call__` (colors.py) → `ValueError("Invalid vmin or vmax")`.

At draw time, the norm's `vmin`/`vmax` hold values that the log transform rejects, even though the user set valid limits.

**User stories / acceptance criteria**
- As a user, I can replace a mappable's norm with a `LogNorm` after a colorbar exists, and the figure redraws without error.
- As a user, I can call `mappable.autoscale()` after replacing the norm, and the resulting limits are valid for the norm. Here they are the data min/max, 1 to 5, which are positive.
- As a user, the colorbar reflects the new norm: log scale, correct limits.

## Assumptions

1. The regression came from a change between 3.6.2 and 3.6.3. It concerns how norm replacement and/or autoscaling interact with the colorbar's callback-driven update. Callbacks fire when the norm changes. During `autoscale()`, `vmin` and `vmax` are set one at a time. A callback may fire between the two assignments and observe or propagate an intermediate state with invalid limits. **This is a hypothesis, not verified.**
2. The bug reproduces non-interactively too, on the agg backend, using `fig.canvas.draw()` instead of `plt.ion()` / `plt.pause()`. The report says agg fails as well.
3. The fix belongs in library code (norm, mappable or colorbar update path), not in user code.
4. The `.norm` setter on mappables with colorbars is public API. Its behaviour must stay backward compatible with 3.6.2.
5. Other norms that restrict valid limits (e.g. `SymLogNorm`, `PowerNorm`, other scale-based norms) may be affected by the same mechanism. Only `LogNorm` is confirmed.
6. The fix must not change the result of a valid user call to `autoscale()` / `autoscale_None()`. It may only change when or how often change notifications are emitted.

## Tech Stack

- Python (reporter used 3.9.15; the supported version range of the target branch is unknown)
- NumPy
- matplotlib, with the 3.6.x maintenance line affected
- Modules named in the traceback: `matplotlib/colors.py`, `matplotlib/cm.py`, `matplotlib/collections.py`, `matplotlib/figure.py`, `matplotlib/axes/_base.py`, `matplotlib/image.py`
- The colorbar module is presumably involved but is not shown in the traceback (unverified)

## Commands

The repository is not visible, so these are **unknown**:
- Build / install for development: unknown
- Test: unknown (likely pytest-based, unconfirmed)
- Lint: unknown
- Reproduce: run the script from the issue. A non-interactive variant that calls `fig.canvas.draw()` is proposed in Testing Strategy.

## Project Structure

Only these paths are known, from the traceback in the installed package:
```
matplotlib/colors.py       → Norm classes (LogNorm.__call__ raises the error)
matplotlib/cm.py           → ScalarMappable (to_rgba, norm handling)
matplotlib/collections.py  → Collection.draw / update_scalarmappable
matplotlib/figure.py       → Figure.draw
matplotlib/axes/_base.py   → Axes.draw
matplotlib/image.py        → _draw_list_compositing_images
```
- Colorbar implementation location: unknown, not in the traceback
- Test directory layout: unknown

## Code Style

Unknown. Follow the existing conventions of the surrounding matplotlib code. No snippet is available from the issue.

## Testing Strategy

- **Regression test (required).** Do the following without GUI or `plt.pause`:
  1. Create a figure with a `pcolormesh` of strictly positive data and a colorbar.
  2. Draw once.
  3. Set `mappable.norm = LogNorm(1, 5)`.
  4. Call `mappable.autoscale()`.
  5. Draw again.

  Assert that no exception is raised. Assert that the norm's limits are valid: `vmin > 0` and `vmin < vmax`, matching the data range after autoscale.
- **Colorbar check.** After the redraw, the colorbar uses the new norm, and its limits match the mappable's norm.
- **Variant without `autoscale()`.** Setting the norm alone, then drawing, also succeeds with the explicit limits preserved.
- **Non-regression.** Existing norm, colormap and colorbar tests still pass. In particular:
  - Tests asserting that changing `vmin`/`vmax` notifies listeners (callbacks) still pass.
  - Tests asserting that the colorbar updates when the norm changes still pass.
- **Test framework and location:** unknown (see Open Questions).

## Boundaries

- **Always:**
  - Add a regression test that fails on the current code and passes after the fix.
  - Keep the public behaviour of `.norm` assignment and `autoscale()` consistent with 3.6.2.
  - Run the existing colors/colorbar/cm test suites.
- **Ask first:**
  - Changing when or how many times norm "changed" callbacks are emitted, since this is observable by user callbacks.
  - Changing the public API or signatures of `Normalize`, `ScalarMappable` or the colorbar.
  - Reverting the 3.6.3 change wholesale instead of fixing it narrowly.
  - Backporting decisions.
- **Never:**
  - Silence or catch the `ValueError` in `LogNorm.__call__` to hide the symptom.
  - Weaken validation of genuinely invalid limits (e.g. `vmin <= 0` for `LogNorm`).
  - Remove or skip existing failing tests without approval.

## Success Criteria

1. The reproduction script from the issue runs without exception on agg and on an interactive backend.
2. A non-interactive regression test passes:
   - It covers `pcolormesh` + colorbar + draw + `norm = LogNorm(1, 5)` + `autoscale()` + draw.
   - After autoscale, `norm.vmin == data.min()` and `norm.vmax == data.max()`, both positive.
3. After the redraw, the colorbar's norm is the new `LogNorm`, and its limits match the mappable's limits.
4. Truly invalid limits still raise `ValueError` when calling the norm, e.g. `LogNorm(vmin=-1, vmax=5)` with a draw.
5. Norm-change callbacks still notify listeners after the limits change. No existing callback or colorbar tests regress.
6. The root-cause change between 3.6.2 and 3.6.3 is identified and referenced in the fix/PR description.

## Open Questions

1. Which commit or PR between 3.6.2 and 3.6.3 introduced the regression? Is it in norm autoscaling, the `.norm` setter, or the colorbar's update-on-norm-change logic?
2. Is the invalid state caused by an intermediate (`vmin`, `vmax`) pair that callbacks observe while `autoscale()` assigns limits one at a time? Or does the colorbar reset or mutate the new norm's limits when it receives the norm-change notification?
3. Does the failure require `plot.autoscale()`, or does assigning the norm alone already fail? (The issue only shows both together.)
4. Is `LogNorm` the only affected norm? Should the regression tests also cover `SymLogNorm`, `PowerNorm` or other scale-derived norms?
5. When autoscaling, should norm-change callbacks fire once (after both limits are set) or once per limit? Do any users or tests depend on the per-limit behaviour?
6. Which branch is the target (3.6.x bugfix and/or main), and is a backport expected?
7. What are the repository's test command, test file locations and test conventions? Image comparison or plain assertions for the colorbar check?
8. Does the `layout="constrained"` option in the reproduction matter, or does the default layout reproduce the bug too?