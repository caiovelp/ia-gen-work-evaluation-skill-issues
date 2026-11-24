## Summary
Pipeline should implement `__len__`

## Description
`Pipeline` now supports indexing, but it does not implement `__len__`. As a result, calling `len(pipe)` on a `Pipeline` instance fails, and so does the expression `pipe[:len(pipe)]`.

Steps to reproduce:

```python
from sklearn import svm
from sklearn.datasets import samples_generator
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.pipeline import Pipeline

# generate some data to play with
X, y = samples_generator.make_classification(
    n_informative=5, n_redundant=0, random_state=42)

anova_filter = SelectKBest(f_regression, k=5)
clf = svm.SVC(kernel='linear')
pipe = Pipeline([('anova', anova_filter), ('svc', clf)])

len(pipe)
```

**Actual behavior:** `len(pipe)` raises an error. The exact error message is not given in the original request.

**Expected behavior:** `len(pipe)` returns the number of steps in the pipeline. In this example, that is 2.

## Product version
- scikit-learn: 0.21.dev0
- Python: 3.6.7 (conda-forge, Feb 19 2019, GCC 4.2.1 Compatible Clang 4.0.1)
- Platform: Darwin-18.2.0-x86_64-i386-64bit
- NumPy: 1.16.2
- SciPy: 1.2.1
- Cython: 0.29.6
- pandas: 0.24.1
- pip: 19.0.3
- setuptools: 40.8.0
- BLAS: openblas (HAVE_CBLAS=None)

## Rationale
`Pipeline` now supports indexing and slicing. Users therefore expect the usual Python sequence idioms to work with it, such as `pipe[:len(pipe)]`. Without `__len__`, those idioms fail with an error, which makes the new indexing support inconsistent and harder to use.

## Use case or scenario
A user builds a `Pipeline`, here a `SelectKBest` feature selector followed by an `SVC` classifier. They want to find out how many steps it contains, or slice it using its length, as in `pipe[:len(pipe)]`.

## Possible solution
Implement `__len__` on `Pipeline`, as the title suggests, so that `len(pipe)` works.