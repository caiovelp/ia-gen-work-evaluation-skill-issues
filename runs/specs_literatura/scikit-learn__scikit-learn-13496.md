## Summary
Expose the `warm_start` parameter in `sklearn.ensemble.IsolationForest`.

## Description
`sklearn.ensemble.IsolationForest` already supports adding new trees incrementally through the `warm_start` parameter. It inherits this parameter from its parent class, `sklearn.ensemble.BaseBagging`.

The parameter is not exposed in `IsolationForest.__init__()`, but it still works. To use it, a user has to:
1. Set `warm_start` to `True` after the estimator has been initialized.
2. Increase `n_estimators` before each subsequent call to `fit`.

This behavior appears to match that of `sklearn.ensemble.BaseForest`, which is the base for estimators such as `sklearn.ensemble.RandomForestClassifier`. The request is to make this existing capability an explicit, documented and tested part of the `IsolationForest` API.

## Product version
Not provided in the original request.

## Rationale
- **The feature is hard to discover.** Because `warm_start` is not exposed in `__init__()` or documented, users do not know it exists. The reporter only found out that it works by reading the source code of both `IsolationForest` and `BaseBagging`.
- **The API is inconsistent.** Comparable ensemble estimators, such as `RandomForestClassifier`, expose and document `warm_start`. `IsolationForest` already behaves the same way but does not offer the parameter openly.
- **The current workaround is awkward.** Changing an attribute after initialization relies on undocumented, inherited behavior, so it is not an easy or clear way to use the feature.

## Use case or scenario
A user wants to grow an `IsolationForest` step by step, adding more trees to an already-fitted ensemble instead of retraining the whole forest from scratch. Today this requires setting `warm_start=True` after construction and increasing `n_estimators` on every iteration, and finding this out requires reading the source code.

## Possible solution
The original request suggests the following:
- Expose `warm_start` in `IsolationForest.__init__()`, with a default of `False`.
- Document it the same way it is documented for `RandomForestClassifier`:
  ```py
      warm_start : bool, optional (default=False)
          When set to ``True``, reuse the solution of the previous call to fit
          and add more estimators to the ensemble, otherwise, just fit a whole
          new forest. See :term:`the Glossary <warm_start>`.
  ```
- Add a test to make sure `warm_start` works properly.
- Possibly mention it in the "IsolationForest example" documentation entry.