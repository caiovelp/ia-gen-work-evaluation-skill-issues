# Spec: Fix `IndexError` in `LogisticRegressionCV.fit` when `refit=False`

## Objective

`LogisticRegressionCV(refit=False).fit(X, y)` raises `IndexError: too many indices for array` instead of completing. The failure is at the step that averages the best coefficients across CV folds.

**Who is affected:** Users who want cross-validation to choose the regularization parameter `C` without the final refit on the full dataset.

**Expected behavior (from the issue):** `fit` completes without error. With `refit=False`, the fitted attributes come from averaging, across folds, the coefficients at each fold's best hyperparameters. These attributes include `coef_`, `intercept_`, `C_` and `l1_ratio_`.

**Observed failure (from traceback):**

- File: `sklearn/linear_model/logistic.py`, method `LogisticRegressionCV.fit` (around line 2192–2194, sklearn 0.21.2)
- Failing expression:
  ```python
  w = np.mean([coefs_paths[:, i, best_indices[i], :]
               for i in range(len(folds))], axis=0)
  ```
- This is the `else` branch of the `refit=False` path. It indexes `coefs_paths` with 4 indices, but in the reporter's configuration the array has fewer dimensions.
- Reported solvers: `saga` and `liblinear`.
- Reported data: a binary target (`y = np.sign(...)`, so labels are {-1, 1}).

**User stories / acceptance criteria:**

1. As a user, I can call `LogisticRegressionCV(cv=5, solver='saga', tol=1e-2, refit=False).fit(X, y)` on the issue's reproduction data, and it returns without raising.
2. The same call works with `solver='liblinear'`.
3. After fitting with `refit=False`:
   - `coef_` has the same shape as with `refit=True` on the same data.
   - `intercept_` has the same shape as with `refit=True` on the same data.
   - `C_` holds finite values taken from `Cs_`.
4. The `refit=False` path also works for the other relevant combinations:
   - `multi_class` set to `'ovr'`
   - `multi_class` set to `'multinomial'`
   - binary and multiclass targets
5. Behavior with `refit=True` does not change.

## Assumptions

1. The bug is a shape/indexing mismatch. The `else` branch uses multinomial-style indexing, `coefs_paths[:, i, best_indices[i], :]`. That branch is reached for one-vs-rest / binary fits, where `coefs_paths` has already been reduced to the current class and has one fewer axis. Confirming this requires reading the source, which I cannot see.
2. The intended semantics of `refit=False` are already defined by the documentation: average the coefficients/intercepts across folds at each fold's best `C` (and `l1_ratio`). The fix should restore those semantics, not redefine them.
3. The reporter's `fit` call uses the default `multi_class` for 0.21.2. For a binary `y`, I assume this resolves to one-vs-rest behavior. The exact default and how it resolves need confirming in the source.
4. The fix belongs in `sklearn/linear_model/logistic.py`. That is the only path visible in the traceback.
5. The fix needs a non-regression test in the existing logistic regression test module. The exact test file path is **unknown** (not visible in the issue).
6. The public API does not change: no new parameters, and no change to the attributes exposed.
7. The fix must be compatible with the versions in the report: Python 3.6, numpy 1.15.1, scipy 1.1.0.

## Tech Stack

