# Spec: Preserve DataFrame index when wrapping transformer output with `transform_output="pandas"` (FeatureUnion + aggregating transformer)

## Objective

**Problem.** With `set_config(transform_output="pandas")`, a `FeatureUnion` (built via `make_union`) raises an error when it wraps a custom transformer whose `transform` returns fewer rows than its input. In the report, the transformer does a groupby-sum: 96 hourly rows become 4 daily rows. The same pipeline works with `transform_output="default"`.

**Observed failure.**
`ValueError: Length mismatch: Expected axis has 4 elements, new values have 96 elements`

The traceback runs through `sklearn/utils/_set_output.py`:

1. `_wrap_method_output.<locals>.wrapped` calls `_wrap_data_with_container`.
2. `_wrap_data_with_container` calls `_wrap_in_pandas_container(data_to_wrap=..., index=getattr(original_input, "index", None), columns=estimator.get_feature_names_out)`.
3. Inside `_wrap_in_pandas_container`, the output is already a DataFrame, so the code runs `data_to_wrap.index = index`.
4. This assigns the input's 96-element index to the 4-row output, and pandas raises.

**Root cause (from the traceback).** When the transformer output is already a pandas DataFrame, the wrapper unconditionally overwrites its index with the index of the original input. This assumes output rows map 1:1 to input rows. That assumption breaks for transformers that change the number of rows, such as aggregation. It also discards a meaningful index the transformer produced (here, the dates).

**User.** Users of scikit-learn's set_output API who combine pandas output with custom transformers inside `FeatureUnion`. Those transformers return pandas objects whose index differs from the input's index.

**User story.** As a user with `transform_output="pandas"`, I want `make_union(MyTransformer()).fit_transform(data)` to return a DataFrame without raising. The result should be equivalent to the `"default"` output, and it should keep the index produced by my transformer.

**Acceptance criteria.**
- AC1: The issue's reproduction runs without error under `transform_output="pandas"`.
- AC2: The resulting DataFrame has 4 rows, and its index equals the transformer's groupby index (the 4 dates), not the input's hourly index.
- AC3: The values match the `"default"` output for the same input.
- AC4: When `data_to_wrap` is a pandas DataFrame, the wrapper does not overwrite its index with the original input's index.
- AC5: When `data_to_wrap` is not a pandas DataFrame (e.g. a numpy array), behavior is unchanged: a DataFrame is built using the original input's index and `get_feature_names_out` columns.
- AC6: Existing set_output behavior for DataFrame outputs is unchanged except for the index handling, including column renaming via `get_feature_names_out`.

## Assumptions

1. The fix belongs in the set_output wrapping layer (`_wrap_in_pandas_container` / `_wrap_data_with_container` in `sklearn/utils/_set_output.py`), not in `FeatureUnion` itself. The traceback shows the failure is in the generic wrapper.
2. A DataFrame returned by a transformer already carries the index the transformer intends. Re-indexing it with the input index is not needed for correctness when row counts match, because built-in sklearn transformers that return DataFrames preserve the input index themselves.
3. The `FeatureUnion` pandas path concatenates sub-transformer outputs into a DataFrame. In the repro, the inner transformer returns a `pd.Series`. That Series is not itself wrapped, because the custom `transform` is not wrapped with a defined `get_feature_names_out`. The failing wrap happens at the `FeatureUnion` level on the concatenated 4-row DataFrame. This is inferred from the error message (4 vs. 96), not verified against source.
4. Target versions are the scikit-learn development branch after 1.2.1 (reported on sklearn 1.2.1, pandas 1.4.4, Python 3.10).
5. The fix should apply to all estimators using set_output, not only `FeatureUnion`.
6. Transformers that change the number of samples are not formally guaranteed by the scikit-learn API contract. This spec only requires that the wrapper not crash or clobber the index, not that such transformers are supported everywhere (e.g. inside `Pipeline` with `y`).

## Tech Stack

