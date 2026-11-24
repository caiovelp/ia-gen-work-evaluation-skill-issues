# Spec: Make `PolyFit` robust to missing data

## Objective

`seaborn.objects.PolyFit` raises an uncaught `numpy.linalg.LinAlgError` when its input contains missing values. The fit should succeed using only the complete observations.

**Reproduction (from the issue):**

```python
so.Plot([1, 2, 3, None, 4], [1, 2, 3, 4, 5]).add(so.Line(), so.PolyFit())
```

**Observed:** `LinAlgError: SVD did not converge in Linear Least Squares`. It is raised from `np.polyfit(x, y, self.order)` in `PolyFit._fit_predict` (`seaborn/_stats/regression.py`, ~line 30). The call path is `Plotter._compute_stats` → `GroupBy.apply` → `PolyFit._fit_predict`.

**Expected:** The plot renders. A polynomial is fitted to the rows where both `x` and `y` are present. The fitted curve is drawn over the range of the non-missing `x` values.

**Users:** People using the `seaborn.objects` interface with real-world data that contains missing values (`None` / `NaN`).

**User stories / acceptance criteria:**

- As a user, when I add `so.PolyFit()` to a plot whose `x` or `y` contains missing values, I get a fitted line instead of an exception.
- As a user, if too few valid observations remain after missing values are removed, I get the stat's existing "not enough data" behavior. Today that is the branch that returns empty output (`xx = yy = []`, ~line 28). I do not get an exception.
- As a user, I can have missing values in only some groups (e.g. a `color` grouping), and each group is fitted on its own complete rows.

## Tech Stack

- Python. The traceback shows a Python 3.9 environment; the supported versions are unknown.
- numpy (`np.polyfit`, `np.polyval`, `np.linspace`)
- pandas (DataFrame input and groupby via `seaborn/_core/groupby.py`)
- seaborn `_core` / `_stats` modules (the objects interface)
- Exact dependency versions: **unknown**

## Commands

The commands are not visible in the issue. All are **unknown**:

- Build: unknown
- Test: unknown (pytest is assumed; see Assumptions)
- Lint: unknown
- Dev: unknown

## Project Structure

Only these files are known from the traceback:

```
seaborn/_stats/regression.py  → PolyFit stat (__call__, _fit_predict); the location of the bug
seaborn/_core/groupby.py      → GroupBy.apply; calls the stat per group
seaborn/_core/plot.py         → Plot / Plotter; _compute_stats invokes stats
```

- Test locations: **unknown**
- Docs and changelog location: **unknown**

## Code Style

- Follow the existing conventions in `seaborn/_stats/regression.py`. No style guide or linter config is visible in the issue.
- Any example snippet would be invented, so none is given here.

## Testing Strategy

- Framework: **unknown** (pytest is assumed).
- Test location: **unknown**. Presumably it sits next to the existing tests for `seaborn/_stats/regression.py`.
- Required test levels:
  - **Unit (stat level):** Call `PolyFit` directly on a DataFrame with missing values in `x`, in `y`, and in both. Assert that:
    - no exception is raised;
    - the output has `gridsize` rows;
    - the output `x` spans the min and max of the non-missing `x`;
    - the output contains no NaN.
  - **Unit, equivalence:** For the same data, PolyFit with NaNs gives the same result as PolyFit on the data with the NaN rows dropped beforehand.
  - **Unit, degenerate case:** After rows are dropped, there are too few unique `x` values for `order`. Assert the existing empty-output behavior and no exception.
  - **Unit, all missing:** Every row has a missing `x` or `y`. Assert empty output and no exception.
  - **Grouped:** One group has missing values and another does not. Both groups are fitted correctly.
  - **Integration / smoke:** The exact reproduction from the issue compiles via `Plot.plot()` without raising.
- Coverage expectations: **unknown**

## Boundaries

- **Always:**
  - Drop missing rows using **pairwise** completeness. A row is excluded when its `x` or its `y` is missing.
  - Apply the existing "too few points" guard *after* missing data is removed.
  - Add regression tests for the reproduction case.
  - Keep the output schema unchanged: the same columns and the same `gridsize` semantics.
- **Ask first:**
  - Changing missing-data handling globally in `Plotter._compute_stats` or `GroupBy`, rather than locally in `PolyFit`.
  - Emitting warnings when rows are dropped.
  - Changing behavior for non-finite values (`inf`), which differ from missing values.
  - Changing the `PolyFit` public parameters or the minimum-data rule.
- **Never:**
  - Silently impute or fill missing values.
  - Swallow `LinAlgError` generically with a try/except that hides other real failures.
  - Change other stats' behavior as part of this fix without approval.

## Success Criteria

1. `so.Plot([1, 2, 3, None, 4], [1, 2, 3, 4, 5]).add(so.Line(), so.PolyFit()).plot()` completes without raising.
2. The fitted values equal those from fitting only the complete rows: `x=[1, 2, 3, 4]`, `y=[1, 2, 3, 5]`.
3. The prediction grid spans `[min, max]` of non-missing `x`, has length `gridsize`, and contains no NaN.
4. Missing values in `y` only, or in both `x` and `y`, are handled the same way.
5. When too few valid points remain, the result is empty output (the existing behavior) with no exception.
6. In grouped plots, missing values are handled independently per group.
7. All existing tests continue to pass (test command unknown).

## Assumptions

1. `None` in the input list is converted to `NaN` by pandas during plot data processing, so `x` reaches `_fit_predict` as a float Series containing `NaN`.
2. The correct semantics is to drop incomplete observations, which is consistent with how seaborn generally handles missing data. Imputation is not wanted.
3. The fix belongs in `PolyFit._fit_predict` (or `PolyFit.__call__`). A broader change to core missing-data handling is out of scope.
4. The existing guard before `np.polyfit` (~lines 27–28, producing `xx = yy = []`) checks whether there is enough data for the requested `order`. It should be evaluated on the cleaned data. Its exact condition is not visible in the issue.
5. pytest is the test framework.
6. `pd.NA` and `NaT` are treated as missing like `NaN`, provided pandas null detection covers them.

## Open Questions

1. Should missing-data dropping happen locally in `PolyFit`, or centrally in `_compute_stats` / `GroupBy` for all stats? Other stats may have the same bug.
2. Should infinite values (`±inf`) also be excluded, or only `NaN` / `None`?
3. Should dropping rows emit a warning or stay silent?
4. What is the exact "not enough data" condition today (e.g. `x.nunique() <= order`)? Should it remain unchanged after missing data is removed?
5. What are the test and lint commands, where do the tests live, and is a changelog/release-notes entry required?
6. Which Python, numpy, and pandas versions must be supported?