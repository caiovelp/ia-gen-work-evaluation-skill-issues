## Summary

In SymPy 1.4, constructing an empty `Array` with `sympy.Array([])` raises a `ValueError`. Constructing an empty `Matrix` with `sympy.Matrix([])` works. The reporter asks whether this is intended.

## Steps to reproduce

1. Start a Python interpreter with SymPy 1.4 installed.
2. Run `from sympy import Array`.
3. Run `a = Array([])`.

## Observed behavior

`Array([])` raises `ValueError: not enough values to unpack (expected 2, got 0)` inside `_scan_iterable_shape` in `sympy/tensor/array/ndim_array.py`. The full traceback is below.

By contrast, `sympy.Matrix([])` works, according to the report title.

## Expected behavior

`Array([])` should create an empty array without raising an error, as `Matrix([])` does. The reporter frames this as a question ("Is this the intended behavior?"). The report does not say what shape or contents the empty `Array` should have.

## Stack trace / error output

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/dense_ndim_array.py", line 130, in __new__
    return cls._new(iterable, shape, **kwargs)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/dense_ndim_array.py", line 136, in _new
    shape, flat_list = cls._handle_ndarray_creation_inputs(iterable, shape, **kwargs)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 142, in _handle_ndarray_creation_inputs
    iterable, shape = cls._scan_iterable_shape(iterable)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 127, in _scan_iterable_shape
    return f(iterable)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 120, in f
    elems, shapes = zip(*[f(i) for i in pointer])
ValueError: not enough values to unpack (expected 2, got 0)
```

## Test case

A minimal test derived from the report. It fails on SymPy 1.4 with the `ValueError` shown above.

```python
from sympy import Array, Matrix

def test_empty_array_construction():
    Matrix([])  # works according to the report
    Array([])   # raises ValueError in SymPy 1.4
```

## Code example

From the original report:

```python
>>> import sympy
>>> from sympy import Array
>>> sympy.__version__
'1.4'
>>> a = Array([])
```

## Version and environment

- SymPy: 1.4
- Python: 3.7, according to the paths in the traceback (`.../lib/python3.7/site-packages/...`)
- SymPy installed in a miniconda environment, according to the traceback paths
- Operating system: Not provided in the original report.