- Python (reported 3.10.6)
- scikit-learn (reported 1.2.1; target: main branch, version unknown)
- pandas (reported 1.4.4; minimum supported version unknown)
- numpy (reported 1.23.5)

## Commands

Unknown; the repository is not visible. Expected categories:
- Build: unknown
- Test: unknown (likely a pytest invocation targeting the set_output and pipeline test modules; exact command and paths unknown)
- Lint: unknown

## Project Structure

Known from the traceback:
- `sklearn/utils/_set_output.py` contains `_wrap_method_output`, `_wrap_data_with_container` and `_wrap_in_pandas_container`.
- `sklearn/pipeline.py` contains `make_union` / `FeatureUnion` (module inferred from the public import `sklearn.pipeline`).

Test file locations are unknown. They are presumably the test modules for `_set_output` and `pipeline`.

## Code Style

Unknown beyond the snippets visible in the traceback. Follow existing scikit-learn conventions in `sklearn/utils/_set_output.py`. No code is prescribed by this spec.

## Testing Strategy

- **Framework:** presumably pytest, matching the existing scikit-learn test suite (unconfirmed).
- **Unit tests (set_output layer):**
  - When `_wrap_in_pandas_container` receives a DataFrame and an `index` argument of a different length, it returns the DataFrame with its original index and does not raise.
  - When it receives a DataFrame and an index of equal length, the original DataFrame index is kept. This is a behavior change to confirm; see Open Questions.
  - When it receives a numpy array, the provided index and columns are still applied. This is a regression guard.
- **Integration / non-regression test:** the issue's reproduction, using `FeatureUnion` with an aggregating transformer under `transform_output="pandas"`. Assert that it does not raise, has 4 rows, has an index equal to the groupby dates, and has values equal to the default-output result.
- **Regression:** the full existing set_output and pipeline test suites must pass.
- **Coverage expectations:** unknown; new branches in the wrapper must be covered.
- Tests must restore global config. Use a config context rather than leaving `set_config(transform_output="pandas")` active.

## Boundaries

- **Always:**
  - Add a non-regression test reproducing the issue.
  - Keep numpy/default output behavior unchanged.
  - Keep column naming via `get_feature_names_out` for DataFrame outputs.
  - Add a changelog entry if the project requires one (location unknown).
- **Ask first:**
  - Changing `FeatureUnion` internals rather than the shared wrapper.
  - Changing public set_output semantics beyond index preservation, e.g. how a `pd.Series` output is handled.
  - Adding a length check that raises a custom error instead of preserving the index.
- **Never:**
  - Silently truncate, reindex or reorder rows to force length agreement.
  - Remove or weaken existing set_output tests.
  - Add new dependencies.

## Success Criteria

- The issue's reproduction script prints a 4-row DataFrame under `transform_output="pandas"` without raising.
- The output index under pandas mode equals the transformer's returned index (dates 2020-01-01 to 2020-01-04).
- The numeric values are identical between `"default"` and `"pandas"` outputs.
- All existing scikit-learn tests pass, specifically those for set_output and pipeline/FeatureUnion.
- A new non-regression test fails before the change and passes after it.

## Open Questions

1. **Index scope.** Should the wrapper always preserve the index of a DataFrame output, or only when its length differs from the input index? Always preserving is simpler and consistent. It could change behavior for transformers that return a DataFrame with a default `RangeIndex` that users relied on being replaced by the input index.
2. **Contract.** Are sample-count-changing transformers inside `FeatureUnion` considered supported? Or is the goal only to stop the set_output layer from crashing (and from discarding the transformer's index)?
3. **Series outputs.** Should a transformer returning a `pd.Series`, as in the repro, be handled explicitly by the wrapper, e.g. converted to a DataFrame? Or is leaving it to `FeatureUnion`'s concatenation acceptable?
4. **Changelog and backport.** Should this be backported to the 1.2.x bugfix series? Where does the changelog entry go?
5. **Exact commands.** What are the exact test, lint and build commands and the test file paths? These are unknown without repository access.