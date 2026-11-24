# Spec: Expose `warm_start` in `IsolationForest.__init__()`

## Objective

`sklearn.ensemble.IsolationForest` already supports adding trees incrementally through the `warm_start` attribute it inherits from `sklearn.ensemble.BaseBagging`. Because `warm_start` is not a parameter of `IsolationForest.__init__()`, users can only find it by reading the source of both classes. The workaround is to set `est.warm_start = True` after construction and increase `n_estimators` before each later `fit`.

The goal is to make this capability public and documented, consistent with `sklearn.ensemble.BaseForest` estimators such as `RandomForestClassifier`.

**Users:** scikit-learn users who train `IsolationForest` models and want to grow the ensemble over time instead of refitting from scratch.

**User stories / acceptance criteria:**

1. As a user, I can write `IsolationForest(warm_start=True)`. The default is `False`.
2. With `warm_start=True`, if I raise `n_estimators` and call `fit` again, the existing trees are kept and only the extra trees are fitted and appended.
3. With `warm_start=False` (the default), every `fit` call builds a whole new forest, exactly as today.
4. The class docstring documents `warm_start` using the same wording as `RandomForestClassifier`:
   ```
   warm_start : bool, optional (default=False)
       When set to ``True``, reuse the solution of the previous call to fit
       and add more estimators to the ensemble, otherwise, just fit a whole
       new forest. See :term:`the Glossary <warm_start>`.
   ```
5. A test checks that warm-start fitting works.
6. Optionally, the "IsolationForest example" documentation entry mentions warm start.

## Assumptions

1. The inherited `BaseBagging` warm-start logic is correct for `IsolationForest`. Only the constructor signature, documentation and tests need to change. No new fitting logic is required.
2. `IsolationForest.__init__()` currently passes arguments to `BaseBagging.__init__()` explicitly. Exposing `warm_start` therefore means accepting it and forwarding it, rather than setting it as an attribute after the fact.
3. Edge cases inherit the `BaseBagging` behavior unchanged and are not redefined here:
   - refitting with the same `n_estimators`
   - refitting with a smaller `n_estimators` (expected to raise or warn)
4. The new parameter goes at the end of the keyword arguments so that existing positional or keyword usage still works. Placement in the signature and docstring order follows project convention (not visible in the issue).
5. The default `False` keeps current behavior, so this change is backward compatible.
6. The issue says the behavior is "in-line with `BaseForest`". That claim is the reporter's and has not been verified here.
7. The change follows the usual scikit-learn contribution conventions: a changelog/"what's new" entry and estimator-check compatibility. The exact files are unknown.

## Tech Stack

- Python, scikit-learn (`sklearn.ensemble`).
- Classes involved: `IsolationForest`, `BaseBagging`, and `BaseForest` / `RandomForestClassifier` (for consistency reference).
- Python version, scikit-learn version/branch, NumPy/SciPy versions: **unknown**.

## Commands

All unknown. The issue gives no repository access and no commands.

```
Build:      unknown
Test:       unknown (presumably a pytest invocation targeting the IsolationForest test module — exact command unknown)
Lint:       unknown
Docs build: unknown
```

## Project Structure

Not visible in the issue. Locations that must be identified:

```
<unknown>  → module defining IsolationForest (sklearn.ensemble)
<unknown>  → module defining BaseBagging (sklearn.ensemble)
<unknown>  → IsolationForest test module
<unknown>  → "IsolationForest example" documentation entry
<unknown>  → changelog / what's-new file (if required)
<unknown>  → Glossary entry for `warm_start` (referenced via :term:)
```

## Code Style

- Follow existing scikit-learn conventions. The only concrete reference available is the numpydoc-style parameter block above, which must be copied verbatim from `RandomForestClassifier`'s docstring.
- Constructor parameters are stored unchanged on `self`, as required by the scikit-learn estimator API (`get_params` / `set_params`).
- Other formatting and lint rules: **unknown** (to be taken from the repository).

## Testing Strategy

- **Framework:** presumably pytest, which is the scikit-learn convention. The test location is unknown.
- **Required test (unit level):** warm-start behavior of `IsolationForest`.
  - Fit with `warm_start=True` and some `n_estimators=N1`. Then raise `n_estimators` to `N2 > N1` and fit again on the same data.
  - Assert the ensemble has `N2` estimators.
  - Assert the first `N1` estimators are the same objects as before the second fit, meaning they were reused rather than refitted.
- **Recommended additional checks:**
  - With `warm_start=False`, a second `fit` replaces the estimators.
  - `get_params()` includes `warm_start`.
  - The estimator still passes the common estimator checks.
- **Regression:** the existing `IsolationForest` tests must pass unchanged.
- **Coverage target:** unknown. Follow project norms.

## Boundaries

- **Always:**
  - Keep the default `warm_start=False`.
  - Reuse the inherited `BaseBagging` warm-start logic.
  - Use the docstring wording given in the issue.
  - Run the existing `IsolationForest` tests plus the new test.
- **Ask first:**
  - Changing the `BaseBagging` warm-start semantics.
  - Changing parameter order in a way that could break positional calls.
  - Reworking the IsolationForest example beyond a short mention.
  - Adding deprecations.
- **Never:**
  - Change the default behavior of `fit`.
  - Alter `IsolationForest` scoring or prediction logic.
  - Remove or weaken existing tests.
  - Add new dependencies.

## Success Criteria

- [ ] `IsolationForest(warm_start=True)` constructs without error, and `get_params()["warm_start"]` is `True`. The default is `False`.
- [ ] With `warm_start=True`, increasing `n_estimators` from N1 to N2 and refitting gives `len(estimators_) == N2`, and the first N1 estimators are identical (same objects) to those from the previous fit.
- [ ] With `warm_start=False`, refitting produces a newly built forest.
- [ ] The `IsolationForest` docstring contains the `warm_start` entry with the specified wording and Glossary reference.
- [ ] The new test exists and passes, and all existing `IsolationForest` tests still pass.
- [ ] (Optional) The IsolationForest example documentation mentions `warm_start`.
- [ ] (If required by the project) A changelog entry exists.

## Open Questions

1. Should the IsolationForest example documentation be updated in this change, or left out? The issue says "possibly".
2. Where exactly should `warm_start` go in the `__init__` signature and docstring? This matters for positional-argument compatibility.
3. Is a changelog / what's-new entry required, and in which file and version section?
4. What should happen when `n_estimators` is not increased (equal or smaller) on a warm-start refit? Is the inherited `BaseBagging` behavior (warning/error) acceptable for `IsolationForest`, and should the test cover it?
5. Should the test also check that refitting with warm start on *different* data is allowed or meaningful? Isolation forest computes the `offset_`/threshold from training data, and it is unclear how that should interact with an incremental fit.
6. What are the target scikit-learn version/branch and the exact test, lint and docs-build commands?