- Python (3.6.7 in report; supported range for the target branch: **unknown**)
- scikit-learn (bug reported against 0.21.2; target branch/version for the fix: **unknown**)
- numpy 1.15.1, scipy 1.1.0 (reporter's environment)
- Cython 0.29.6 (reporter's environment; likely irrelevant to this fix)

## Commands

All unknown: the repository is not visible.

- Build: **unknown**
- Test: **unknown**. Likely a pytest invocation against the logistic regression tests, but the path and flags are not confirmed.
- Lint: **unknown**
- Reproduce: run the snippet from the issue with Python, against a build that includes the change.

## Project Structure

Only what the issue shows:

```
sklearn/linear_model/logistic.py   → LogisticRegressionCV implementation (location of the failing code)
```

Test file location: **unknown**.

## Code Style

The repository is not visible, so project conventions are **unknown**. Follow the style of the surrounding code in `logistic.py`. The relevant existing code is the failing snippet:

```python
w = np.mean([coefs_paths[:, i, best_indices[i], :]
             for i in range(len(folds))], axis=0)
```

Any fix should match this numpy-vectorized, list-comprehension style and the existing variable names: `coefs_paths`, `best_indices`, `folds`, `Cs_`.

## Testing Strategy

- **Framework:** **unknown** (presumably pytest, as used by scikit-learn, but not confirmed from the repo).
- **Non-regression test:**
  - Fit `LogisticRegressionCV(refit=False)` on a small binary dataset and assert that no exception is raised.
  - Parametrize over at least `solver` ∈ {`saga`, `liblinear`} and `multi_class` ∈ {`ovr`, `multinomial`}. Skip combinations that are invalid; for example, `liblinear` does not support `multinomial`.
- **Shape checks:**
  - Compare `coef_`, `intercept_` and `C_` against a `refit=True` fit on the same data.
  - Cover both binary and multiclass targets.
- **Elastic-net check:** with `penalty='elasticnet'`, `solver='saga'`, `l1_ratios` set and `refit=False`, verify that `l1_ratio_` is populated sensibly. This exercises the neighboring `l1_ratio` averaging code in the same branch.
- **Non-elastic-net check:** with `penalty='l2'`, `refit=False` must not fail when computing `l1_ratio_`. In that case `l1_ratios` is not set by the user (see Open Questions).
- **Regression guard:** the existing `LogisticRegressionCV` tests must keep passing unchanged.

## Boundaries

- **Always:**
  - Add a non-regression test that reproduces the issue before the fix.
  - Keep `refit=True` behavior unchanged.
  - Preserve the documented `refit=False` semantics (cross-fold averaging at best hyperparameters).
- **Ask first:**
  - Changing the shape or meaning of public fitted attributes (`coef_`, `intercept_`, `C_`, `l1_ratio_`, `coefs_paths_`, `scores_`).
  - Changing the default `multi_class` resolution.
  - Refactoring beyond the `refit=False` branch.
- **Never:**
  - Silence the error by forcing a refit.
  - Catch and swallow the `IndexError`.
  - Remove or weaken existing tests.

## Success Criteria

1. The exact reproduction script from the issue runs without exception with `solver='saga'`.
2. The same script runs without exception with `solver='liblinear'`.
3. A new test covering `refit=False` × {`ovr`, `multinomial`} × {binary, multiclass} (valid solver combinations only):
   - fails on the pre-fix code;
   - passes on the fixed code.
4. With `refit=False`:
   - `coef_.shape` and `intercept_.shape` equal those produced with `refit=True` on the same input;
   - every value in `C_` is an element of `Cs_`.
5. With `refit=False` and a non-elasticnet penalty, `fit` completes, and `l1_ratio_` has a well-defined value (e.g. `None` entries). It does not raise.
6. The full existing `LogisticRegressionCV` test suite passes.

## Open Questions

1. **Target version/branch:** Which branch is the fix for (e.g. a 0.21.x bugfix release or the development branch)? This affects the changelog entry and the Python/numpy versions that must be supported.
2. **Root-cause confirmation:** Is the `else` branch reached specifically for `multi_class='ovr'` (including binary problems)? In that case `coefs_paths` would be 3-D (folds × Cs·l1_ratios × features) rather than 4-D. This needs confirming against the source.
3. **`l1_ratio_` with `refit=False`:** When `penalty != 'elasticnet'`, `l1_ratios_` presumably holds `None`. Does the averaging of `l1_ratios_[best_indices_l1]` in the same branch also fail, and what should `l1_ratio_` be in that case? (Presumably `None`.) Should this be fixed in the same change?
4. **Default `multi_class`:** What does the 0.21.2 default `multi_class` resolve to for the reporter's binary {-1, 1} labels? Is that resolution path also covered by tests?
5. **Changelog:** Is a changelog entry required, and where does it live? (Path **unknown**.)
6. **Test location and commands:** Which test file and which exact test command should be used? (**Unknown** from the issue.)