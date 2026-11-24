# Spec: Fix ZeroDivisionError in `_sparse_fit` When `support_vectors_` Is Empty

## Objective

Fitting a scikit-learn SVM estimator on **sparse** input crashes with `ZeroDivisionError: float division by zero` when the fitted model has **zero support vectors**. The same data fits without error as a **dense** array. This change makes the sparse path behave like the dense path in that situation.

**Users:** Anyone fitting libsvm-based estimators (the issue uses `SVR`) on `scipy.sparse` input whose solution has no support vectors. In the issue, this happens because every target lies inside the epsilon-tube.

**Observed (from the issue):**
- Version: `sklearn 0.21.3`, Python 3.5.2, numpy 1.17.0, scipy 1.3.0.
- Traceback: `sklearn/svm/base.py`, `fit` (line 209) → `_sparse_fit` (line 302), at the expression `dual_coef_indices.size / n_class`.
- With dense `x_train`, `model.fit` succeeds.
- With `scipy.sparse.csr_matrix(x_train)`, `model.fit` raises `ZeroDivisionError`.

**Expected (from the issue):** No error is raised, and `self.dual_coef_` is an empty `scipy.sparse.csr_matrix`. The issue writes this as `sp.csr_matrix([])`.

**Acceptance criteria:**
1. The reproduction script from the issue runs to completion without raising, for both dense and sparse inputs.
2. After the sparse fit, `model.dual_coef_` is a `scipy.sparse` CSR matrix with zero stored elements. Its exact shape is listed under Open Questions.
3. After the sparse fit, `model.support_vectors_` is sparse and has 0 rows.
4. The dense fit's behaviour and attributes are unchanged.
5. Sparse fits that have one or more support vectors are unchanged (no regressions in existing SVM tests).

## Assumptions

1. The root cause is the construction of the CSR index pointer for `dual_coef_` in `_sparse_fit`. When the number of support vectors is 0, the step derived from `dual_coef_indices.size / n_class` is 0, and building the index pointer with a zero step raises `ZeroDivisionError`. This is inferred from the traceback only. The surrounding code has not been seen.
2. `_sparse_fit` is shared by all libsvm-based estimators: `SVR`, `NuSVR`, `SVC`, `NuSVC`, and `OneClassSVM`. The fix and its tests should therefore cover more than `SVR`. This is unverified.
3. "Empty `dual_coef_`" should mean an empty CSR matrix of shape `(n_class, 0)`. Here `n_class` is the same row count the non-empty case would produce, which is presumably 1 for regression and one-class. This keeps it shape-compatible with the dense path.
4. The fix belongs on the current development branch, not the 0.21.x release line. The file location may have changed since 0.21.3, for example if `base.py` was renamed.
5. Only fitting must stop crashing. Prediction with zero support vectors should simply produce whatever the dense path produces, which is presumably the constant intercept.
6. No public API changes and no new dependencies are needed.

## Tech Stack

- Python, NumPy, SciPy (`scipy.sparse`), scikit-learn's libsvm wrapper.
- Versions from the issue: Python 3.5.2, numpy 1.17.0, scipy 1.3.0, sklearn 0.21.3.
- The supported versions on the target branch are **unknown**.

## Commands

The repository is not visible, so all commands are **unknown**. These need to be confirmed:
- Build (the Cython/libsvm extension): unknown
- Test (SVM test module): unknown
- Lint: unknown

## Project Structure

Known from the traceback:
- `sklearn/svm/base.py`: contains `fit` and `_sparse_fit`. This path is from 0.21.3; the current path is unknown.

Unknown:
- The location of the SVM tests, including any sparse-specific SVM test module.
- The location of the changelog / what's-new entry.

## Code Style

Unknown. Follow the existing conventions in the SVM module. No snippet is available.

## Testing Strategy

- **Framework:** assumed to be pytest, as used by scikit-learn. Test file locations are unknown.
- **Regression test (required):** a test built from the issue's data (`x_train`, `y_train`, `SVR(kernel='linear', C=316.227766017, epsilon=0.1, gamma=1.0, max_iter=15000)`). It should:
  - fit on `csr_matrix` input and assert that no exception is raised;
  - assert that `support_vectors_` has 0 rows;
  - assert that `dual_coef_` is sparse with zero stored elements and the agreed shape.
- **Dense/sparse parity:** for the same data, compare these attributes between the dense and sparse fits:
  - `dual_coef_` shape;
  - `intercept_`;
  - `predict` output.
- **Breadth:** if Assumption 2 holds, add a parametrized case for other estimators that can reach zero support vectors. Whether such inputs exist for the classifiers is an open question.
- **Regression safety:** the existing SVM test suite must pass unchanged.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep dense-path behaviour untouched.
  - Run the existing SVM tests.
- **Ask first:**
  - Changing the shape or type of `dual_coef_` in the non-empty case.
  - Touching the Cython/libsvm wrapper.
  - Raising an error or warning instead of returning an empty model.
- **Never:**
  - Suppress the exception with a broad `try/except`.
  - Alter the libsvm C sources.
  - Weaken or remove existing tests.

## Success Criteria

- The issue's reproduction script exits cleanly on the target branch.
- The new regression test(s) fail on the unfixed code and pass on the fixed code.
- Sparse and dense fits on the issue's data agree on:
  - `dual_coef_` shape;
  - number of support vectors;
  - `intercept_`;
  - predictions.
- The full existing SVM test suite passes.
- A changelog entry is added, if the project requires one (location unknown).

## Open Questions

1. **Exact `dual_coef_` shape.** The issue says `sp.csr_matrix([])`, which has shape `(1, 0)`. Should the shape instead mirror the dense path's empty `dual_coef_`, for example `(n_class, 0)`? What is the dense shape here?
2. **Prediction behaviour.** Should `predict`, `decision_function`, and similar methods work on a sparse model with zero support vectors? If so, should they return the intercept, matching dense?
3. **Warning.** Should fitting emit a warning when no support vectors are found, or is silent success intended? Does the dense path warn?
4. **Scope across estimators.** Does the same failure occur for `SVC`, `NuSVC`, `NuSVR`, and `OneClassSVM` with sparse input? Should all of them be covered by tests?
5. **Branch and backport.** Which branch is targeted, and is a backport to 0.21.x expected?
6. **Paths and commands.** What are the current path of the SVM base module, the test file locations, and the build/test/lint commands?