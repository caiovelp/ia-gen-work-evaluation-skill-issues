# Spec: Relax NCA Parameter Type Checks and Generalize Parameter Validation

## Objective

**Problem.** `NeighborhoodComponentsAnalysis` (NCA) validates its hyperparameters with exact type checks. `GridSearchCV` passes values exactly as they appear in the param grid, so valid-looking values are rejected:

- `tol=1` (a Python `int`) is rejected because NCA expects a float.
- `n_components=np.int64(k)` (from `np.arange(1, 10)`) is rejected because NCA expects a Python `int`.

The issue's example fits a `Pipeline([('nca', NCA()), ('knn', KNeighborsClassifier())])` inside `GridSearchCV(..., error_score='raise')` with `params = {'nca__tol': [0.1, 0.5, 1], 'nca__n_components': np.arange(1, 10)}`. It fails with a type error.

**Users.**
- Library users who tune NCA, or any estimator that uses the same validation helper, with `GridSearchCV` or similar tools. Their grids may contain Python ints where floats are expected, or NumPy scalar types.
- Library maintainers. They currently write ad-hoc, duplicated `_check_params` code, for example in LDA, and many parameters are never checked at all.

**Scope.** The issue bundles two separable capabilities. This spec covers both, but treats them as distinct deliverables (see Open Questions on splitting):

1. **Bug fix (required).** NCA accepts numerically valid values regardless of concrete Python or NumPy numeric type.
2. **Generalized validation helper (proposal).** Extend the existing parameter-checking tool from the NCA PR so that it:
   - checks against abstract numeric types (`numbers.Real`, `numbers.Integral`);
   - supports open, closed, half-open and unbounded intervals;
   - supports membership in a list of allowed values;
   - supports multiple allowed types per parameter, each with its own constraint.

**Proposed API (from the issue, not final):**
```
check_param(param, name, valid_options)
```
`valid_options` is a dict that maps each allowed type to a constraint:

| Constraint | Meaning |
|---|---|
| `None` | No constraint for that type |
| list | Allowed values (membership) |
| `Interval(left=..., right=..., closed=...)` | Range check |

Examples from the issue:
- NMF `beta_loss`: `{numbers.Real: None, str: ['frobenius', 'kullback-leibler', 'itakura-saito']}`
- LogisticRegression `l1_ratio`: `{numbers.Real: Interval(0, 1, closed='both')}`
- `max_iter`: `{numbers.Integral: Interval(left=1)}`

**Acceptance criteria (user-facing):**
- The issue's `GridSearchCV` example runs to completion without raising.
- NCA rejects truly invalid values with a clear error naming the parameter, the received value and its type, and the expected constraint. Examples of invalid values: non-numeric `tol`, `n_components <= 0`, `n_components` greater than the number of features (if that is currently checked).

## Assumptions

1. The existing helper introduced in the NCA PR is the right place to extend, rather than writing a new one. Its name and location are not stated in the issue and are **unknown**.
2. "Accept int for a float parameter" means accepting any `numbers.Real`. "Accept np.int64 for an int parameter" means accepting any `numbers.Integral`.
3. `bool` is a subclass of `int` and therefore of `numbers.Integral`, so it would pass integral checks unless explicitly excluded. Whether to exclude it is an open question; the default assumption is that the current behavior is preserved.
4. Integral values passed for real-valued parameters do not need to be converted to `float` by the validator; validation only checks them.
5. The fix must not change NCA's numerical results for previously accepted inputs.
6. Validation happens at `fit` time, not in `__init__`, consistent with estimators whose params are set via `set_params` in a grid search.
7. Error type stays as it is today: presumably `TypeError` for a wrong type and `ValueError` for out-of-range values. The current exception classes are **unknown**.
8. Migrating other estimators (LDA, NMF, LogisticRegression, ...) to the new helper is out of scope for the bug fix. Those are illustrative future adopters.

## Tech Stack

- Python, NumPy, scikit-learn. Versions are **unknown**.
- The standard-library `numbers` module, for abstract numeric types.

## Commands

- Build: **unknown**
- Test: **unknown**
- Lint: **unknown**

The issue's reproduction script can be used as a manual check: run it with Python and expect no exception.

## Project Structure

- NCA estimator source: **unknown**. It is exposed as `sklearn.neighbors.NeighborhoodComponentsAnalysis`.
- Existing parameter-checking helper from the NCA PR: **unknown**.
- LDA `_check_params`: **unknown** location. It is cited as an example of duplicated validation.
- Test locations: **unknown**.

