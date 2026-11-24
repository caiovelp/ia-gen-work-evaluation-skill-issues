## Summary

`FeatureUnion` (created with `make_union`) raises `ValueError: Length mismatch` when `set_config(transform_output="pandas")` is enabled and the union contains a custom transformer whose `transform` aggregates the data, so it returns fewer rows than the input. The same code works with the default (`numpy`) transform output.

## Steps to reproduce

1. Create a DataFrame with an hourly `DatetimeIndex` from 2020-01-01 to 2020-01-05 (`inclusive="left"`, so 96 rows). Give it a `value` column (all `10`) and a `date` column (`index.date`).
2. Define a custom transformer (`BaseEstimator`, `TransformerMixin`) whose `transform` returns `X["value"].groupby(X["date"]).sum()`. This aggregates the 96 hourly rows into 4 daily rows.
3. Call `set_config(transform_output="default")` and run `make_union(MyTransformer()).fit_transform(data)`. This works.
4. Call `set_config(transform_output="pandas")` and run `make_union(MyTransformer()).fit_transform(data)` again. This raises a `ValueError`.

## Observed behavior

With `transform_output="pandas"`, `fit_transform` on the `FeatureUnion` fails with:

```
ValueError: Length mismatch: Expected axis has 4 elements, new values have 96 elements
```

The error is raised in `sklearn/utils/_set_output.py`, in `_wrap_in_pandas_container`, at `data_to_wrap.index = index`. At that point the index of the original input (96 elements) is assigned to the transformer's aggregated output (4 elements).

With `transform_output="default"`, the same call completes without error. The original report does not include its printed output.

## Expected behavior

No error should be raised when using `pandas` transform output, just as with the default `numpy` output.

## Stack trace / error output

```
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[5], line 25
     23 # This does not work.
     24 set_config(transform_output="pandas")
---> 25 print(make_union(MyTransformer()).fit_transform(data))

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/sklearn/utils/_set_output.py:150, in _wrap_method_output.<locals>.wrapped(self, X, *args, **kwargs)
    143 if isinstance(data_to_wrap, tuple):
    144     # only wrap the first output for cross decomposition
    145     return (
    146         _wrap_data_with_container(method, data_to_wrap[0], X, self),
    147         *data_to_wrap[1:],
    148     )
--> 150 return _wrap_data_with_container(method, data_to_wrap, X, self)

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/sklearn/utils/_set_output.py:130, in _wrap_data_with_container(method, data_to_wrap, original_input, estimator)
    127     return data_to_wrap
    129 # dense_config == "pandas"
--> 130 return _wrap_in_pandas_container(
    131     data_to_wrap=data_to_wrap,
    132     index=getattr(original_input, "index", None),
    133     columns=estimator.get_feature_names_out,
    134 )

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/sklearn/utils/_set_output.py:59, in _wrap_in_pandas_container(data_to_wrap, columns, index)
     57         data_to_wrap.columns = columns
     58     if index is not None:
---> 59         data_to_wrap.index = index
     60     return data_to_wrap
     62 return pd.DataFrame(data_to_wrap, index=index, columns=columns)

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/pandas/core/generic.py:5588, in NDFrame.__setattr__(self, name, value)
   5586 try:
   5587     object.__getattribute__(self, name)
-> 5588     return object.__setattr__(self, name, value)
   5589 except AttributeError:
   5590     pass

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/pandas/_libs/properties.pyx:70, in pandas._libs.properties.AxisProperty.__set__()

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/pandas/core/generic.py:769, in NDFrame._set_axis(self, axis, labels)
    767 def _set_axis(self, axis: int, labels: Index) -> None:
    768     labels = ensure_index(labels)
--> 769     self._mgr.set_axis(axis, labels)
    770     self._clear_item_cache()

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/pandas/core/internals/managers.py:214, in BaseBlockManager.set_axis(self, axis, new_labels)
    212 def set_axis(self, axis: int, new_labels: Index) -> None:
    213     # Caller is responsible for ensuring we have an Index object.
--> 214     self._validate_set_axis(axis, new_labels)
    215     self.axes[axis] = new_labels

File ~/.local/share/virtualenvs/3e_VBrf2/lib/python3.10/site-packages/pandas/core/internals/base.py:69, in DataManager._validate_set_axis(self, axis, new_labels)
     66     pass
     68 elif new_len != old_len:
---> 69     raise ValueError(
     70         f"Length mismatch: Expected axis has {old_len} elements, new "
     71         f"values have {new_len} elements"
     72     )

ValueError: Length mismatch: Expected axis has 4 elements, new values have 96 elements
```

## Test case

This minimal test is derived from the reproduction snippet in the report. It fails with the `ValueError` above under the reported environment.

```python
import pandas as pd
from sklearn import config_context
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_union


class MyTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None, **kwargs):
        return self

    def transform(self, X, y=None):
        return X["value"].groupby(X["date"]).sum()


def _make_data():
    index = pd.date_range(
        start="2020-01-01", end="2020-01-05", inclusive="left", freq="H"
    )
    data = pd.DataFrame(index=index, data=[10] * len(index), columns=["value"])
    data["date"] = index.date
    return data


def test_feature_union_aggregating_transformer_default_output():
    # Reported to work
    with config_context(transform_output="default"):
        make_union(MyTransformer()).fit_transform(_make_data())


def test_feature_union_aggregating_transformer_pandas_output():
    # Reported to raise ValueError: Length mismatch
    with config_context(transform_output="pandas"):
        make_union(MyTransformer()).fit_transform(_make_data())
```

## Code example

Original reproduction script from the report:

```python
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import set_config
from sklearn.pipeline import make_union

index = pd.date_range(start="2020-01-01", end="2020-01-05", inclusive="left", freq="H")
data = pd.DataFrame(index=index, data=[10] * len(index), columns=["value"])
data["date"] = index.date


class MyTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: pd.Series | None = None, **kwargs):
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series | None = None) -> pd.DataFrame:
        return X["value"].groupby(X["date"]).sum()


# This works.
set_config(transform_output="default")
print(make_union(MyTransformer()).fit_transform(data))

# This does not work.
set_config(transform_output="pandas")
print(make_union(MyTransformer()).fit_transform(data))
```

## Version and environment

- **scikit-learn:** 1.2.1
- **pandas:** 1.4.4
- **numpy:** 1.23.5
- **scipy:** 1.10.1
- **joblib:** 1.2.0
- **threadpoolctl:** 3.1.0
- **matplotlib:** 3.7.0
- **pip:** 22.3.1
- **setuptools:** 67.3.2
- **Cython:** None
- **Python:** 3.10.6 (main, Aug 30 2022, 05:11:14) [Clang 13.0.0 (clang-1300.0.29.30)]
- **OS / machine:** macOS-11.3-x86_64-i386-64bit
- **Built with OpenMP:** True
- **threadpoolctl info:**
  - numpy: OpenBLAS 0.3.20 (pthreads, Haswell, 4 threads)
  - sklearn: libomp, OpenMP (8 threads)
  - scipy: OpenBLAS 0.3.18 (pthreads, Haswell, 4 threads)
- The error was observed in an interactive (Jupyter/IPython-style) cell, running in a virtualenv.