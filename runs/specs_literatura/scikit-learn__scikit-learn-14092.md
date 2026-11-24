## Summary

`NeighborhoodComponentsAnalysis` (NCA) checks that its parameters are of specific Python types. These checks are too strict and fail inside `GridSearchCV` because of how parameter grids are commonly written:

- `tol`: the value `1` is an `int`, not a `float`, so it is rejected.
- `n_components`: values from `np.arange(1, 10)` are `np.int64`, not `int`, so they are rejected.

## Steps to reproduce

1. Generate random data: `X` of shape `(100, 10)` and binary labels `y` of length 100.
2. Build a `Pipeline` with `NeighborhoodComponentsAnalysis()` (step name `'nca'`) followed by `KNeighborsClassifier()` (step name `'knn'`).
3. Define a parameter grid:
   - `'nca__tol': [0.1, 0.5, 1]`
   - `'nca__n_components': np.arange(1, 10)`
4. Create `GridSearchCV(estimator=pipe, param_grid=params, error_score='raise')`.
5. Call `gs.fit(X, y)`.

## Observed behavior

`gs.fit(X, y)` fails. NCA's parameter validation rejects:

- `tol=1` because it is not a `float`.
- `n_components` values of type `np.int64` because they are not `int`.

## Expected behavior

The grid search should run without error. An integer value such as `1` should be accepted for `tol`, and NumPy integer types such as `np.int64` should be accepted for `n_components`.

## Stack trace / error output

Not provided in the original report.

## Test case

```python
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.neighbors import KNeighborsClassifier


def test_nca_in_gridsearch_accepts_int_tol_and_numpy_int_n_components():
    X = np.random.random_sample((100, 10))
    y = np.random.randint(2, size=100)

    pipe = Pipeline([('nca', NeighborhoodComponentsAnalysis()),
                     ('knn', KNeighborsClassifier())])

    params = {'nca__tol': [0.1, 0.5, 1],
              'nca__n_components': np.arange(1, 10)}

    gs = GridSearchCV(estimator=pipe, param_grid=params, error_score='raise')
    gs.fit(X, y)  # should not raise
```

## Code example

Original reproduction snippet from the report:

```python
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.neighbors import KNeighborsClassifier

X = np.random.random_sample((100, 10))
y = np.random.randint(2, size=100)

nca = NeighborhoodComponentsAnalysis()
knn = KNeighborsClassifier()

pipe = Pipeline([('nca', nca),
                 ('knn', knn)])

params = {'nca__tol': [0.1, 0.5, 1],
          'nca__n_components': np.arange(1, 10)}

gs = GridSearchCV(estimator=pipe, param_grid=params, error_score='raise')
gs.fit(X, y)
```

## Version and environment

Not provided in the original report.