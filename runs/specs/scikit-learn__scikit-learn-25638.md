# Spec: Support nullable pandas dtypes in `unique_labels`

## Objective

`sklearn.utils.multiclass.unique_labels` should accept pandas Series that use the nullable extension dtypes `"Int64"`, `"Float64"` and `"boolean"`. Its behavior should match what happens when the same data uses the numpy-backed dtypes `"int64"`, `"float64"` and `"bool"`.

**Current behavior (sklearn 1.2.1):** these dtypes become `object` dtype when converted to a numpy array. Target-type detection then classifies them as `'unknown'`. Mixing them with a regular `int64` Series raises:

```
ValueError: Mix type of y not allowed, got types {'binary', 'unknown'}
```

**Users:** people who pass pandas data with nullable dtypes to sklearn, either through metrics or directly to `unique_labels`. Today they must convert to numpy with an explicit dtype first. The issue describes this as their current workaround.

**User story:** As a user with labels stored in a nullable-dtype pandas Series, I can call `unique_labels(y_true, y_pred)` without converting my data by hand. I get the same result as with the equivalent numpy-backed dtype.

**Acceptance criteria (from the issue):**

```python
import pandas as pd
from sklearn.utils.multiclass import unique_labels

for dtype in ["Int64", "Float64", "boolean"]:
    y_true = pd.Series([1, 0, 0, 1, 0, 1, 1, 0, 1], dtype=dtype)
    y_predicted = pd.Series([0, 0, 1, 1, 0, 1, 1, 1, 1], dtype="int64")
    unique_labels(y_true, y_predicted)  # must not raise
```

- The result must equal the result for the corresponding numpy-backed dtype: `"Int64"`→`"int64"`, `"Float64"`→`"float64"`, `"boolean"`→`"bool"`.

## Assumptions

1. The root cause is in target-type detection, believed to be `type_of_target` in the same module. That function returns `'unknown'` for the `object`-dtype array produced from a nullable pandas Series. The fix most likely belongs where the input is converted to numpy, not in `unique_labels`' mixing check. This has not been verified against the source.
2. The scope covers only the three dtypes named in the issue: `Int64`, `Float64` and `boolean`. Other nullable or extension dtypes are out of scope unless confirmed: sized variants such as `Int32`/`UInt8`/`Float32`, `string`, and `category`.
3. "Same behavior" covers two things:
   - **Type detection:** the same `type_of_target` classification as the numpy-backed dtype, e.g. `'binary'` for this data.
   - **Output:** the same set of returned labels.
   Exact dtype equality of the returned array is not required unless confirmed.
4. Inputs that contain missing values (`pd.NA`) are a separate concern. This change only needs to handle nullable-dtype Series with **no** missing values.
5. A fix to type detection may also affect other callers, such as metrics and classifiers that call `type_of_target`. Such side effects are acceptable and desirable, as long as existing behavior for non-pandas inputs and plain `object` arrays (e.g. string labels) does not change.
6. pandas stays an optional dependency. Any pandas-specific handling must not import pandas unconditionally.
7. Supported pandas/numpy version ranges are whatever the project already supports. This change does not alter them.

## Tech Stack

- Python, NumPy, scikit-learn (the issue reproduces on 1.2.1), and pandas (optional dependency).
- Exact versions and minimum supported pandas version: **unknown**. These are not visible in the issue.

## Commands

The repository is not accessible. All commands are **unknown** and must be confirmed:

- Build: unknown
- Test: unknown. Pytest is the likely runner, since the issue's repro uses `pytest`, but the exact invocation is unknown.
- Lint: unknown
- Dev: unknown

## Project Structure

- Affected public function: `sklearn.utils.multiclass.unique_labels`. The module path comes from the issue's import.
- Likely related function: target-type detection in the same module. This is an assumption; see Assumption 1.
- Source file path, test file location and changelog location: **unknown**.

## Code Style

- Unknown; the codebase is not visible. Follow the conventions already used in the surrounding module and its tests.
- Tests should be parametrized over the dtype pairs, mirroring the loop in the issue's repro.

## Testing Strategy

- **Framework:** pytest. This is inferred from the issue repro; the exact configuration is unknown.
- **Location:** alongside the existing tests for `sklearn.utils.multiclass`. The exact path is unknown.
- **Pandas availability:** tests that need pandas should be skipped when pandas is not installed, using whatever mechanism the project already has (unknown).
- **Test levels:**
  - **Unit, `unique_labels`:** for each nullable dtype in `["Int64", "Float64", "boolean"]`, call `unique_labels(nullable_series, int64_series)`. It must not raise, and the result must equal the result of calling it with the corresponding numpy-backed dtype.
  - **Unit, type detection** (if the fix lives there): the nullable-dtype Series must get the same target type as its numpy-backed counterpart, e.g. `'binary'`.
  - **Regression:** existing tests for `unique_labels` and type detection still pass. In particular, plain `object` arrays and mixed-type inputs that currently raise must still raise.
- **Coverage expectations:** unknown. At minimum, every new code path must be exercised.

## Boundaries

- **Always:**
  - Add tests that reproduce the issue's failing case before or alongside the fix.
  - Keep pandas optional.
  - Preserve existing behavior for non-pandas inputs.
  - Run the existing multiclass utility tests.
- **Ask first:**
  - Changing public function signatures.
  - Handling `pd.NA` / missing values.
  - Extending support to dtypes beyond the three named.
  - Changing the error message or type-detection results for any input that currently does not raise.
  - Adding dependencies.
- **Never:**
  - Make pandas a hard dependency.
  - Silently coerce genuinely mixed label types, e.g. strings and ints, into a single type.
  - Remove or weaken existing tests.
  - Change the "Mix type of y not allowed" check for truly mixed inputs.

## Success Criteria

1. The issue's repro loop over `"Int64"`, `"Float64"` and `"boolean"` runs without raising `ValueError`.
2. For each nullable dtype, `unique_labels(nullable_y_true, int64_y_pred)` returns the same labels as `unique_labels(numpy_backed_y_true, int64_y_pred)`.
3. Target-type detection for each nullable-dtype Series in the repro returns the same type as for its numpy-backed counterpart (`'binary'`).
4. New tests covering criteria 1–3 are added and pass. They are skipped cleanly when pandas is unavailable.
5. All existing tests in the multiclass utilities test suite pass unchanged.
6. A changelog entry is added if the project requires one. The process for this is unknown.

## Open Questions

1. **Missing values:** what should happen when a nullable Series contains `pd.NA`? Options are to raise a clear error, to behave like the `float64` + `NaN` case, or to leave this out of scope.
2. **Dtype scope:** should support extend to all nullable integer and float widths and to unsigned variants (`Int8`–`Int64`, `UInt*`, `Float32`)? Should `string` or `category` dtypes also be considered?
3. **Fix location:** should the fix live in target-type detection, so that every caller such as metrics and classifiers benefits, or be limited to `unique_labels`?
4. **Return dtype:** is matching the returned labels enough, or must the returned array's dtype also match the numpy-backed case?
5. **Versions:** what is the minimum supported pandas version, and do all supported versions provide the APIs needed to convert nullable dtypes to their numpy equivalents?
6. **Commands and paths:** what are the build/test/lint commands, the test file location, and the changelog process for this repository?
7. **Backport:** should this be targeted at a bugfix release or only the next feature release?