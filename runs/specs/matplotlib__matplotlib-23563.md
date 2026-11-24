# Spec: Failed `Axes3D.plot` call must not leave a broken `Line3D` that breaks later draws

## Objective

**Problem.** In matplotlib 3.5.0, calling `Axes3D.plot(xs, ys, zs, ...)` with a `zs` whose shape does not match `xs`/`ys` raises:

```
input operand has more dimensions than allowed by the axis remapping
```

After that, every later draw fails with:

```
AttributeError: 'Line3D' object has no attribute '_verts3d'
```

The traceback ends in `mpl_toolkits/mplot3d/art3d.py`, line 215, `Line3D.draw`, at `xs3d, ys3d, zs3d = self._verts3d`. This happens even when the next calls use valid scalar inputs and a new figure. Only restarting the Python/IPython process clears it.

**Working hypothesis (to be confirmed during investigation, not asserted as fact):**

1. The failing `plot` call creates a 2D line and attaches it to the axes.
2. It converts the line to `Line3D`.
3. It then raises while setting the 3D properties, before `_verts3d` is assigned.
4. The half-built artist stays attached to the axes. Its figure also stays registered with pyplot.
5. Each later `plt.show()` redraws all open figures, including the broken one, so the error repeats in every session until restart.

The numpy message matches a failed broadcast of a 2-D `zs` to the 1-D shape of `xs`.

**Who is affected.** Users of `mplot3d`, especially in interactive sessions (IPython, PyCharm, Jupyter) where figures persist between cell runs.

**What success looks like:**

- An invalid `zs` gives one clear, immediate error at the `plot` call.
- The axes and figure are left in a consistent state.
- Later valid plotting and `plt.show()` work without restarting the interpreter.

**User stories:**

- As a user, when I pass mismatched `zs` to `ax.plot`, I get an error that tells me the shapes are incompatible.
- As a user, after such an error, I can fix my inputs, plot again and show figures without an `AttributeError` from an unrelated, earlier artist.

## Assumptions

1. The root cause is in the `mplot3d` toolkit: either `Axes3D.plot` or the 2D→3D line conversion in `art3d` (the traceback points to `art3d.py` / `Line3D.draw`). The issue does not point to the PyCharm backend.
2. The reporter's "numpy array for `x_s_0[n]`" case is equivalent to passing a `zs` (or `xs`/`ys`) element that is an array rather than a scalar. This produces a ragged or 2-D `zs` that cannot be broadcast to the shape of `xs`.
3. The error persists because the broken figure is still registered with pyplot and gets redrawn by later `plt.show()` calls. It is not a global-state corruption inside matplotlib.
4. The first error ("input operand has more dimensions…") is correct behaviour for invalid input and should still be raised. Its wording may be improved. Only the leftover broken state is the bug.
5. The fix targets the current development branch, not just 3.5.0. Whether the bug still reproduces on `main` is unverified.
6. `fig.gca(projection='3d')` in the reporter's code is deprecated API but not relevant to the bug. `fig.add_subplot(projection='3d')` should reproduce it equally.

## Tech Stack

- Python (reporter: 3.8.12; supported versions for the target branch: unknown)
- matplotlib with the `mpl_toolkits.mplot3d` toolkit (reported on 3.5.0)
- NumPy (version unknown)

## Commands

Unknown. The repository is not visible. Expected categories:

- Build/install (editable): unknown
- Test (mplot3d subset): unknown
- Lint: unknown

## Project Structure

Only what the traceback shows:

- `lib/.../mpl_toolkits/mplot3d/axes3d.py` → `Axes3D`, including `plot` and `draw`
- `lib/.../mpl_toolkits/mplot3d/art3d.py` → 3D artists, including `Line3D` (`draw` reads `self._verts3d`)
- Test location for mplot3d: unknown (presumably a `tests/` directory inside `mpl_toolkits/mplot3d`; to be confirmed)

## Code Style

