# Spec: Figure DPI must survive pickle round-trips on HiDPI (M1/Retina) macOS

## Objective

**Problem.** On an M1 Mac using the `MacOSX` backend, each pickle → unpickle round-trip of a Matplotlib `Figure` doubles its `dpi`. Repeating the round-trip grows the DPI exponentially: 200 → 400 → … → 419430400. Eventually unpickling fails with:

```
OverflowError: signed integer is greater than maximum
```

The error is raised from `_macosx.FigureCanvas.__init__(self, width, height)` in `matplotlib/backends/backend_macosx.py`. That call is reached via `Figure.__setstate__` (`matplotlib/figure.py`) → `new_figure_manager_given_figure` (`matplotlib/backend_bases.py`).

**Who is affected.** Users who pickle figures, for example to cache them, send them between processes, or save and restore sessions. The reported setup is:

- macOS 12.4 on arm64
- `MacOSX` backend
- Matplotlib 3.5.2
- Python 3.9.12, installed via pip

The reporter says the Python version does not matter.

**Desired behavior.** Unpickling a figure gives back a figure with the same `dpi` as the original. The value stays stable however many round-trips are done. The display-scaling factor (device pixel ratio) must not compound across round-trips.

**Acceptance criteria (user-visible).**

- AC1: After one pickle round-trip, `fig2.dpi == fig.dpi`.
- AC2: After N consecutive round-trips (the reproduction uses 32), `dpi` equals the value before the first round-trip, and no `OverflowError` is raised.
- AC3: The figure's size in inches (`get_size_inches()`) is also unchanged after round-trips. *(Assumed; see Assumptions.)*
- AC4: The behavior on non-HiDPI displays and other backends does not regress.

## Assumptions

1. **Suspected cause (not verified).** The root cause is likely HiDPI/Retina scaling, not "M1" as such. The canvas likely multiplies the figure's DPI by a device pixel ratio of 2. The pickled state then likely stores this already-scaled DPI. On unpickle, the new canvas would apply the ratio again, so the scaling compounds.
   - Supporting evidence: the first printed value is 200.0, which is twice the usual default of 100.
   - This hypothesis must be confirmed during implementation.
2. **Other affected setups.** The bug probably also affects Intel Macs with Retina displays, and possibly other backends that support device-pixel-ratio scaling. Only the `MacOSX` backend on M1 has been reported.
3. **What "dpi is preserved" means.** It means `fig.dpi` reads the same value before and after unpickling within the same display environment.
4. **Figure size.** Size in inches should be preserved as well as DPI.
5. **Scope of the fix.** The fix belongs in Matplotlib's figure pickling and/or canvas DPI-scaling logic. No change is needed in user code.
6. **Version under test.** The target is the current development branch. The report was against 3.5.2, and whether the bug still exists on main is unknown.

## Tech Stack

- Python, Matplotlib, and the `MacOSX` backend (a native `_macosx` extension module), as named in the traceback.
- Other versions, dependency pins and the build toolchain: **unknown**. They are not visible in the issue.

## Commands

- Build: **unknown**
- Test: **unknown** (likely pytest, but the exact invocation is not visible)
- Lint: **unknown**
- Reproduce: run the script from the issue with the `MacOSX` backend on a HiDPI Mac.

## Project Structure

Only the files that appear in the traceback are known:

```
matplotlib/figure.py                 → Figure.__setstate__ (unpickling path)
matplotlib/backend_bases.py          → new_figure_manager_given_figure
matplotlib/backends/backend_macosx.py → FigureCanvas.__init__ (where the overflow is raised)
```

Unknown:

- Test directory locations.
- The location of the native `_macosx` source.
- Where device-pixel-ratio handling lives.

## Code Style

**Unknown.** Follow the conventions already used in the files listed above. No snippet is available from the issue.

## Testing Strategy

- **Regression test (unit level).**
  - Create a figure and simulate a device pixel ratio greater than 1, if a backend-independent mechanism for that exists (unknown).
  - Pickle and unpickle it, then assert that `dpi` and the size in inches are unchanged.
  - Repeat the round-trip several times and assert the values stay stable.
- **Pickle tests for normal displays.** Existing pickle tests must still pass.
- **Manual verification.**
  - Run the issue's reproduction script on a HiDPI Mac with the `MacOSX` backend.
  - The DPI must stay constant over 32 iterations, and no `OverflowError` may occur.
- **CI limits.** Whether CI can exercise the `MacOSX` backend on HiDPI hardware is **unknown**. A backend-agnostic test that simulates the device pixel ratio is preferred.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix.
  - Keep the existing pickle format compatible where feasible.
  - Run the existing test suite.
- **Ask first:**
  - Changing the public meaning of `Figure.dpi`, meaning whether it is "logical" or "physical" DPI.
  - Changing the pickled-state format in a way that affects older pickles.
  - Modifying the native `_macosx` extension.
- **Never:**
  - Mask the bug by clamping the DPI or catching `OverflowError`.
  - Special-case "M1" or `arm64` in the fix.
  - Remove or skip existing tests.

## Success Criteria

1. The issue's reproduction script prints the same DPI on every one of its 32 iterations and finishes without error on an M1/HiDPI Mac with the `MacOSX` backend.
2. A new automated test asserts that `dpi` and the size in inches are unchanged after a single round-trip and after multiple round-trips when a device pixel ratio greater than 1 is in effect.
3. All existing pickle and figure tests pass.
4. Behavior on displays with a device pixel ratio of 1, and on non-macOS backends, is unchanged.

## Open Questions

1. **Initial DPI value.** The "expected outcome" shows 200 throughout, but the default DPI is presumably 100. Should a fresh figure on a Retina display report `fig.dpi == 200` (physical) or `100` (logical)? This spec only requires that the value is stable across round-trips. Is it acceptable for the initial value to stay 200?
2. **Moving between displays.** If a figure is pickled on a HiDPI display and unpickled on a display with a ratio of 1 (or the other way round), what `dpi` should it have?
3. **Other backends.** Are other HiDPI-aware backends known to have the same compounding problem? If so, should they be included in this fix's scope?
4. **Old pickles.** Do pickles created by affected versions, which may contain an already-doubled DPI, need to load correctly? Or is only new pickling behavior in scope?
5. **Reproducibility on main.** Is the bug still reproducible on the current development branch, or only on 3.5.2?
6. **Test tooling.** What are the exact test command and test file locations? Is there an existing way to simulate a device pixel ratio in tests?