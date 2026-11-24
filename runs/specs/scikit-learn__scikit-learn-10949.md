# Spec: `warn_on_dtype` should warn when a pandas DataFrame's dtype is converted in `check_array`

## Assumptions

1. The function in scope is `sklearn.utils.validation.check_array`, which the issue names directly. Other validators that call it, such as `check_X_y`, are affected only through `check_array`.
2. `warn_on_dtype=True` already warns correctly for NumPy array inputs. The defect is specific to `pandas.DataFrame` inputs.
3. The warning class and message should match the existing behaviour for NumPy inputs. The issue expects `DataConversionWarning: Data with input dtype object was converted to float64.`
4. The default `dtype="numeric"` converts object dtype to `float64`. That conversion is what should trigger the warning in the reproduction.
5. The issue text appears twice. This is treated as one issue.
6. The target is the development version the reporter used (scikit-learn 0.20.dev0) with pandas 0.21.0. Other supported pandas versions should behave the same way.
7. No new public parameters or API changes are intended. This is a behavioural bug fix.
8. Repository layout, test commands and code style are not visible to me. Everything marked "unknown" below must be confirmed.

## Objective

When a user passes a `pandas.DataFrame` to `check_array(..., warn_on_dtype=True)` and validation changes the data's dtype, a `DataConversionWarning` must be raised. NumPy array inputs already behave this way. Currently no warning is raised for DataFrames, so users who opted in to dtype-change notifications are silently not notified.

**User:** scikit-learn users and internal estimators that rely on `warn_on_dtype` to detect implicit dtype conversion.

**User story:** As a user validating a DataFrame with `warn_on_dtype=True`, I want to be warned when my data is converted to a different dtype, so I can detect unintended conversions. Example: an `object` DataFrame converted to `float64`.

**Reproduction (from issue):**
```python
from sklearn.utils.validation import check_array
import pandas as pd
df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)
checked = check_array(df, warn_on_dtype=True)
```
- Expected: `DataConversionWarning: Data with input dtype object was converted to float64.`
- Actual: no warning.

## Tech Stack

- Python (issue environment: 3.6.3)
- NumPy 1.13.1, SciPy 0.19.1, pandas 0.21.0, scikit-learn 0.20.dev0 (from issue)
- Supported version ranges: unknown

## Commands

- Build: unknown
- Test: unknown (presumably a pytest invocation; not confirmed)
- Lint: unknown
- Dev: unknown

## Project Structure

- Module under change: `sklearn.utils.validation` (from the import in the issue). File path: unknown.
- Test location for `check_array`: unknown.
- Changelog / release-notes location: unknown.

## Code Style

Unknown. Follow the existing conventions in `sklearn.utils.validation` and its test module. The new warning must reuse the existing `DataConversionWarning` class and message format rather than introduce a new one.

## Testing Strategy

- **Framework:** unknown (assumed pytest-style tests in scikit-learn's existing test suite).
- **Level:** unit tests on `check_array`.
- **Required cases:**
  1. Object-dtype DataFrame with `warn_on_dtype=True` emits `DataConversionWarning` with the expected message (the issue reproduction).
  2. A DataFrame whose dtype already matches the requested dtype (e.g. `float64`) with `warn_on_dtype=True` emits no warning.
  3. An object-dtype DataFrame with `warn_on_dtype=False` (default) emits no warning.
  4. NumPy array inputs keep their current warning behaviour (regression guard).
  5. A mixed-dtype DataFrame (e.g. int and float columns) is covered according to the decision in Open Questions.
- Tests must skip cleanly if pandas is not installed. The mechanism for this in the repo is unknown.

## Boundaries

- **Always:**
  - Keep the warning type and message identical to the NumPy-input path.
  - Add regression tests reproducing the issue.
  - Run the existing validation test suite before committing.
- **Ask first:**
  - Changing the warning message format.
  - Changing behaviour for sparse inputs or other non-DataFrame array-likes.
  - Adding pandas as a hard dependency.
  - Changing the default value of `warn_on_dtype`.
- **Never:**
  - Make pandas a required import for `check_array`.
  - Change the dtype-conversion result itself; only the warning behaviour is in scope.
  - Remove or weaken existing tests.

## Success Criteria

1. Running the issue's reproduction with warnings enabled emits exactly one `DataConversionWarning`. Its message states input dtype `object` and output dtype `float64`.
2. No warning is emitted for a DataFrame when the output dtype equals the input dtype.
3. No warning is emitted when `warn_on_dtype=False`.
4. The returned array's values and dtype are unchanged from current behaviour.
5. All existing `check_array` / validation tests pass.
6. New regression tests cover cases 1–3 (and 5 once decided). They fail before the fix and pass after it.

## Open Questions

1. **Mixed-dtype DataFrames:** a DataFrame can have several column dtypes, so there may be no single "input dtype". Should the warning fire when any column's dtype differs from the output dtype? And what should the message report: all distinct dtypes, or a generic "mixed"?
2. **Other pandas containers:** should `pandas.Series` inputs (where applicable) and DataFrames with extension or categorical dtypes get the same treatment, or are they out of scope?
3. **Sparse DataFrames:** pandas 0.21 still had `SparseDataFrame`. Should this be considered, or excluded?
4. **Changelog:** is a changelog / what's-new entry required, and where does it go?
5. **Version support:** which pandas and NumPy versions must the fix and tests support?
6. **Test and lint commands:** what are the exact commands, and what conventions (e.g. a skip-if-no-pandas helper) does the repo use?