# Spec: Eliminate NumPy 1.24 DeprecationWarnings in `Colormap.__call__` for small integer dtypes

## Objective

Calling a Matplotlib colormap with an integer array whose dtype cannot represent the colormap's special lookup indices (over, under, bad) triggers NumPy 1.24+ `DeprecationWarning`s:

```
NumPy will stop allowing conversion of out-of-bound Python integers to integer arrays.
The conversion of 257 to uint8 will fail in the future.
```

The warnings come from `matplotlib/colors.py` lines 730–732 (Matplotlib 3.6.2):

```python
xa[xa > self.N - 1] = self._i_over
xa[xa < 0] = self._i_under
xa[mask_bad] = self._i_bad
```

For the default colormap (`N = 256`), the special indices are 256, 257 and 258. None of them fits in `uint8`. NumPy currently wraps these values silently. Future NumPy versions will raise an error instead of warning, so the code path will break rather than just get noisy.

**Who is affected:** Anyone who passes integer arrays to a `Colormap`, directly or indirectly. The issue's example uses `uint8`, which is common for image data.

**What success looks like:**
- No `DeprecationWarning` is emitted under NumPy ≥ 1.24.
- The code keeps working on NumPy versions where out-of-bound integer assignment raises.
- RGBA results stay correct, including correct handling of over, under and bad values.

**User story:** As a user mapping `uint8` (or other narrow integer) data through a colormap, I get correct colors with no warnings on current and future NumPy releases.

## Assumptions

1. The failure is caused by assigning Python ints (`_i_over`, `_i_under`, `_i_bad`, i.e. `N+1`, `N`, `N+2` going by the warning values) into `xa` while `xa` keeps the caller's narrow integer dtype. This is inferred from the traceback values and line numbers. I have not read the full source.
2. The fix belongs in `Colormap.__call__` in `lib/matplotlib/colors.py`. The `lib/` prefix follows the usual Matplotlib layout and is not verified.
3. Intended semantics for integer input are unchanged:
   - Values in `[0, N-1]` index the LUT directly.
   - Values above `N-1` map to "over".
   - Negative values map to "under".
   - Masked values map to "bad".
4. Only the dtype handling of `xa` is in scope. The public API and output shape/dtype (RGBA floats or `uint8` when `bytes=True`) must not change.
5. Other NumPy 1.24 deprecation warnings elsewhere in Matplotlib are out of scope unless they share this root cause. The issue says "several", but all three shown come from these lines.
6. The behavior should hold across the NumPy versions Matplotlib supports. That range is unknown to me.

## Tech Stack

- Python (issue reports 3.10.9)
- NumPy ≥ 1.24 (triggers the warnings). The minimum supported version is unknown.
- Matplotlib 3.6.2 (reported version). The target branch is unknown.

## Commands

All commands are unknown because the repository was not accessible. Placeholders:

```
Build:   UNKNOWN
Test:    UNKNOWN (likely pytest-based; exact invocation/flags unverified)
Lint:    UNKNOWN
Dev:     N/A
```

Minimal repro from the issue. It should run with warnings promoted to errors once fixed:

```
python -W error::DeprecationWarning -c "import matplotlib.pyplot as plt, numpy as np; plt.get_cmap()(np.empty((0,), dtype=np.uint8))"
```

## Project Structure

Only what the issue shows:

```
matplotlib/colors.py   → Colormap implementation (lines ~730–732 in 3.6.2)
```

The test location is unknown. Presumably there is a test module for `colors`, but its path is unverified.

## Code Style

Unknown. Follow the existing conventions in `colors.py`. No snippet is available beyond the three lines quoted above.

## Testing Strategy

The framework is unknown, presumably pytest. Required test coverage:

- **Regression test: empty input.** Call a colormap on an empty `uint8` array. Assert that no `DeprecationWarning` (or any warning) is raised. Ideally run it with warnings-as-errors.
- **Regression test: populated input.** Call a colormap with `N = 256` on a populated `uint8` array containing values 0, 128 and 255. Assert:
  - no warnings;
  - results equal the LUT entries for those indices.
- **Special indices with narrow dtypes.** Use integer dtypes where special indices overflow, such as `uint8` and `int8`, and include:
  - out-of-range values (where representable, e.g. negative for `int8`);
  - masked values.

  Assert that they map to the over, under and bad colors respectively.
- **Non-default `N`.** Use a colormap with `N` such that `N+2` exceeds the dtype maximum (e.g. `N = 256` for `uint8`). Optionally include a small `N`, where no overflow occurs, to confirm unchanged behavior.
- **`bytes=True` path.** Confirm the output dtype and values are unchanged.
- **Float input.** Confirm there is no behavior change.
- Tests should pass on the oldest supported NumPy and on NumPy ≥ 1.24. CI matrix details are unknown.

## Boundaries

- **Always:**
  - Preserve existing color-mapping semantics and output dtypes.
  - Add regression tests reproducing the issue.
  - Run the colors test suite before committing.
- **Ask first:**
  - Changing the public `Colormap.__call__` signature or return types.
  - Bumping the minimum NumPy version.
  - Broadening scope to other NumPy 1.24 warnings elsewhere in the codebase.
- **Never:**
  - Suppress or filter the `DeprecationWarning` instead of fixing the cause.
  - Rely on silent integer overflow/wraparound.
  - Remove or weaken existing colormap tests.

## Success Criteria

1. The issue's reproduction emits no warnings under NumPy ≥ 1.24, including when run with `-W error::DeprecationWarning`.
2. No warnings or errors occur for non-empty `uint8`/`int8` inputs, with or without masks, for colormaps where `N+2` exceeds the dtype's maximum.
3. For integer input, in-range values map to `lut[value]`, values `> N-1` map to the over color, values `< 0` map to the under color, and masked values map to the bad color. Results are identical to the pre-change intended behavior.
4. Float input behavior and `bytes=True` output are unchanged, as confirmed by existing tests passing.
5. New regression tests are added and pass on all NumPy versions in the project's CI matrix.

## Open Questions

1. Which Matplotlib branch should receive the fix: `main` only, or also a 3.6.x bugfix release?
2. What is the minimum NumPy version Matplotlib supports on the target branch? Any dtype-handling approach must work on all of them.
3. Are there other NumPy 1.24 deprecation warnings in the codebase the reporter considers part of "several"? Should they go in this change or be tracked separately?
4. What are the exact test commands, test file location, and lint tooling for the repository?
5. Is there a performance constraint on `Colormap.__call__` for large integer image arrays? For example, is widening the integer dtype of a copy acceptable memory-wise?
6. Should signed narrow dtypes (`int8`, `int16`) and unsigned dtypes be treated identically for under/over detection? This is currently assumed yes.