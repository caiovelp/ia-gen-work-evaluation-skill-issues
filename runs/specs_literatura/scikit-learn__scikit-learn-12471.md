## Summary

`OneHotEncoder` with `handle_unknown='ignore'` raises a `ValueError` in `transform` when the categories are strings held in a NumPy array (not object dtype). The reporter explains that during `transform`, unknown entries are replaced with `OneHotEncoder.categories_[i][0]`, the first category in alphabetical order from `fit`. If that category is longer than the fixed-width strings in the array being transformed, it gets truncated (`'11111111'` becomes `'111111'`). The truncated value is then treated as a previously unseen label, which raises the error.

The reporter notes that the issue does not occur when the input is a list of lists, because it is then treated as an array of objects.

## Steps to reproduce

1. Create a training array of strings as a NumPy array (not a list of lists), where the alphabetically first category is a long string:
   `np.array(['22', '333', '4444', '11111111']).reshape((-1, 1))`
2. Create a test array of strings with shorter maximum length than that first category, containing one unknown value and one known value:
   `np.array(['55555', '22']).reshape((-1, 1))`
3. Create `OneHotEncoder(dtype=bool, handle_unknown='ignore')`.
4. Call `fit` with the training array.
5. Call `transform` with the test array.

## Observed behavior

`transform` raises a `ValueError` stating that the input contains a previously unseen label, `'111111'`. This is a truncated version of the category `'11111111'`.

## Expected behavior

`transform` should return a 2x4 sparse matrix that is `False` everywhere except at position (1, 1), which corresponds to the known value `'22'`. The unknown value `'55555'` should be ignored.

## Stack trace / error output

```
ValueError: y contains previously unseen labels: ['111111']
```

The full stack trace was not provided in the original report.

## Test case

Minimal test derived from the reproduction snippet and the stated expected result:

```python
import numpy as np
from sklearn.preprocessing import OneHotEncoder


def test_one_hot_encoder_handle_unknown_strings():
    train = np.array(['22', '333', '4444', '11111111']).reshape((-1, 1))
    test = np.array(['55555', '22']).reshape((-1, 1))

    ohe = OneHotEncoder(dtype=bool, handle_unknown='ignore')
    ohe.fit(train)
    enc_test = ohe.transform(test)  # currently raises ValueError

    expected = np.zeros((2, 4), dtype=bool)
    expected[1, 1] = True
    assert enc_test.shape == (2, 4)
    assert np.array_equal(enc_test.toarray(), expected)
```

## Code example

```python
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# It needs to be numpy arrays, the error does not appear
# if you have lists of lists because it gets treated like an array of objects.
train = np.array(['22', '333', '4444', '11111111']).reshape((-1, 1))
test = np.array(['55555', '22']).reshape((-1, 1))

ohe = OneHotEncoder(dtype=bool, handle_unknown='ignore')

ohe.fit(train)
enc_test = ohe.transform(test)
```

## Version and environment

```
System:
    python: 2.7.12 (default, Dec  4 2017, 14:50:18)  [GCC 5.4.0 20160609]
   machine: Linux-4.4.0-138-generic-x86_64-with-Ubuntu-16.04-xenial
executable: /usr/bin/python

BLAS:
    macros: HAVE_CBLAS=None
cblas_libs: openblas, openblas
  lib_dirs: /usr/lib

Python deps:
    Cython: 0.25.2
     scipy: 0.18.1
setuptools: 36.7.0
       pip: 9.0.1
     numpy: 1.15.2
    pandas: 0.19.1
   sklearn: 0.21.dev0
```