## Summary

`Matrix.is_upper` raises an `IndexError` for "tall" matrices, which have more rows than columns. For example, it fails on a 4x2 matrix of zeros. The cause appears to be that the code builds column indices from the row range. It therefore tries to access entries outside the matrix's columns, such as entry (3, 2) of a 4x2 matrix.

## Steps to reproduce

1. Import SymPy.
2. Create a 4x2 zero matrix with `sympy.zeros(4, 2)`.
3. Access its `is_upper` property.

```python
>>> sympy.zeros(4,2).is_upper
```

## Observed behavior

Accessing `is_upper` raises `IndexError: Index out of range: a[2]`.

The generator in `is_upper` produces these `(i, j)` index pairs for a 4x2 matrix:

```
([1, 0], [2, 0], [2, 1], [3, 0], [3, 1], [3, 2])
```

The pairs `[2, 1]` and `[3, 1]` are valid because the matrix has columns 0 and 1. The pair `[3, 2]` refers to column 2, which does not exist in a 2-column matrix. The reporter identifies the attempt to index the (3, 2) entry as the apparent source of the error.

## Expected behavior

The report does not state the expected result explicitly. It implies that `is_upper` should work for tall (non-square) matrices: it should return a result instead of raising an `IndexError`.

## Stack trace / error output

```
>>> sympy.zeros(4,2).is_upper
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "sympy/matrices/matrices.py", line 1112, in is_upper
    for i in range(1, self.rows)
  File "sympy/matrices/matrices.py", line 1113, in <genexpr>
    for j in range(i))
  File "sympy/matrices/dense.py", line 119, in __getitem__
    return self.extract(i, j)
  File "sympy/matrices/matrices.py", line 352, in extract
    colsList = [a2idx(k, self.cols) for k in colsList]
  File "sympy/matrices/matrices.py", line 5261, in a2idx
    raise IndexError("Index out of range: a[%s]" % (j,))
IndexError: Index out of range: a[2]
```

## Test case

This minimal test was derived from the reproduction in the report. It checks only that no `IndexError` is raised, since the report does not state the expected return value.

```python
import sympy

def test_is_upper_tall_matrix_does_not_raise():
    A = sympy.zeros(4, 2)
    A.is_upper  # currently raises IndexError: Index out of range: a[2]
```

## Code example

Current implementation of `is_upper`, as quoted in the report:

```python
        return all(self[i, j].is_zero
                   for i in range(1, self.rows)
                   for j in range(i))
```

Index pairs this code iterates over for a 4x2 matrix, as shown in the report:

```python
>>> A = sympy.zeros(4, 2)
>>> print tuple([i, j] for i in range(1, A.rows) for j in range(i))
([1, 0], [2, 0], [2, 1], [3, 0], [3, 1], [3, 2])
```

## Version and environment

- The SymPy version, Python version and OS are not provided in the original report.
- The snippet uses the Python 2 `print` statement syntax (`print tuple(...)`), which suggests a Python 2 interpreter.
- The traceback references `sympy/matrices/matrices.py` (lines 1112, 1113, 352, 5261) and `sympy/matrices/dense.py` (line 119).