Unknown. Follow the existing conventions in `art3d.py` and `axes3d.py`. No code from the repository is visible here.

## Testing Strategy

- **Framework:** unknown (presumably pytest, as used by matplotlib; to be confirmed).
- **Regression test (unit level, mplot3d tests):**
  1. Create a 3D axes and record the number of lines it holds.
  2. Call `ax.plot` with mismatched `zs` and assert that it raises.
  3. Assert the axes holds no new line (or no line without valid 3D data).
  4. Call `fig.canvas.draw()` (Agg) and assert that it succeeds.
  5. Plot valid data on the same axes and draw again successfully.
- **Candidate minimal reproducer (unverified, derived from the error message):**

  ```python
  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')
  ax.plot([0, 1], [0, 1], [[0, 1], [0, 1]])  # expected to raise
  fig.canvas.draw()                           # currently expected to raise AttributeError on _verts3d
  ```

- **Related paths to check:**
  - other ways of building a `Line3D` with bad `zs`: the `Line3D(...)` constructor, `set_data_3d`, `set_3d_properties`;
  - the 2D→3D conversion helper used by `plot`.

  These should either validate before mutating state or leave the artist drawable.
- **Coverage expectation:** unknown project threshold. At minimum, the new test must fail on the current code and pass after the fix.

## Boundaries

- **Always:**
  - Keep raising an error for invalid `zs`.
  - Add a regression test that reproduces the persistent-failure scenario.
  - Keep the public `Axes3D.plot` / `Line3D` signatures unchanged.
- **Ask first:**
  - Changing the exception type or message raised for invalid input.
  - Changing `Line3D` behaviour for valid inputs, e.g. how `zs` is broadcast.
  - Making `Line3D.draw` silently tolerate missing data instead of preventing the bad state.
  - Any change outside `mpl_toolkits/mplot3d`.
- **Never:**
  - Swallow the input error silently.
  - Change pyplot's figure-management behaviour to work around this bug.
  - Add backend-specific (PyCharm/interagg) workarounds.
  - Remove or loosen existing tests.

## Success Criteria

1. `ax.plot(xs, ys, zs)` with `zs` not broadcastable to the shape of `xs` raises an exception at call time. Preferably it is a `ValueError` whose message mentions the shape mismatch; exact type and wording are an open question.
2. After that exception, `ax.get_lines()` (or the axes' artist list) contains no `Line3D` without valid 3D vertex data.
3. After that exception, `fig.canvas.draw()` on the same figure completes without `AttributeError`.
4. After that exception, a valid `ax.plot` on the same axes followed by a draw renders correctly.
5. Valid 3D line plotting is unchanged:
   - scalar `zs`, 1-D `zs` matching `xs`, and the `zdir` variants still behave as before;
   - the existing mplot3d test suite passes.
6. The regression test fails on the unfixed code and passes on the fixed code.

## Open Questions

1. Does the bug still reproduce on the current development branch, or was it fixed after 3.5.0?
2. Which fix strategy is preferred?
   - (a) Validate and broadcast `zs` before the line is added to the axes or converted to `Line3D`.
   - (b) On failure, remove the partially created line(s) from the axes.
   - (c) Make the `Line3D` constructor and conversion assign valid `_verts3d` before anything else, so a failure never leaves the attribute missing.
   - Or a combination of these.
3. Should the error for mismatched shapes become a matplotlib-raised `ValueError` with a clearer message, or is the raw NumPy broadcast error acceptable?
4. Is a ragged or 2-D `zs` ever meant to be valid for `Axes3D.plot`, for example to plot several lines at once as 2D `plot` does with 2-D inputs? If so, the expected behaviour changes from "raise" to "support".
5. Should `xs`/`ys` mismatches be covered too? They fail in the 2D `plot` path, before any 3D conversion.
6. What are the exact build, test and lint commands and the mplot3d test file location in this repository?
7. Should the fix be backported to a maintenance branch (e.g. 3.5.x)?