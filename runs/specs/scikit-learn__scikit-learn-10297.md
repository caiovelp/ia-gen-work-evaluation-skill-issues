# Spec: Add `store_cv_values` support to `RidgeClassifierCV`

## Objective

`sklearn.linear_model.RidgeClassifierCV` does not accept a `store_cv_values` constructor parameter. Its documentation still describes a `cv_values_` attribute that depends on `store_cv_values=True` and `cv=None`. Passing the parameter fails:

```
TypeError: __init__() got an unexpected keyword argument 'store_cv_values'
```

**Goal:** `RidgeClassifierCV` should accept a boolean `store_cv_values` parameter, as its regression counterpart `RidgeCV` does. When the flag is enabled and efficient Leave-One-Out cross-validation is used (`cv=None`), the fitted estimator should expose `cv_values_`. The code and the docs will then agree.

**Users:** scikit-learn users who fit `RidgeClassifierCV` and want to inspect the per-sample, per-alpha cross-validation values, for example to plot them or to choose alpha themselves.

**User story:** As a user, I can call `RidgeClassifierCV(alphas=..., store_cv_values=True).fit(X, y)` on classification targets. I can then read `cv_values_` with a documented shape, without getting a `TypeError`.

### Acceptance criteria

1. `RidgeClassifierCV.__init__` accepts `store_cv_values` (bool). Its default keeps current behaviour, which is assumed to be `False`.
2. With `store_cv_values=True` and `cv=None`, after `fit`:
   - `cv_values_` exists.
   - Its shape matches the documented contract: `[n_samples, n_alphas]` for a single response, or `[n_samples, n_responses, n_alphas]` for several responses. For a classifier, "responses" are the binarized class columns (see Open Questions).
3. With `store_cv_values=False`, which is the default, `cv_values_` is not set. Behaviour and results stay the same as before the change.
4. With `store_cv_values=True` and a non-`None` `cv`, the estimator behaves the same way `RidgeCV` does in that situation (see Open Questions).
5. `get_params()` / `set_params()` round-trip `store_cv_values`. `clone()` preserves it.
6. The docstring for `RidgeClassifierCV` documents the `store_cv_values` parameter. The existing `cv_values_` attribute description stays accurate.
7. A changelog / what's-new entry records the fix, if the project requires one for this kind of change.

### Note on the reproducer

The script in the issue passes a continuous target (`y = np.random.normal(size=n)`) to a classifier. Once `store_cv_values` is accepted, that script would probably fail later, at `fit`, with a label-type error. That failure is expected classifier behaviour and is **out of scope**. Tests for this spec must use valid classification targets.

## Assumptions

1. `RidgeCV` already supports `store_cv_values` and `cv_values_`. `RidgeClassifierCV` shares a common CV base with it, but its constructor does not forward the parameter. *(Inferred from the issue's documentation quote, not verified in code.)*
2. The default value of `store_cv_values` is `False`, matching `RidgeCV`.
3. `cv_values_` for the classifier is computed on the internal binarized/encoded targets (one column per class, or one column for binary problems). It is not computed on the original labels.
4. The `normalize` parameter used in the issue exists in the targeted version and does not interact with this change.
5. The fix targets the current development branch, not a backport to 0.19.x.
6. This is a single capability, so Phase 0 (capability map) does not apply.

## Tech Stack

- Python, NumPy, SciPy, scikit-learn. The issue reports Python 3.6.3, NumPy 1.13.3, SciPy 0.19.1 and scikit-learn 0.19.1.
- The supported version range on the target branch is **unknown**.

## Commands

All commands are **unknown**, because the repository is not visible. The following need confirming:

- Build/install (in-place dev build): unknown
- Test (targeted to ridge tests): unknown
- Lint/style check: unknown
- Docs build: unknown

## Project Structure

Exact paths are **unknown**. Expected locations, to be confirmed:

- The module defining `RidgeClassifierCV`, `RidgeCV` and their shared CV base, inside `sklearn.linear_model`: path unknown
- Tests for the ridge estimators: path unknown
- What's-new / changelog file for the target release: path unknown

## Code Style

Unknown, because no repository code is visible. Follow the conventions already used in the existing `RidgeCV` constructor and docstring, which use NumPy-style docstrings with `Parameters` / `Attributes` sections. Keep parameter naming, ordering style and docstring wording consistent with `RidgeCV`'s `store_cv_values` documentation.

## Testing Strategy

- **Framework:** the project's existing unit test framework. The name and command are unknown.
- **Level:** unit tests next to the existing ridge tests.
- **Cases to cover:**
  - Construction with `store_cv_values=True` does not raise.
  - Binary classification, `cv=None`, `store_cv_values=True`: `cv_values_` exists with shape `(n_samples, n_alphas)`, or whatever single-column layout is decided (see Open Questions).
  - Multiclass classification, `cv=None`, `store_cv_values=True`: `cv_values_` has shape `(n_samples, n_classes, n_alphas)`.
  - Default (`store_cv_values=False`): `cv_values_` is absent, and predictions match those of an estimator built without the parameter.
  - `store_cv_values=True` with an explicit `cv`: behaviour matches `RidgeCV`, whether that is an error or the flag being ignored.
  - `get_params` / `clone` include and preserve `store_cv_values`.
- **Regression:** the existing ridge test suite passes unchanged.
- **Coverage expectation:** the new parameter path is exercised. Any numeric coverage threshold is unknown.

## Boundaries

- **Always:**
  - Keep backward compatibility, so that the default behaviour of `RidgeClassifierCV` is unchanged.
  - Mirror `RidgeCV` semantics for `store_cv_values`.
  - Update the docstrings.
  - Add tests.
  - Run the ridge test suite before committing.
- **Ask first:**
  - Changing `RidgeCV`'s behaviour or the shared base class signature in ways that affect other estimators.
  - Renaming `store_cv_values` or `cv_values_`.
  - Adding deprecations.
  - Changing the documented shape of `cv_values_`.
- **Never:**
  - Change the classifier's target validation to accept continuous `y`.
  - Remove or weaken existing tests.
  - Alter numerical results for the default configuration.

## Success Criteria

- `RidgeClassifierCV(alphas=..., store_cv_values=True).fit(X, y_class)` succeeds with valid class labels and `cv=None`.
- The fitted model exposes `cv_values_` with the agreed shape for both binary and multiclass targets.
- With the default settings, nothing changes: there is no `cv_values_`, and predictions and `alpha_` are identical to before.
- `store_cv_values` appears in `get_params()` and in the `RidgeClassifierCV` docstring.
- The new tests pass, and the existing ridge tests still pass.

## Open Questions

1. **Shape for binary problems:** Should `cv_values_` be `(n_samples, n_alphas)` or `(n_samples, 1, n_alphas)` for binary classification? The answer depends on how the targets are binarized internally. Should the docstring spell this out for the classifier?
2. **Non-`None` `cv`:** What should happen when `store_cv_values=True` is combined with an explicit `cv`? Should it raise a `ValueError`, as `RidgeCV` presumably does, or silently ignore the flag?
3. **What the values mean:** For a classifier, should the docstring clarify that `cv_values_` contains LOO errors or predictions on the encoded targets, not on class labels?
4. **Release target:** Which release should get the what's-new entry, and is a backport to 0.19.x wanted?
5. **Commands and paths:** What are the repository's build, test and lint commands, and the exact file paths? All are currently unknown.
6. **Reproducer:** Should the issue's reproducer be corrected in the issue thread? Its continuous `y` is a separate user error.