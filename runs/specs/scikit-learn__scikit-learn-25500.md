# Spec: Make `CalibratedClassifierCV` work with `set_config(transform_output="pandas")`

## Assumptions

1. This is a bug in scikit-learn, reported against version 1.2.0. The fix targets the scikit-learn codebase, not the user's code.
2. The root cause is the one the reporter identified. With `transform_output="pandas"`, the fitted `IsotonicRegression` calibrator's `predict` returns a 2D object of shape `(n_samples, 1)` (a DataFrame, or 2D data derived from one). It should return a 1D array of shape `(n_samples,)`. The assignment `proba[:, class_idx] = calibrator.predict(this_pred)` in `_CalibratedClassifier.predict_proba` (`sklearn/calibration.py`) then fails with `could not broadcast input array from shape (20,1) into shape (20,)`.
3. The likely mechanism is that `IsotonicRegression.predict` shares code with `IsotonicRegression.transform`, and the global output config wraps `transform`. This is inferred, not verified, because the source is not visible.
4. `predict` and `predict_proba` should return NumPy arrays whatever `transform_output` is set to. The `transform_output` setting is meant to affect `transform` / `fit_transform` only.
5. `method="sigmoid"` is not affected, since the issue reports only isotonic. This still needs checking (see Open Questions).
6. The minimal reproducer in the issue triggers the same error, even though the reported traceback comes from `cross_val_predict` on a `Pipeline`.
7. pandas is an optional dependency. Tests that use `transform_output="pandas"` must be skipped when pandas is not installed.

## Objective

Users who enable pandas output globally with `set_config(transform_output="pandas")` cannot use `CalibratedClassifierCV(method="isotonic")`. Calling `predict` or `predict_proba` crashes with a broadcast `ValueError`. The same failure happens when the model is used inside a `Pipeline` or `cross_val_predict`.

**Goal:** `CalibratedClassifierCV` must give the same results with the global pandas output config as without it.

**User story:** As a user who set `transform_output="pandas"` so that my transformers return DataFrames, I want calibrated classifiers to keep working, so that I don't have to turn the config off around calibration code.

**Acceptance criteria:**
- The issue's reproducer runs without error and `model.predict(...)` returns an array of shape `(30,)`.
- `model.predict_proba(X)` returns a NumPy array of shape `(n_samples, n_classes)` with rows summing to 1.
- Predictions and probabilities are numerically identical whether `transform_output` is `"default"` or `"pandas"`.

## Tech Stack

- Python, NumPy, SciPy, with pandas optional. The reporter used Python 3.9.15, numpy 1.23.5, scipy 1.9.3 and pandas 1.4.1.
- scikit-learn: bug reported on 1.2.0. The target branch/version for the fix is unknown.
- Components involved:
  - `sklearn.calibration.CalibratedClassifierCV`
  - `sklearn.calibration._CalibratedClassifier.predict_proba`
  - `sklearn.isotonic.IsotonicRegression` (`predict` / `transform`)
  - `sklearn.set_config` (`transform_output`)

## Commands

Unknown, because the repository is not visible. Required commands:
- Build (in-place / editable install): **unknown**
- Run the calibration and isotonic tests: **unknown** (presumably `pytest` on the relevant test modules; exact paths not confirmed)
- Lint/format: **unknown**

## Project Structure

Only what the issue reveals:
```
sklearn/calibration.py   → CalibratedClassifierCV, _CalibratedClassifier (predict_proba, ~line 764 in 1.2.0)
sklearn/isotonic.py      → IsotonicRegression (path assumed from the public import sklearn.isotonic; not shown in issue)
```
- Test file locations: **unknown**
- Changelog / what's-new location: **unknown**

## Code Style

Unknown from the issue. The fix should follow existing scikit-learn conventions in the touched modules. No snippet is provided because none can be verified.

## Testing Strategy

- **Framework:** pytest (assumed, standard for scikit-learn; not confirmed by the issue).
- **Regression test for calibration:** fit `CalibratedClassifierCV(..., method="isotonic")` while `transform_output="pandas"` is set, then call `predict` and `predict_proba`. Assert:
  - no error is raised
  - the outputs are NumPy arrays with the expected shapes
  - the outputs match a run without the pandas config
- **Scoping:** use a config context manager, or restore the config afterwards, so the global setting does not leak into other tests. Skip the test if pandas is unavailable.
- **Isotonic unit test:** check that `IsotonicRegression.predict` returns a 1D ndarray under `transform_output="pandas"`. Also check that `transform` still respects the pandas output config, which preserves existing behaviour.
- **Optional coverage:**
  - `method="sigmoid"`
  - binary and multiclass targets
  - `ensemble=True/False`
  - `cv="prefit"`
  - usage inside `cross_val_predict` on a `Pipeline`, mirroring the traceback

## Boundaries

- **Always:**
  - Keep `predict` / `predict_proba` outputs as NumPy arrays.
  - Keep numerical results identical to the default config.
  - Add regression tests.
  - Keep the `transform_output` change scoped inside tests.
- **Ask first:**
  - Changing the public output type or shape of `IsotonicRegression.transform` under the pandas config.
  - Changing how the `set_output` mechanism wraps methods globally.
  - Adding a changelog entry, since its location and format are unknown.
- **Never:**
  - Require users to disable `transform_output="pandas"` as the fix.
  - Make pandas a hard dependency.
  - Weaken or remove existing tests.

## Success Criteria

1. The issue's reproducer completes without exception under `set_config(transform_output="pandas")`.
2. For `CalibratedClassifierCV(method="isotonic")`, `predict_proba(X)` under the pandas config is a `numpy.ndarray` of shape `(n_samples, n_classes)`. It is `allclose`-equal (ideally exactly equal) to the result under the default config.
3. `cross_val_predict(pipeline_with_calibrated_isotonic, X, y, method="predict_proba")` succeeds under the pandas config.
4. `IsotonicRegression.predict` returns a 1D array under the pandas config, and its behaviour under the default config is unchanged.
5. All existing calibration and isotonic tests still pass.

## Open Questions

1. Where should the fix live?
   - Option (a): make `IsotonicRegression.predict` independent of the output config. This fixes every internal and external caller.
   - Option (b): defensively ravel or convert the calibrator output inside `_CalibratedClassifier.predict_proba`.
   - Option (c): both.
2. What should `IsotonicRegression.transform` return under the pandas config: a single-column DataFrame, as today? Is that the intended contract?
3. Are other estimators affected, where `predict` reuses a wrapped `transform`, or where internal code calls `transform` / `fit_transform` and expects arrays? Should the fix include an audit or a common test for this?
4. Should calibration fitting (`_fit_calibrator`) also be checked for config-dependent behaviour, even though the error appears only at predict time?
5. Is `method="sigmoid"` confirmed unaffected?
6. Which branch or version should the fix target, and is a backport to the 1.2.x bugfix release expected?
7. What are the exact build, test and lint commands, and where are the test files and changelog?