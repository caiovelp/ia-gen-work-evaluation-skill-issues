## Summary

`ColumnTransformer` fails when it contains a transformer that applies to an empty list of columns and the output is set to pandas (`set_output(transform="pandas")`). Fitting raises `ValueError: Length mismatch: Expected axis has 3 elements, new values have 0 elements`.

The reporter notes the error goes away in either of these cases:
- `.set_output(transform="pandas")` is removed.
- The transformer with zero features (the `("categorical", 'passthrough', [])` step) is removed.

## Steps to reproduce

1. Create a pandas DataFrame `X` with columns `a`, `b`, `c` and `d`, and a target `y`.
2. Build a `ColumnTransformer` with `remainder='drop'` and two transformers:
   - `'categorical'`: `'passthrough'` applied to an empty column list (`[]`).
   - `'numerical'`: a `Pipeline` of `RobustScaler()` followed by `SimpleImputer(strategy="median")`, applied to `["a", "b", "c"]`.
3. Put the `ColumnTransformer` in a `Pipeline` as the `"preprocessing"` step, followed by an `LGBMClassifier` as the `"classifier"` step.
4. Call `.set_output(transform="pandas")` on the pipeline.
5. Call `pipeline.fit(X, y)`.
6. A `ValueError` is raised.

## Observed behavior

`pipeline.fit(X, y)` raises:

```
ValueError: Length mismatch: Expected axis has 3 elements, new values have 0 elements
```

The error is raised in `ColumnTransformer._hstack` (`sklearn/compose/_column_transformer.py`, line 862) when it runs `output.columns = names_out`.

The reporter's analysis is that steps with 0 features are not fitted. As a result, they do not appear in `self._iter(fitted=True)` (`_column_transformer.py` line 856). This breaks the input passed to `_add_prefix_for_feature_names_out` (line 859).

## Expected behavior

The step with no features should be ignored. Fitting should succeed with pandas output, just as it does without `set_output(transform="pandas")`.

## Stack trace / error output

```pytb
Traceback (most recent call last):
  File "/home/philippe/workspace/script.py", line 22, in <module>
    pipeline.fit(X, y)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 402, in fit
    Xt = self._fit(X, y, **fit_params_steps)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 360, in _fit
    X, fitted_transformer = fit_transform_one_cached(
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/joblib/memory.py", line 349, in __call__
    return self.func(*args, **kwargs)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 894, in _fit_transform_one
    res = transformer.fit_transform(X, y, **fit_params)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/utils/_set_output.py", line 142, in wrapped
    data_to_wrap = f(self, X, *args, **kwargs)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/compose/_column_transformer.py", line 750, in fit_transform
    return self._hstack(list(Xs))
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/compose/_column_transformer.py", line 862, in _hstack
    output.columns = names_out
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/generic.py", line 5596, in __setattr__
    return object.__setattr__(self, name, value)
  File "pandas/_libs/properties.pyx", line 70, in pandas._libs.properties.AxisProperty.__set__
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/generic.py", line 769, in _set_axis
    self._mgr.set_axis(axis, labels)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/internals/managers.py", line 214, in set_axis
    self._validate_set_axis(axis, new_labels)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/internals/base.py", line 69, in _validate_set_axis
    raise ValueError(
ValueError: Length mismatch: Expected axis has 3 elements, new values have 0 elements

Process finished with exit code 1
```

## Test case

This test is derived directly from the reproduction snippet in the report. It should pass once the bug is resolved. It currently fails with the `ValueError` shown above.

```python
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


def test_column_transformer_pandas_output_with_empty_feature_transformer():
    X = pd.DataFrame(data=[[1.0, 2.0, 3.0, 4.0], [4, 2, 2, 5]],
                     columns=["a", "b", "c", "d"])
    y = np.array([0, 1])
    categorical_features = []
    numerical_features = ["a", "b", "c"]
    model_preprocessing = ("preprocessing",
                           ColumnTransformer([
                               ('categorical', 'passthrough', categorical_features),
                               ('numerical', Pipeline([("scaler", RobustScaler()),
                                                       ("imputer", SimpleImputer(strategy="median"))
                                                       ]), numerical_features),
                           ], remainder='drop'))
    pipeline = Pipeline([model_preprocessing, ("classifier", LGBMClassifier())]).set_output(transform="pandas")
    # Expected: the step with no features is ignored and fit succeeds.
    pipeline.fit(X, y)
```

## Code example

The reporter's original reproduction script:

```python
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

X = pd.DataFrame(data=[[1.0, 2.0, 3.0, 4.0], [4, 2, 2, 5]],
                 columns=["a", "b", "c", "d"])
y = np.array([0, 1])
categorical_features = []
numerical_features = ["a", "b", "c"]
model_preprocessing = ("preprocessing",
                       ColumnTransformer([
                           ('categorical', 'passthrough', categorical_features),
                           ('numerical', Pipeline([("scaler", RobustScaler()),
                                                   ("imputer", SimpleImputer(strategy="median"))
                                                   ]), numerical_features),
                       ], remainder='drop'))
pipeline = Pipeline([model_preprocessing, ("classifier", LGBMClassifier())]).set_output(transform="pandas")
pipeline.fit(X, y)
```

## Version and environment

```shell
System:
    python: 3.9.15 (main, Nov 24 2022, 14:31:59)  [GCC 11.2.0]
executable: /home/philippe/.anaconda3/envs/strategy-training/bin/python
   machine: Linux-5.15.0-57-generic-x86_64-with-glibc2.31

Python dependencies:
      sklearn: 1.2.0
          pip: 22.2.2
   setuptools: 62.3.2
        numpy: 1.23.5
        scipy: 1.9.3
       Cython: None
       pandas: 1.4.1
   matplotlib: 3.6.3
       joblib: 1.2.0
threadpoolctl: 3.1.0

Built with OpenMP: True

threadpoolctl info:
       user_api: openmp
   internal_api: openmp
         prefix: libgomp
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scikit_learn.libs/libgomp-a34b3233.so.1.0.0
        version: None
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/numpy.libs/libopenblas64_p-r0-742d56dc.3.20.so
        version: 0.3.20
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scipy.libs/libopenblasp-r0-41284840.3.18.so
        version: 0.3.18
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12
```

The LightGBM version is not provided in the original report.