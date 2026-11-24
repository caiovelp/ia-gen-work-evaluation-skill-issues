## Summary

`GaussianMixture.fit_predict(X)` and `GaussianMixture.predict(X)` often return different labels when `n_init` is greater than 1. With the default `n_init`, the two methods agree. The existing unit test `test_gaussian_mixture_fit_predict` does not catch this because it does not set `n_init`.

## Steps to reproduce

1. Generate random data: `X = numpy.random.randn(1000, 5)`.
2. Create `GaussianMixture(n_components=5)` with the default `n_init`.
3. Call `c1 = gm.fit_predict(X)`, then `c2 = gm.predict(X)`.
4. Compare with `assert_array_equal(c1, c2)`. This passes.
5. Create `GaussianMixture(n_components=5, n_init=5)`.
6. Call `c1 = gm.fit_predict(X)`, then `c2 = gm.predict(X)` on the same `X`.
7. Compare with `assert_array_equal(c1, c2)`. This fails.

## Observed behavior

With `n_init=5`, the labels from `fit_predict(X)` and the labels from a later `predict(X)` on the same fitted model and data differ. In the reported run, 88.6% of the labels did not match, so `assert_array_equal` raised an `AssertionError`. The reporter says the results are "often" different, not always.

## Expected behavior

`fit_predict(X)` and `predict(X)` should return identical labels for the same data, whatever the value of `n_init`. The script should print:

```
no n_init
n_init=5
```

and raise no exception.

## Stack trace / error output

```
no n_init
n_init=5
Traceback (most recent call last):
  File "test_gm.py", line 17, in <module>
    assert_array_equal(c1,c2)
  File "/home/scott/.local/lib/python2.7/site-packages/numpy/testing/_private/utils.py", line 872, in assert_array_equal
    verbose=verbose, header='Arrays are not equal')
  File "/home/scott/.local/lib/python2.7/site-packages/numpy/testing/_private/utils.py", line 796, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(mismatch 88.6%)
 x: array([4, 0, 1, 1, 1, 3, 3, 4, 4, 2, 0, 0, 1, 2, 0, 2, 0, 1, 3, 1, 1, 3,
       2, 1, 0, 2, 1, 0, 2, 0, 3, 1, 2, 3, 3, 1, 0, 2, 2, 0, 3, 0, 2, 0,
       4, 2, 3, 0, 4, 2, 4, 1, 0, 2, 2, 1, 3, 2, 1, 4, 0, 2, 2, 1, 1, 2,...
 y: array([4, 1, 0, 2, 2, 1, 1, 4, 4, 0, 4, 1, 0, 3, 1, 0, 2, 2, 1, 2, 0, 0,
       1, 0, 4, 1, 0, 4, 0, 1, 1, 2, 3, 1, 4, 0, 1, 4, 4, 4, 0, 1, 0, 2,
       4, 1, 1, 2, 4, 3, 4, 0, 2, 3, 2, 3, 0, 0, 2, 3, 3, 3, 3, 0, 3, 2,...
```

## Test case

This minimal test is derived from the reproduction snippet. It fails on the reported version.

```python
import numpy
from sklearn.mixture import GaussianMixture
from sklearn.utils.testing import assert_array_equal

def test_gaussian_mixture_fit_predict_n_init():
    X = numpy.random.randn(1000, 5)
    gm = GaussianMixture(n_components=5, n_init=5)
    c1 = gm.fit_predict(X)
    c2 = gm.predict(X)
    assert_array_equal(c1, c2)
```

The data is random and no seed is set, and the reporter says the mismatch happens "often". The test may therefore not fail on every run.

## Code example

This is the original reproduction script (Python 2 syntax), as given in the report:

```python
from sklearn.mixture import GaussianMixture
from sklearn.utils.testing import assert_array_equal
import numpy
X = numpy.random.randn(1000,5)
print 'no n_init'
gm = GaussianMixture(n_components=5)
c1 = gm.fit_predict(X)
c2 = gm.predict(X)
assert_array_equal(c1,c2)
print 'n_init=5'
gm = GaussianMixture(n_components=5, n_init=5)
c1 = gm.fit_predict(X)
c2 = gm.predict(X)
assert_array_equal(c1,c2)
```

## Version and environment

```
System:
    python: 2.7.15rc1 (default, Nov 12 2018, 14:31:15)  [GCC 7.3.0]
   machine: Linux-4.15.0-43-generic-x86_64-with-Ubuntu-18.04-bionic
executable: /usr/bin/python

BLAS:
    macros: HAVE_CBLAS=None, NO_ATLAS_INFO=-1
cblas_libs: cblas
  lib_dirs: /usr/lib/x86_64-linux-gnu

Python deps:
    Cython: 0.28.5
     scipy: 1.2.0
setuptools: 39.0.1
       pip: 19.0.1
     numpy: 1.16.0
    pandas: 0.23.1
   sklearn: 0.20.2
```