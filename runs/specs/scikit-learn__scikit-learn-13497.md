# Spec: Fix string-to-array comparison of `discrete_features` in `_estimate_mi`

## Assumptions
1. `_estimate_mi` is the private helper behind the public mutual-information estimators. In scikit-learn these are `mutual_info_classif` and `mutual_info_regression`. The issue does not name the project, module or callers, so this is inferred.
2. `discrete_features` accepts three forms: the string `'auto'`, a boolean, or an array-like. The array-like is either a set of feature indices or a boolean mask of length `n_features`. The issue confirms `'auto'`, indices and masks. Scalar booleans are an assumption.
3. The current behaviour for the three issue-mentioned forms (`'auto'`, index array, boolean mask) is intended. Only the comparison is wrong. The intended semantics must not change.
4. The defect has two parts:
   - The comparison `discrete_features == 'auto'` does an element-wise comparison when `discrete_features` is an ndarray.
   - NumPy warns about this today (FutureWarning or DeprecationWarning) and will change the behaviour or raise in future versions.
5. The project uses NumPy, and its test suite runs with NumPy warnings visible or able to be made fatal. The test framework is assumed to be pytest. This is unconfirmed.
6. No public API change is wanted. The fix is internal, plus new tests.

## Objective
`_estimate_mi` checks whether `discrete_features` is the string `'auto'` with `discrete_features == 'auto'`. When the caller passes an array of indices or a boolean mask, this compares an array with a string. It produces a NumPy warning now and will error or misbehave in future NumPy versions. The code paths for non-`'auto'` values also appear to be untested.

The goal is twofold:
- Make `_estimate_mi` handle every supported form of `discrete_features` correctly, with no element-wise string comparison and no NumPy warnings.
- Add test coverage for the non-`'auto'` forms so this class of bug is caught in future.

**Users:** library users who call the mutual-information functions with explicit discrete-feature indices or masks. Maintainers who need to stay compatible with upcoming NumPy releases.

**Acceptance criteria:**
- `discrete_features='auto'` behaves exactly as before.
- `discrete_features` as an index array (e.g. `[0, 2]` or `np.array([0, 2])`) marks exactly those features as discrete.
- `discrete_features` as a boolean mask of length `n_features` marks the `True` features as discrete.
- None of these inputs emits a NumPy FutureWarning or DeprecationWarning about element-wise comparison.
- The results for index-array and boolean-mask inputs that describe the same feature set are identical.

## Tech Stack
- Language: Python (version unknown)
- Key dependency: NumPy (supported version range unknown)
- Project: presumed scikit-learn (unconfirmed; see Assumptions)

## Commands
- Build: unknown
- Test: unknown (presumably a pytest invocation targeting the feature-selection tests)
- Lint: unknown
- Dev: N/A

## Project Structure
- Location of `_estimate_mi`: unknown. It is presumed to be the mutual-information module of the feature-selection package.
- Location of the existing tests for mutual information: unknown.
- New tests should go in the existing test module for the mutual-information estimators. Its path is unknown.

## Code Style
Unknown; follow the existing conventions of the surrounding module. The one constraint is that a type check must not rely on `==` against an array. The check for "is the string `'auto'`" must first establish that the value is a string, and only then compare it.

## Testing Strategy
- **Framework:** unknown (assumed pytest).
- **Unit tests, one per supported form of `discrete_features`:**
  - `'auto'`, with dense input and with sparse input if sparse input is supported (unknown)
  - Scalar `True` / `False`, if supported (Assumption 2)
  - A list of indices and an ndarray of indices
  - A boolean mask, as a list and as an ndarray
- **Equivalence test:** the index form and the mask form for the same feature set give equal results, using a fixed `random_state` if the estimator is stochastic.
- **Warning test:** each array-like form runs with NumPy FutureWarning and DeprecationWarning promoted to errors, and no warning fires.
- **Invalid-input tests:** cover only behaviour that already exists. Do not add new validation without approval; see Open Questions.
- **Coverage:** every branch in `_estimate_mi` that depends on `discrete_features` is executed by at least one test.

## Boundaries
- **Always:**
  - Preserve the existing results for `'auto'`.
  - Run the full mutual-information test module before committing.
  - Keep the change local to the `discrete_features` handling.
- **Ask first:**
  - Changing the public signature or the documented accepted types of `discrete_features`.
  - Adding new input validation or error messages for malformed masks or indices.
  - Changing the minimum NumPy version.
- **Never:**
  - Silence the NumPy warning with warning filters instead of fixing the comparison.
  - Remove or weaken existing tests.
  - Change mutual-information numerical results for already-supported inputs.

## Success Criteria
1. No code path in `_estimate_mi` compares `discrete_features` to a string with `==` when it may be an array.
2. With NumPy element-wise-comparison warnings turned into errors, calling the public MI functions succeeds for each form of `discrete_features`: `'auto'`, index list or array, and boolean mask list or array.
3. The new tests fail on the current code, at least when warnings are errors or on a NumPy version where the comparison raises, and pass after the fix.
4. Existing tests continue to pass unchanged.
5. For each supported form, the set of features treated as discrete matches the documented semantics.

## Open Questions
1. Which project, file path and NumPy version range are in scope? Is this scikit-learn's mutual-information module?
2. Is a scalar boolean (`True` / `False`) a supported value for `discrete_features`? If so, what does each value mean?
3. How should these inputs behave? Should validation be added as part of this fix or deferred?
   - A boolean mask whose length differs from `n_features`
   - Out-of-range or negative indices
   - Other strings than `'auto'`
4. Does `'auto'` resolve differently for sparse and dense `X`? Should sparse input with explicit masks or indices also be tested?
5. Do any other functions in the codebase use the same `== 'auto'` pattern on parameters that can be arrays, and are they in scope?
6. Is the estimator deterministic given `random_state`? This matters for writing exact-equality equivalence tests.
7. What are the exact build, test and lint commands for the repository?