## Code Style

Follow existing project conventions; they are **unknown** beyond the snippets in the issue. The issue's LDA snippet shows the current pattern to be replaced:

```python
if self.n_components <= 0:
    raise ValueError("Invalid 'n_components' parameter: %r"
                     % self.n_components)
```

Target style, illustrative only and taken from the issue's proposal:

```python
check_param(self.tol, 'tol', {numbers.Real: Interval(left=0, closed='neither')})
```

The `left=0, closed='neither'` bound for `tol` is an assumption; see Open Questions.

## Testing Strategy

The framework is **unknown** (presumably the project's existing test runner). Planned tests:

- **Regression test** reproducing the issue: NCA inside a `Pipeline` in `GridSearchCV` with an `int` `tol` and `np.int64` `n_components`. It must not raise.
- **Unit tests for NCA parameter validation:**
  - accepts `int`, `float`, `np.float32/64`, `np.int32/64` where numerically valid;
  - rejects wrong types and out-of-range values with the expected exception and message.
- **Unit tests for the generalized helper** (if in scope):
  - each interval closure (`'both'`, `'left'`, `'right'`, `'neither'`);
  - unbounded left and unbounded right;
  - list membership;
  - multi-type options, including the NMF `beta_loss` example;
  - `None` constraint;
  - a type matching none of the options;
  - the error message includes the parameter name and allowed options;
  - `bool` handling.
- Existing NCA tests must continue to pass unchanged, except tests that assert the old overly strict rejection.

## Boundaries

- **Always:**
  - Validate with abstract numeric types (`numbers.Real` / `numbers.Integral`), not concrete `int`/`float`.
  - Include the parameter name and the offending value in error messages.
  - Add a regression test for the reported example.
- **Ask first:**
  - Changing the public signature or name of the existing helper.
  - Making the helper public API.
  - Migrating other estimators (LDA, NMF, LogisticRegression, ...) to it.
  - Changing exception types.
  - Rejecting `bool` where it was previously accepted.
- **Never:**
  - Silently coerce invalid values.
  - Loosen checks so far that non-numeric values pass.
  - Change NCA's numerical behavior.
  - Remove existing validation tests without approval.

## Success Criteria

1. The issue's exact reproduction script completes with `error_score='raise'` and no exception.
2. NCA accepts `tol` given as `int`, `float`, or a NumPy float/int scalar when the value is in range.
3. NCA accepts `n_components` and other integer params (e.g. `max_iter`) given as Python `int` or any NumPy integer scalar when the value is in range.
4. NCA still raises for invalid types (e.g. string `tol`) and out-of-range values, with messages naming the parameter.
5. If the helper extension is in scope:
   - it supports open/closed/half-open/unbounded intervals, list membership, and multiple type→constraint options;
   - every combination is covered by unit tests.
6. All pre-existing tests pass.

## Open Questions

1. **Scope split.** Should the NCA bug fix ship separately from, and before, the generalized `check_param` design? They are independently testable, and the design discussion could block the fix.
2. What is the existing helper's name, location, and current signature? Should it be extended in place or replaced by `check_param`?
3. Should the helper be public API or private/internal?
4. Should `bool` be rejected for `numbers.Integral` and `numbers.Real` parameters?
5. **`Interval` semantics:**
   - Is `closed` one of `'both'`, `'left'`, `'right'`, `'neither'`?
   - What is the default when only `left` is given?
   - Should an interval apply to `numbers.Integral` and `numbers.Real` identically?
6. Should the helper also validate the *type* of list-membership values (e.g. `str` only), or only membership?
7. Exact valid ranges for each NCA parameter:
   - Is `tol` strictly positive or non-negative?
   - Is `n_components` bounded above by `n_features`?
   - `max_iter`, `verbose`, and others?
8. Which exceptions should be raised (`TypeError` vs `ValueError`), and is there a required message format?
9. Should the validator convert accepted values (e.g. `np.int64` to `int`) or only check them?
10. Is there a deprecation or compatibility concern for estimators that currently raise different errors once migrated?
11. Which estimators, if any, should adopt the helper in this change versus follow-ups (LDA, NMF, LogisticRegression were cited)?
12. Build, test, and lint commands, and the repository layout, are unknown and need confirming.