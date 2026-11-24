# Spec: Restore `pairplot` support for `hue_order` subsets of hue values

## Objective

**Problem.** In seaborn < 0.11, a user could plot a subset of the hue levels by passing a `hue_order` list containing only those levels. Rows whose hue value was not in `hue_order` were not plotted. In seaborn 0.11.1 the same call raises an exception instead. The first frame of the traceback is in `seaborn/_core.py`:

```
TypeError: ufunc 'isnan' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
```

**Reproduction (from the issue):**

```python
import seaborn as sns
iris = sns.load_dataset("iris")
# The hue column contains three species; plot only two
sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"])
```

**Who is affected.** Users of `sns.pairplot` who use `hue_order` to filter which hue levels appear. This is a regression from pre-0.11 behavior.

**Goal.** Restore the pre-0.11 behavior. When `hue_order` is a strict subset of the values in the `hue` column, `pairplot` should:

- succeed,
- plot only observations whose hue value is in `hue_order`, and
- order and color those levels according to `hue_order`.

**User stories / acceptance**

- As a user, I can call `pairplot(data, hue=col, hue_order=subset)` without an exception.
- As a user, I can see that points, and diagonal univariate plots, for excluded hue levels are absent from every panel.
- As a user, I can see that the legend lists only the levels in `hue_order`, in that order.

## Assumptions

1. The intended behavior is the pre-0.11 behavior: excluded levels are silently dropped, not reported as an error or warning.
2. The failure comes from the hue-mapping layer in `seaborn/_core.py`. Hue values outside `hue_order` probably have no lookup entry, and the fallback path calls `np.isnan` on a non-numeric (string) key. This is inferred from the traceback and has not been verified against source.
3. The same root cause may affect other functions that use the 0.11 hue-mapping core, such as `scatterplot` and `histplot` used on pairplot diagonals. The fix belongs in the shared layer, not only in `pairplot`.
4. The default diagonal kind for `pairplot` with `hue` (KDE in 0.11) and the off-diagonal scatter both need to respect the subset.
5. The issue does not depend on the matplotlib version or backend. It was reported on matplotlib 3.3.2 with the MacOSX, Agg and inline backends.
6. A subset `hue_order` on a numeric hue variable is out of scope unless it shares the same code path. The reported case is categorical (string) hue.

## Tech Stack

- Python library: seaborn. The bug was reported on 0.11.1; the target version for the fix is unknown.
- Dependencies seen in the issue: matplotlib 3.3.2, NumPy (`isnan` ufunc), and pandas (the iris DataFrame).
- Exact supported version ranges are **unknown** (not visible in the issue).

## Commands

All commands are **unknown**, because the repository is not visible:

- Build/install: unknown
- Test: unknown (likely pytest, but not confirmed)
- Lint: unknown
- Dev: N/A (library)

## Project Structure

- `seaborn/_core.py`: hue mapping core. This is where the first exception is raised, according to the issue.
- Location of `pairplot` / `PairGrid`: **unknown** (not shown in the issue).
- Test directory and file layout: **unknown**.
- Docs and changelog location: **unknown**.

## Code Style

- Unknown. Follow the existing conventions in `seaborn/_core.py` and the surrounding test files.
- No snippet is available from the repository.

## Testing Strategy

- **Regression test (required).** Reproduce the issue scenario: a categorical hue column with 3 levels and a `hue_order` containing 2 of them. Assert that `pairplot` completes without an exception.
- **Behavioral assertions:**
  - Off-diagonal axes contain only points from rows whose hue is in `hue_order`. Check this by artist count or by plotted offsets matching the filtered data.
  - Diagonal axes draw one artist set per included level only.
  - Legend entries equal `hue_order`, in order.
- **Core-level test.** Exercise the hue mapping in `_core.py` directly with data containing levels outside the order list. Assert that no exception is raised and that excluded values are handled consistently, for example by mapping to a sentinel or being dropped. The exact contract is an open question.
- **Guard tests.** Verify existing behavior is unchanged:
  - `hue_order` equal to the full set,
  - `hue_order` omitted,
  - numeric hue.
- Test framework, location and coverage requirements are **unknown**.
- Avoid network access in tests. The bundled iris dataset may require a download, so prefer a small synthetic DataFrame.

## Boundaries

- **Always:**
  - Add a failing regression test before the fix.
  - Keep the fix in the shared hue-mapping layer if that is where the root cause is.
  - Preserve existing behavior when `hue_order` covers all levels or is not given.
  - Run the full test suite.
- **Ask first:**
  - Changing public signatures.
  - Emitting a new warning for dropped levels.
  - Changing behavior of other plotting functions (`scatterplot`, `histplot`, `kdeplot`, etc.) beyond what is needed to fix the shared bug.
  - Adding dependencies.
- **Never:**
  - Mutate the user's input DataFrame.
  - Silently change behavior for numeric hue.
  - Remove or skip existing failing tests without approval.

## Success Criteria

1. `sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"])` runs without exception on the target version.
2. "virginica" observations do not appear in any panel, whether diagonal or off-diagonal.
3. The legend shows exactly `["setosa", "versicolor"]`, in that order, with palette colors assigned by position in `hue_order`.
4. A regression test covering this scenario is added, fails before the fix and passes after.
5. All existing tests pass.
6. A full-set `hue_order` and an omitted `hue_order` produce output identical to the current behavior.

## Open Questions

1. Should excluded hue levels be dropped silently, as in pre-0.11, or should a warning be emitted?
2. Should the fix apply to all functions built on the 0.11 hue-mapping core (e.g. `scatterplot(hue_order=subset)`), or only to `pairplot`? Do those functions currently fail the same way?
3. What is the expected behavior for a numeric hue variable when `hue_order` is given as a subset?
4. What should happen with data rows whose hue is NaN when `hue_order` is provided?
5. Should `PairGrid` used directly (not through `pairplot`) also support subset `hue_order`, and is it currently broken?
6. Which release branch or version should the fix target? Is a changelog or release-notes entry required, and where?
7. What are the repository's test, lint and build commands, and where do the tests live?