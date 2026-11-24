## Summary
Support nullable pandas dtypes (`"Int64"`, `"Float64"`, `"boolean"`) in `sklearn.utils.multiclass.unique_labels`.

## Description
Passing pandas Series with nullable dtypes (`"Int64"`, `"Float64"`, `"boolean"`) to `unique_labels` raises an error. When converted to numpy arrays, these dtypes become `object` dtype. As a result, `unique_labels` sees the inputs as having mixed target types and raises:

```
ValueError: Mix type of y not allowed, got types {'binary', 'unknown'}
```

Reproduction:

```py
import pandas as pd
import pytest
from sklearn.utils.multiclass import unique_labels

for dtype in ["Int64", "Float64", "boolean"]:
    y_true = pd.Series([1, 0, 0, 1, 0, 1, 1, 0, 1], dtype=dtype)
    y_predicted = pd.Series([0, 0, 1, 1, 0, 1, 1, 1, 1], dtype="int64")

    with pytest.raises(ValueError, match="Mix type of y not allowed, got types"):
        unique_labels(y_true, y_predicted)
```

The same data with the non-nullable equivalents (`int64`, `float64`, `bool`) works without error:

```python
import pandas as pd
from sklearn.utils.multiclass import unique_labels

for dtype in ["int64", "float64", "bool"]:
    y_true = pd.Series([1, 0, 0, 1, 0, 1, 1, 0, 1], dtype=dtype)
    y_predicted = pd.Series([0, 0, 1, 1, 0, 1, 1, 1, 1], dtype="int64")

    unique_labels(y_true, y_predicted)
```

## Product version
scikit-learn 1.2.1 (version used for the reproduction). The pandas version is not provided in the original request.

## Rationale
The nullable pandas dtypes hold the same labels as `int64`, `float64` and `bool`, but they are handled differently: the nullable versions fail, and the standard versions work. Users must currently convert their data manually before calling `unique_labels`. The proposed change would remove this extra step and make the behavior consistent across the equivalent dtypes.

## Use case or scenario
A user has target labels stored in a pandas Series with a nullable dtype (`"Int64"`, `"Float64"` or `"boolean"`). The predictions are stored in a standard `int64` Series. The user calls `unique_labels(y_true, y_predicted)` to get the set of labels and expects it to work as it does with non-nullable dtypes. Instead, the call raises a `ValueError`.

The reporter's current workaround is to convert the data to numpy arrays with a corresponding dtype that works before passing it to `unique_labels`.

## Possible solution
`unique_labels` should handle the nullable pandas dtypes `"Int64"`, `"Float64"` and `"boolean"` the same way it handles `int64`, `float64` and `bool`. That is, it should raise no error and return the unique labels.