# Spec: Colorbar Refreshes Correctly After `mappable.norm` Is Replaced

## Objective

**Problem.** If a user replaces the norm of a mappable that already has a colorbar (for example, `plot.norm = LogNorm()` on an `imshow` image), there is no working way to make the colorbar reflect the new norm:

- `cb.update_normal(plot)` returns without error, but the colorbar does not change. It keeps its old linear scaling, ticks and color mapping.
- `cb.update_bruteforce(plot)` raises `ZeroDivisionError`. Per the traceback, the error is raised in `LogNorm.inverse` (`vmin * ma.power((vmax / vmin), val)`), called from `Colorbar._process_values` through `Colorbar.draw_all`.

**User.** A Matplotlib user who changes the normalization of an existing plot interactively or in a script, such as switching linear to log, and expects the attached colorbar to follow.

**Goal.** After the user replaces `mappable.norm` with a new norm instance and calls the public colorbar update method, the colorbar must:

1. Use the new norm for its color mapping, scaling, ticks and tick formatter. For a `LogNorm`, this means a log-scaled colorbar with log-appropriate ticks.
2. Do this without raising, even when the new norm has not been scaled yet (`vmin`/`vmax` unset). In that case the limits should come from the mappable's data, the same way the image itself would be autoscaled.
3. Still work for the common case where only the existing norm's limits or the cmap changed and the norm was not replaced.

**Acceptance criteria (user-facing):**

- Running the issue's example with only `cb.update_normal(plot)` (no `update_bruteforce`) produces a colorbar whose norm is the new `LogNorm`. Its limits match the image's data range and its axis is log-scaled.
- Running the issue's example with `cb.update_bruteforce(plot)` does not raise `ZeroDivisionError`. Whether this method should be kept, deprecated or aliased is an open question.
- The image and the colorbar agree on `vmin`/`vmax` after the update.

## Assumptions

1. The issue applies to the `Colorbar` class in `matplotlib/colorbar.py` and to `LogNorm` in `matplotlib/colors.py`. These are the files named in the traceback. Other files involved are unknown.
2. The reporter's environment was Python 3.4 with an Anaconda-installed Matplotlib. The exact Matplotlib version is **unknown**. The fix targets the current development branch, not that release.
3. The exception happens because the freshly constructed `LogNorm()` has no `vmin`/`vmax` when the colorbar processes it, and some fallback ends up with `vmin == 0`. This is a **hypothesis** based on the traceback and has not been verified against the source.
4. `update_normal` is the intended public entry point for "the mappable changed, refresh the colorbar". The fix should make it handle norm replacement rather than adding a new API.
5. Replacing the norm on the mappable, as opposed to mutating it, is a supported user action. The mappable's own norm is the source of truth, and the colorbar should follow it.
6. Behavior for colorbars created without a mappable (`ColorbarBase` with an explicit norm) must not regress.
7. Changing the norm type (for example, linear to log) may require resetting the colorbar's locator, formatter and axis scale. Any of these that the user set explicitly is out of scope unless the Open Questions resolve it otherwise.

## Tech Stack

- Python and NumPy (`numpy.ma` is used in `LogNorm.inverse`). Supported versions are **unknown** for the target branch.
- Matplotlib. Relevant modules from the traceback: `matplotlib.colorbar` and `matplotlib.colors`. Relevant objects: `Colorbar`, `update_normal`, `update_bruteforce`, `draw_all`, `_process_values`, `_uniform_y`, `LogNorm.inverse`.

## Commands

The issue does not state these. All are **unknown**:

- Build: unknown
- Test: unknown (likely a pytest-based suite, not confirmed)
- Lint: unknown
- Docs build: unknown

## Project Structure

The only paths visible from the issue are:

```
matplotlib/colorbar.py   → Colorbar, update_normal, update_bruteforce, draw_all, _process_values
matplotlib/colors.py     → LogNorm (inverse)
```

The location of tests, image-comparison baselines and docs or changelog entries is **unknown**.

