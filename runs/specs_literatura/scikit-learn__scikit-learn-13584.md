## Summary

With `print_changed_only=True`, printing an estimator whose parameter is a NumPy array fails with a `ValueError`. Example: `LogisticRegressionCV(Cs=np.array([0.1, 1]))`. The bug is in the new `repr` when it handles vector (array-valued) parameters.

## Steps to reproduce

1. Import `sklearn`, `numpy` and `LogisticRegressionCV`.
2. Turn on changed-only printing with `sklearn.set_config(print_changed_only=True)`.
3. Create a `LogisticRegressionCV` estimator and pass a NumPy array for `Cs`, e.g. `Cs=np.array([0.1, 1])`.
4. Call `print()` on the estimator.

## Observed behavior

Printing the estimator raises a `ValueError` about the truth value of an array being ambiguous. No representation is printed.

## Expected behavior

The estimator should print without error, like it does for scalar parameter values.

## Stack trace / error output

```
ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

The original report includes only this error message, not the full traceback.

## Test case

Minimal test derived from the reproduction snippet:

```python
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegressionCV


def test_repr_print_changed_only_with_array_param():
    sklearn.set_config(print_changed_only=True)
    # Currently raises ValueError; should not raise.
    repr(LogisticRegressionCV(Cs=np.array([0.1, 1])))
```

## Code example

```python
import sklearn
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
sklearn.set_config(print_changed_only=True)
print(LogisticRegressionCV(Cs=np.array([0.1, 1])))
```

## Version and environment

Not provided in the original report. The report only says this affects the "new repr" with the `print_changed_only` setting.