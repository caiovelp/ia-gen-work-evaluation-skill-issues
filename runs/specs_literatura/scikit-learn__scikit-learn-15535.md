## Summary

Regression in the input validation of clustering metrics. `mutual_info_score` from `sklearn.metrics.cluster` raises `ValueError: could not convert string to float` when given string labels in an array of `object` dtype. The same labels as a plain NumPy string array work, but emit a warning. According to the reporter, both cases worked without a warning in scikit-learn 0.21.1.

## Steps to reproduce

1. Import `mutual_info_score` from `sklearn.metrics.cluster` and import `numpy`.
2. Create an array of string labels with `object` dtype: `x = np.random.choice(['a', 'b'], size=20).astype(object)`.
3. Call `mutual_info_score(x, x)`. A `ValueError` is raised.
4. For comparison, create the same labels without converting to `object` dtype: `x = np.random.choice(['a', 'b'], size=20)`.
5. Call `mutual_info_score(x, x)`. The call succeeds but emits a warning.

## Observed behavior

- With string labels of `object` dtype, `mutual_info_score` raises `ValueError: could not convert string to float: 'b'`.
- With string labels of NumPy string dtype (no `.astype(object)`), `mutual_info_score` works but emits a warning. The original report does not give the warning text.

## Expected behavior

`mutual_info_score` should accept string labels in both cases (`object` dtype and NumPy string dtype) without an error and without a warning. This matches the behavior the reporter saw in scikit-learn 0.21.1.

## Stack trace / error output

```
ValueError: could not convert string to float: 'b'
```

The original report does not include a full stack trace or the text of the warning from the second case.

## Test case

Minimal test derived from the report:

```python
import numpy as np
from sklearn.metrics.cluster import mutual_info_score

# Case 1: object dtype string labels -> currently raises ValueError
x = np.random.choice(['a', 'b'], size=20).astype(object)
mutual_info_score(x, x)  # expected: no error, no warning

# Case 2: NumPy string dtype labels -> currently works but emits a warning
x = np.random.choice(['a', 'b'], size=20)
mutual_info_score(x, x)  # expected: no warning
```

## Code example

From the original report (the second snippet was edited by @ogrisel to remove `.astype(object)`):

```python
from sklearn.metrics.cluster import mutual_info_score
import numpy as np

x = np.random.choice(['a', 'b'], size=20).astype(object)
mutual_info_score(x, x)
```

```python
x = np.random.choice(['a', 'b'], size=20)
mutual_info_score(x, x)
```

## Version and environment

- Last known working version: scikit-learn 0.21.1 (worked without a warning).
- Affected version: Not provided in the original report.
- NumPy version, Python version and OS: Not provided in the original report.