## Code Style

The project's conventions are not visible in the issue and are **unknown**. Follow the existing style of `matplotlib/colorbar.py` and `matplotlib/colors.py`. The user-facing usage the fix must support, taken from the issue:

```python
plot = ax.imshow(img, cmap='gray')
cb = fig.colorbar(plot, ax=ax)
plot.norm = LogNorm()
cb.update_normal(plot)   # must now switch the colorbar to the LogNorm
```

## Testing Strategy

The framework and locations are **unknown**. The levels needed are:

- **Regression unit test (issue reproducer):** create an image and a colorbar, replace the norm with an unscaled `LogNorm()`, call `update_normal`, and assert all of the following:
  - The colorbar's norm is the new norm, or is equivalent to it.
  - `vmin`/`vmax` match the image data range.
  - No exception is raised, including during a subsequent `fig.canvas.draw()`.
- **Regression for `update_bruteforce`:** the same scenario must not raise `ZeroDivisionError`. This depends on the decision about that method's future.
- **Pre-scaled norm:** replacing the norm with `LogNorm(vmin=..., vmax=...)` must keep the user's explicit limits.
- **Non-replacement path:** changing `plot.set_clim(...)` or `plot.set_cmap(...)` followed by `update_normal` still updates the colorbar, with no regression.
- **Reverse direction:** switching from log back to linear (`Normalize()`) works.
- **Visual check (optional):** an image-comparison test of the log colorbar after the switch, if the project uses baseline images. Whether it does is unknown.

Coverage expectations are **unknown**.

## Boundaries

- **Always:**
  - Reproduce the issue's example as a failing test before changing behavior.
  - Keep the public method signatures `update_normal(mappable)` and `update_bruteforce(mappable)` intact.
  - Run the existing colorbar and colors tests.
- **Ask first:**
  - Deprecating or removing `update_bruteforce`.
  - Changing `LogNorm.inverse` semantics for unscaled or zero `vmin`. That is a `colors` module change with wider impact.
  - Overriding locators or formatters the user set explicitly when the norm type changes.
  - Adding new public API.
- **Never:**
  - Silently swallow the `ZeroDivisionError` without making the colorbar correct.
  - Mutate the user's norm limits when they were explicitly set.
  - Change unrelated colorbar layout or extension behavior.

## Success Criteria

1. The issue's script, using `update_normal` alone, renders a log-scaled colorbar matching the log-normalized image, with no exception.
2. The issue's script, using `update_bruteforce`, does not raise `ZeroDivisionError`. It either works or follows the agreed deprecation path.
3. An unscaled replacement norm is autoscaled from the mappable's data before the colorbar uses it, so the image and colorbar `vmin`/`vmax` are identical.
4. An explicitly scaled replacement norm keeps its limits.
5. `set_clim` and `set_cmap` followed by `update_normal` behave as before.
6. All existing colorbar and colors tests pass, and the new regression tests pass.

## Open Questions

1. Which Matplotlib version and branch should the fix target, and has the current code changed since the reporter's version, given that the line numbers in the traceback may be stale?
2. Should `update_normal` fully reset the colorbar (scale, locator, formatter) when the norm *type* changes, or only when the norm *instance* changes?
3. What should happen to a user-customized locator or formatter on the colorbar when the norm is replaced? Keep it, or reset it to the new norm's default?
4. What is the future of `update_bruteforce`? Fix it, deprecate it in favor of `update_normal`, or make it an alias?
5. Should an unscaled norm be autoscaled by the colorbar from the mappable's array, or should the mappable be responsible for autoscaling when `.norm` is assigned (for example, through a norm property setter)?
6. Should `LogNorm.inverse` itself guard against `vmin <= 0` or unset limits with a clear error, separately from the colorbar fix?
7. Should assigning `plot.norm = ...` automatically notify and update attached colorbars, with no manual `update_normal` call? That would be a scope expansion.
8. Are a changelog entry or doc update for `update_normal` required, and where do they go? The location is unknown.