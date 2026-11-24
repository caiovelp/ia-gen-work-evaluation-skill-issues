# Spec: ColumnTransformer pandas output with zero-feature transformers

## Assumptions

1. The bug lives in scikit-learn's `ColumnTransformer` (`sklearn/compose/_column_transformer.py`), in the `_hstack` path. The issue says this path is used when `set_output(transform="pandas")` is active. Line numbers (~856–862) come from sklearn 1.2.0 and may have drifted.
2. The root cause is as the reporter describes:
   - Transformers whose column selection is empty are skipped during fit.
   - So they are absent from `self._iter(fitted=True)`.
   - The list of transformer names zipped with the output DataFrames is then misaligned with `Xs`.
   - As a result, `_add_prefix_for_feature_names_out` receives the wrong or empty input, and the column assignment fails with a length mismatch.
3. LightGBM is incidental. The bug reproduces with `ColumnTransformer` alone, and with `Pipeline` + any sklearn estimator. The fix and tests must not depend on LightGBM.
4. "Ignored" means the following for a zero-feature transformer:
   - It contributes no columns to the output.
   - It does not raise.
   - It does not appear in the output column names.
5. Behavior with the default (numpy) output already works and must stay unchanged.
6. The fix targets the current development branch of scikit-learn. Backporting to 1.2.x is a maintainer decision.
7. Empty selections can be expressed in several ways, and all of them should behave the same: an empty list `[]`, an empty boolean mask, an empty slice, or a callable returning an empty selection.

## Objective

Make `ColumnTransformer` with pandas output (`set_output(transform="pandas")`) work when one or more transformers select zero columns. Such transformers must be silently ignored, exactly as they are with numpy output.

**User:** sklearn users who build feature lists dynamically (e.g. `categorical_features = []`) and use pandas output, often inside a `Pipeline`.

**Acceptance criteria:**
- The reporter's reproduction fits without error when using a standard sklearn classifier in place of `LGBMClassifier`.
- `ColumnTransformer.fit_transform` and `.transform` both return a `pandas.DataFrame` whose columns are exactly the outputs of the non-empty transformers.
- Column names follow existing naming rules:
  - When `verbose_feature_names_out=True`, names are prefixed, e.g. `numerical__a`.
  - Otherwise names are unprefixed.
- The returned columns equal `get_feature_names_out()`.

## Tech Stack

- Python, scikit-learn (affected: 1.2.0; target: main branch, version unknown)
- pandas (reported with 1.4.1; minimum supported version unknown)
- numpy
- Exact supported version ranges: unknown (not in issue)

## Commands

Unknown — not visible in the issue. Presumably the project's standard pytest invocation on `sklearn/compose/tests/`, but the exact commands and flags are unknown.

## Project Structure

Known from the traceback/issue:
- `sklearn/compose/_column_transformer.py` → `ColumnTransformer`, including `_hstack`, `_iter`, `_add_prefix_for_feature_names_out`
- `sklearn/utils/_set_output.py` → set_output wrapping machinery
- `sklearn/pipeline.py` → `Pipeline` (only the caller, not expected to change)

Test file location: unknown. It is likely `sklearn/compose/tests/test_column_transformer.py`, but this is unverified.
Changelog location/format: unknown.

## Code Style

Follow existing scikit-learn conventions in `_column_transformer.py`. No snippet is available from the issue. The fix should reuse the existing logic that decides whether a transformer is "empty", i.e. the same logic that causes it to be skipped during fit, rather than introducing a parallel check.

## Testing Strategy

- Framework: pytest (assumed, as is standard for scikit-learn).
- Add a non-regression test that is parametrized over:
  - empty-selection forms: `[]`, empty boolean array, callable returning `[]`, and others as applicable;
  - transformer type: `'passthrough'`, `'drop'`, and a real estimator;
  - position of the empty transformer: first, middle, and last;
  - `verbose_feature_names_out`: `True` and `False`;
  - `remainder`: `'drop'` and `'passthrough'`.
- Assert all of the following:
  - no error is raised;
  - the output is a DataFrame;
  - `list(out.columns) == list(ct.get_feature_names_out())`;
  - the values match the numpy-output result.
- Cover both `fit_transform` and `fit` followed by `transform`.
- Do not use LightGBM. Use only sklearn estimators.

## Boundaries

- **Always:**
  - Add a non-regression test reproducing the issue.
  - Keep numpy/sparse output behavior unchanged.
  - Keep `get_feature_names_out()` consistent with the DataFrame columns.
- **Ask first:**
  - Changing which transformers appear in `transformers_` or `named_transformers_` after fit.
  - Changing the semantics of `_iter(fitted=True)` for other callers.
  - Emitting new warnings.
- **Never:**
  - Raise an error for empty selections, since the issue expects them to be ignored.
  - Add a dependency on LightGBM or any other third-party estimator.
  - Change public API signatures.

## Success Criteria

1. This code runs without error and returns a DataFrame with columns `['numerical__a', 'numerical__b', 'numerical__c']`:
   ```python
   ColumnTransformer([("categorical", "passthrough", []),
                      ("numerical", RobustScaler(), ["a", "b", "c"])],
                     remainder="drop").set_output(transform="pandas").fit_transform(X)
   ```
2. The same configuration with numpy output produces numerically identical values.
3. Empty transformers in any position, and multiple empty transformers, are handled.
4. With `remainder="passthrough"`, the remainder columns are still correctly named and placed.
5. The full existing `ColumnTransformer` test suite still passes.

## Open Questions

1. When *all* transformers select zero columns (and the remainder is dropped), should pandas output return an empty DataFrame with the original index, matching numpy's `(n_samples, 0)` behavior?
2. Should the fix be backported to the 1.2.x release line?
3. Is a changelog entry required, and in which file?
4. Should `_iter(fitted=True)` be changed to align consistently with `Xs`, or should only `_hstack` be fixed locally? The first is broader, the second carries less risk.
5. Are there other code paths with the same misalignment that should be fixed in the same change? Candidates include `transform` with pandas output, sparse output, and `get_feature_names_out` with empty transformers.
6. What is the minimum supported pandas version against which the fix must be verified?