# Spec: Skip `None` Estimators in Voting Ensemble `sample_weight` Support Check

## Objective

**Problem.** If any estimator in a voting ensemble is set to `None` (e.g. via `set_params(lr=None)`), calling `fit(X, y, sample_weight=...)` raises:

```
AttributeError: 'NoneType' object has no attribute 'fit'
```

The issue states the cause: the `sample_weight` support check does not skip estimators that are `None`.

**Reproduction (from the issue):**

```python
X, y = load_iris(return_X_y=True)
voter = VotingClassifier(
    estimators=[('lr', LogisticRegression()),
                ('rf', RandomForestClassifier())]
)
voter.fit(X, y, sample_weight=np.ones(y.shape))   # works
voter.set_params(lr=None)
voter.fit(X, y, sample_weight=np.ones(y.shape))   # AttributeError
```

**Users.** Anyone using a voting ensemble who disables a sub-estimator by setting it to `None` and also passes `sample_weight`.

**Expected behavior.**
- `None` estimators are excluded from the `sample_weight` support check.
- `fit` completes using only the remaining non-`None` estimators.
- The result is the same as fitting without `sample_weight`, where `None` estimators are already skipped.

**Acceptance criteria:**
1. The reproduction above runs without error.
2. After that second `fit`, the fitted ensemble contains only the non-`None` estimator(s). `predict` works.
3. `sample_weight` is still validated for every non-`None` estimator. If a non-`None` estimator does not support `sample_weight`, the existing error is still raised, with the same type and message as today.
4. If all estimators are `None`, the existing "all estimators are None" error is raised (current behavior, unchanged), not an `AttributeError`.
5. Behavior without `sample_weight` is unchanged.

## Assumptions

1. The fix belongs in shared voting-ensemble fitting logic. Any regressor counterpart (e.g. `VotingRegressor`, if present in this version) shares the same code path and needs the same fix and tests.
2. Setting an estimator to `None` is a supported, documented way to drop it from the ensemble. The bug is only that the `sample_weight` path ignores this.
3. The existing behavior when *all* estimators are `None` is to raise a `ValueError`. This should be preserved.
4. Estimator `weights` (the voting weights parameter) are out of scope. The issue concerns `sample_weight` passed to `fit`.
5. The project uses pytest (the standard for this library). This is unconfirmed for this repository.
6. No public API change is required, so no deprecation is needed.

## Tech Stack

- Python, NumPy; the library is scikit-learn (inferred from `VotingClassifier`, `LogisticRegression`, `RandomForestClassifier`, `load_iris`).
- Versions: **unknown**.

## Commands

- Build: **unknown**
- Test: **unknown** (likely a pytest invocation targeting the voting tests; exact command and path not visible)
- Lint: **unknown**

## Project Structure

- Voting ensemble source file: **unknown** (not visible in the issue).
- Voting ensemble test file: **unknown**.
- Changelog / release notes location: **unknown**.

## Code Style

- Follow the existing conventions of the voting ensemble module. Not visible here, so **unknown**.
- Error messages for unsupported `sample_weight` must remain unchanged.

## Testing Strategy

- **Level:** unit tests in the existing voting ensemble test module.
- **Regression test:** the issue's reproduction, asserting that the second `fit` succeeds and that the fitted ensemble contains only the remaining estimator.
- **Additional cases:**
  - A `None` estimator plus a non-`None` estimator that does *not* support `sample_weight`: the existing error is still raised.
  - All estimators `None` with `sample_weight`: the existing "all None" error is raised, not `AttributeError`.
  - If a voting regressor shares the code path, the same regression test is applied to it.
- No reduction of existing tests.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue.
  - Keep validation of `sample_weight` support for non-`None` estimators.
  - Run the voting ensemble test suite before committing.
- **Ask first:**
  - Changing error types or messages.
  - Changing behavior for the all-`None` case.
  - Refactoring the fitting logic beyond the `None` check.
  - Touching other ensemble classes.
- **Never:**
  - Silently drop `sample_weight` for estimators that do support it.
  - Remove or weaken existing tests.
  - Change the public API.

## Success Criteria

- The reproduction script from the issue runs to completion with no exception.
- New regression test(s) fail before the fix and pass after it.
- The full existing voting ensemble test suite passes.
- Unsupported-`sample_weight` errors for non-`None` estimators are unchanged.
- A changelog entry is added, if the project requires one for bug fixes (convention **unknown**).

## Open Questions

1. Does a voting regressor (or another voting class) exist in this version, and does it share the affected code path?
2. Should the `None` check be applied once, centrally (e.g. filter `None` estimators before all validation), or only in the `sample_weight` check?
3. What error, if any, is expected today when all estimators are `None` and `sample_weight` is passed? Should it match the no-`sample_weight` case exactly?
4. Are there other places in `fit` (or `set_params`/`get_params` handling) that assume non-`None` estimators and should be covered by this fix?
5. What are the test command, file locations, and changelog conventions for this repository?
6. Is `'drop'` (or any other sentinel) also supported for disabling estimators in this version? If so, does it need the same handling?