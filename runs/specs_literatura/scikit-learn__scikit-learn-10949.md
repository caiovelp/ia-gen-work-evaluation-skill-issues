## Summary

`sklearn.utils.validation.check_array` emits no warning when `warn_on_dtype=True` and the input is a pandas `DataFrame` whose dtype is converted (for example, `object` to `float64`). The `warn_on_dtype` option appears to have no effect for `DataFrame` input.

## Steps to reproduce

1. Import `check_array` from `sklearn.utils.validation` and import `pandas`.
2. Create a `DataFrame` with `dtype=object`: `pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)`.
3. Call `check_array(df, warn_on_dtype=True)`.
4. Check whether a `DataConversionWarning` is emitted.

## Observed behavior

No warning is emitted.

## Expected behavior

A `DataConversionWarning` should be emitted because the input dtype `object` is converted to `float64`:

```
DataConversionWarning: Data with input dtype object was converted to float64.
```

## Stack trace / error output

Not provided in the original report. No error occurs. The issue is that the expected warning is missing.

## Test case

This minimal test is derived from the reproduction snippet in the report:

```python
import warnings

import pandas as pd
from sklearn.utils.validation import check_array


def test_warn_on_dtype_with_dataframe():
    df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        check_array(df, warn_on_dtype=True)
    messages = [str(w.message) for w in record
                if w.category.__name__ == "DataConversionWarning"]
    assert any("Data with input dtype object was converted to float64" in m
               for m in messages)
```

## Code example

```python
from sklearn.utils.validation import check_array
import pandas as pd
df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)
checked = check_array(df, warn_on_dtype=True)
```

## Version and environment

- Platform: Linux-4.4.0-116-generic-x86_64-with-debian-stretch-sid
- Python: 3.6.3 | Anaconda, Inc. | (default, Nov 3 2017, 19:19:16) [GCC 7.2.0]
- NumPy: 1.13.1
- SciPy: 0.19.1
- Scikit-Learn: 0.20.dev0
- Pandas: 0.21.0