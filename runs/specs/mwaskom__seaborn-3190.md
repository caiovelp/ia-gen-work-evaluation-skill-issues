# Spec: Support Boolean Data in `so.Plot` Color Mapping

## Objective

**Problem.** In the seaborn objects interface, passing boolean data to the `color` semantic raises a `TypeError` during scale setup:

```python
so.Plot(["a", "b"], [1, 2], color=[True, False]).add(so.Bar())
```

```
TypeError: numpy boolean subtract, the `-` operator, is not supported, use the bitwise_xor, the `^` operator, or the logical_xor function instead.
```

The traceback shows the following:

- The failure happens in `Plotter._setup_scales` (`seaborn/_core/plot.py`), which calls `scale._setup(var_df[var], prop)`.
- The scale chosen is a continuous one: `ContinuousBase._setup` in `seaborn/_core/scales.py`.
- The crash is at `b = forward(vmax) - forward(vmin)`, where `vmin` and `vmax` are numpy booleans and subtracting them is not allowed.

So boolean data is inferred as numeric and gets a continuous scale. The normalization step then subtracts numpy booleans, which numpy rejects.

**User.** Someone using `seaborn.objects` who maps a boolean column, such as a flag, mask, or yes/no field, to `color`. Other semantics may be affected as well (see Open Questions).

**Goal.** Boolean data passed to `color` produces a valid plot instead of an exception. The default mapping is sensible and documented.

**User stories / acceptance**

- As a user, I can pass a list, array, or Series of `bool` to `color=` and get a rendered plot.
- As a user, the legend shows meaningful entries for `True` and `False`.
- As a user, I can still force a specific scale type explicitly via `.scale(color=...)` without a crash. Exactly which scale types must work is an open question.

## Tech Stack

- Python, seaborn objects interface (`seaborn/_core/plot.py`, `seaborn/_core/scales.py`, both seen in the traceback).
- numpy, whose boolean `-` restriction triggers the error. pandas is presumably involved for data handling.
- Exact versions of Python, numpy, pandas, and matplotlib are **unknown**.

## Commands

All unknown; none were visible in the issue.

- Build: unknown
- Test: unknown (likely pytest, unconfirmed)
- Lint: unknown
- Dev / reproduce: run the snippet from the issue in a Python session with seaborn installed from source

## Project Structure

Known from the traceback:

```
seaborn/_core/plot.py    → Plot / Plotter; scale setup (Plotter._setup_scales)
seaborn/_core/scales.py  → Scale classes, incl. ContinuousBase._setup
```

Unknown or not visible:

- Where variable-type inference and default-scale selection live
- The test directory layout and the relevant test modules
- The location of the docs and changelog

## Code Style

Unknown. Follow existing conventions in `seaborn/_core/`. No style guide or snippet is available beyond the traceback lines.

## Testing Strategy

- **Regression test.** The exact snippet from the issue must run without raising.
- **Unit tests at the scale and property level:**
  - Default scale inference for boolean data on `color`.
  - Mapping of `True` and `False` to distinct colors.
  - Legend entries for boolean data.
- **Explicit-scale tests.** Boolean data with an explicitly requested scale, covering whichever types are decided under Open Questions, behaves as specified (works, or raises a clear error).
- **Input variants:**
  - Python `list[bool]`
  - numpy `bool` array
  - pandas `bool` Series
  - pandas nullable `boolean` dtype with missing values, if in scope
- **Non-regression.** Existing numeric, continuous, and categorical color tests still pass.
- Framework, test file locations, and coverage expectations are **unknown**.

## Boundaries

- **Always:**
  - Add a regression test for the reported snippet.
  - Keep existing behavior for non-boolean numeric and categorical data unchanged.
  - Run the existing test suite before committing.
- **Ask first:**
  - Changing the default scale type for booleans in a user-visible way that affects semantics other than `color`.
  - Changing public APIs or adding parameters, such as a scale-inference option for booleans.
  - Adding dependencies.
- **Never:**
  - Silently swallow the error or drop the boolean variable.
  - Remove or weaken existing tests.
  - Change unrelated scale behavior.

## Success Criteria

1. `so.Plot(["a", "b"], [1, 2], color=[True, False]).add(so.Bar())` renders without exception.
2. The two bars receive distinct colors, and the legend lists `True` and `False`, or labels as decided in Open Questions.
3. The same holds for numpy bool arrays and pandas bool Series inputs.
4. If the user explicitly requests a continuous color scale for boolean data, the result is either a working mapping (booleans cast to 0/1) or a clear, documented error. A raw numpy `TypeError` is not acceptable.
5. All pre-existing tests pass.

## Assumptions

1. The root cause is that boolean data is inferred as numeric and assigned a continuous scale. The traceback shows `ContinuousBase._setup` being used for `color`.
2. The preferred default is to treat boolean data as **categorical/nominal** for `color`, since there are two discrete levels.
3. The fix belongs in seaborn's `_core` (scale inference and/or `ContinuousBase._setup`), not in user code.
4. Other semantic properties that infer continuous scales could hit the same crash with booleans. Fixing `color` is the required scope; others are desirable.
5. Coordinate variables (x/y) with boolean data are out of scope unless they share the same code path.

## Open Questions

1. **Default semantics.** Should boolean data default to a categorical scale or a continuous one (cast to 0/1)? Should this apply to all semantic properties, or only to `color`?
2. **Explicit continuous scale.** If a user requests a continuous scale for boolean data, should booleans be cast to numeric, or should a clear error be raised?
3. **Legend ordering and labels.** Should the order be `True, False`, `False, True`, or the order of appearance? Should the labels read "True"/"False" verbatim?
4. **Missing values.** How should pandas nullable `boolean` dtype with `NA` values be handled?
5. **Scope beyond color.** Should the fix also cover the other properties (marker, linestyle, pointsize, alpha, etc.) and x/y coordinates in this change?
6. **Tooling.** What are the exact test, lint, and build commands, where do the tests live, and what dependency versions are supported?
7. **Release notes.** Does this need a changelog or release-notes entry, and where?