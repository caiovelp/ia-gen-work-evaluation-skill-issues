# Spec: Consistent labels from `GaussianMixture.fit_predict` and `predict` when `n_init > 1`

## Objective

Make `GaussianMixture.fit_predict(X)` return the same labels as calling `fit(X)` and then `predict(X)` on the fitted model, for every value of `n_init`.

**Current behaviour (from the issue, sklearn 0.20.2):**

- With the default `n_init`, `fit_predict(X)` and a later `predict(X)` agree.
- With `n_init=5`, they disagree on 88.6% of samples in the reported run (`X = numpy.random.randn(1000, 5)`, `n_components=5`).
- The existing unit test `test_gaussian_mixture_fit_predict` does not set `n_init`, so it misses this.

**Who is affected:** Anyone calling `fit_predict` on `GaussianMixture` with `n_init > 1`. The labels they get do not match the model that is actually stored on the estimator.

**What success means:**

- Labels from `fit_predict(X)` always match labels from `predict(X)` on the resulting fitted estimator.
- Both reflect the best of the `n_init` initializations, which is the one kept as the fitted model.

## Assumptions

1. The fitted model's stored parameters (the "best of `n_init`" run) are the correct reference. `predict` is right, and `fit_predict` is what must be brought into line, not the reverse. *(Needs confirmation; see Open Questions.)*
2. Suspected cause, to be verified and not yet confirmed: `fit_predict` derives its labels from state that does not belong to the selected best initialization. Examples would be the last initialization run, or responsibilities computed before the best parameters are restored. This hypothesis must be proven by reading the code before any change is made.
3. The shared fitting logic may live in a common mixture base class. If so, `BayesianGaussianMixture` likely has the same defect and falls in scope. *(Unverified; see Open Questions.)*
4. The fix must not change which initialization is selected as best, or the fitted parameters themselves (`weights_`, `means_`, `covariances_`, etc.). Only the labels returned by `fit_predict` should change.
5. Agreement is expected to be exact (`assert_array_equal`), not approximate, when `random_state` is fixed and the same `X` is used.
6. The reporter used Python 2.7 with sklearn 0.20.2. The fix targets the current development branch, whose supported Python versions are unknown to me.

## Tech Stack

- Language: Python (supported versions on the target branch: **unknown**)
- Library: scikit-learn, module `sklearn.mixture` (`GaussianMixture`)
- Dependencies seen in the report: numpy 1.16.0, scipy 1.2.0, Cython 0.28.5. Minimum versions on the target branch: **unknown**.
- Test helper used in the report: `sklearn.utils.testing.assert_array_equal`

## Commands

Not visible in the issue; all **unknown**:

- Build: unknown
- Test: unknown (the repo's test runner and the path to the mixture test module are not shown)
- Lint: unknown
- Reproduce: the script in the issue, ported to Python 3 `print()` syntax and run with a fixed `random_state`

## Project Structure

Only these locations are known or implied:

- `sklearn/mixture/`: public `GaussianMixture` (known from the import path)
- The test module containing `test_gaussian_mixture_fit_predict`: exact path **unknown**
- The base class or shared module implementing `fit` / `fit_predict` for mixtures: **unknown** (assumed to exist; see Assumption 3)

## Code Style

Follow the existing scikit-learn conventions in the surrounding mixture code. No style snippet is available from the issue (**unknown**). Any change should be minimal and localized to the fit / fit-predict path.

## Testing Strategy

**Framework:** the repo's existing test framework (assumed pytest; confirm). Use `assert_array_equal` as in the existing test.

**Regression tests to add or extend:**

1. **Extend `test_gaussian_mixture_fit_predict`**, or add a sibling test, to parametrize over `n_init` values, including `1` and at least one value `> 1` (e.g. 2 and 5).
2. **Assert exact equality** between:
   - labels from `fit_predict(X)` on one estimator, and
   - labels from `predict(X)` on that same estimator after the call.
3. **Cover all `covariance_type` values** the existing test already covers.
4. **Use a fixed `random_state`** so the test is deterministic. The data and settings should make the failure reproducible before the fix, e.g. the issue's `randn(1000, 5)`, `n_components=5`, `n_init=5`, with a seed confirmed to fail on the current code.
5. **If Assumption 3 holds**, add the equivalent test for `BayesianGaussianMixture`.
6. **Optionally**, assert that `fit_predict(X)` labels match `fit(X).predict(X)` on a separately constructed estimator with the same `random_state`. This guards against fitted parameters drifting between the two entry points.

**Test levels:** unit tests only. No integration or performance tests are needed.

**Pre-fix check:** the new test must fail on the current code before the fix (red), then pass after it (green).

## Boundaries

- **Always:**
  - Reproduce the bug with a deterministic test before changing code.
  - Keep `fit`, `fit_predict`, and `predict` consistent.
  - Run the full mixture test suite.
  - Add a changelog / what's-new entry if the project requires one (process **unknown**).
- **Ask first:**
  - Changing which initialization counts as "best".
  - Changing the public API, parameter defaults, or warning behaviour (e.g. convergence warnings).
  - Extending the fix beyond `GaussianMixture` / `BayesianGaussianMixture`.
  - Changing behaviour of the default `n_init=1` path in any observable way.
- **Never:**
  - Weaken or delete existing assertions in `test_gaussian_mixture_fit_predict`.
  - Make the test pass by loosening exact equality or by skipping `n_init > 1`.
  - Change the fitted parameters produced by `fit`.

## Success Criteria

- [ ] **Agreement for all `n_init`:** for `n_init ∈ {1, 2, 5}` and every supported `covariance_type`, with fixed `random_state`, `gm.fit_predict(X)` equals `gm.predict(X)` element-wise (exact).
- [ ] **Issue script passes:** the reproduction script from the issue (`n_components=5`, `n_init=5`, `X = randn(1000, 5)`, seeded) runs without `AssertionError`.
- [ ] **Fitted parameters unchanged:** after `fit_predict(X)`, the parameters are identical to those after `fit(X)` with the same `random_state` and data. This holds both before and after the fix.
- [ ] **No regressions:** existing mixture tests pass unchanged.
- [ ] **Tests fail before the fix:** the new or extended tests fail on the unfixed code.
- [ ] **Bayesian variant (if affected):** `BayesianGaussianMixture` satisfies the same agreement property.

## Open Questions

1. **Reference behaviour:** Is the intended contract that `fit_predict(X)` must equal `fit(X).predict(X)`, with the stored best-of-`n_init` model as the reference? (Assumed yes.)
2. **Root cause:** What is the actual cause? Assumption 2 is a hypothesis only and needs confirmation from the source.
3. **Shared code:** Does `BayesianGaussianMixture` share the affected code path, and should it be fixed in the same change?
4. **Non-convergence:** How should agreement behave when no initialization converges (convergence warning raised)? Should the labels still come from the best-by-lower-bound run?
5. **Other parameters:** Does `warm_start=True` interact with `n_init` here, and does it need its own test case?
6. **Repo specifics:** What are the exact test file path, test command, supported Python/numpy versions, and changelog process for the target branch?
7. **Backport:** Should the fix be backported to a 0.20.x maintenance release, or land only on the development branch?