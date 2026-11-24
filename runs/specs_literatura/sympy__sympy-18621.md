## Summary

Converting a `BlockDiagMatrix` with exactly one matrix block to a regular `Matrix` raises `TypeError: 'One' object is not subscriptable`. The same conversion works with two or more blocks. This is a regression: it happens in SymPy 1.5.1 but not in SymPy 1.4.

## Steps to reproduce

1. Create a regular matrix: `M = sympy.Matrix([[1, 2], [3, 4]])`
2. Wrap it in a block diagonal matrix with a single block: `D = sympy.BlockDiagMatrix(M)`
3. Convert it back to a regular matrix: `B = sympy.Matrix(D)`

## Observed behavior

Step 3 raises `TypeError: 'One' object is not subscriptable`. The error comes from `BlockMatrix._entry` while `as_explicit()` builds the explicit matrix.

For comparison, the conversion works with two blocks:

```python
M = sympy.Matrix([[1, 2], [3, 4]])
D = sympy.BlockDiagMatrix(M, M)
B = sympy.Matrix(D)
```

Output:

```
Matrix([
[1, 2, 0, 0],
[3, 4, 0, 0],
[0, 0, 1, 2],
[0, 0, 3, 4]])
```

## Expected behavior

`sympy.Matrix(D)` should return a regular matrix for a single-block `BlockDiagMatrix`, just as it does for two blocks. Here that is a matrix equal to `M`, i.e. `Matrix([[1, 2], [3, 4]])`. This worked in SymPy 1.4.

## Stack trace / error output

```
Traceback (most recent call last):

  File "<ipython-input-37-5b65c1f8f23e>", line 3, in <module>
    B = sympy.Matrix(D)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/dense.py", line 430, in __new__
    return cls._new(*args, **kwargs)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/dense.py", line 442, in _new
    rows, cols, flat_list = cls._handle_creation_inputs(*args, **kwargs)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/matrices.py", line 2528, in _handle_creation_inputs
    return args[0].rows, args[0].cols, args[0].as_explicit()._mat

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 340, in as_explicit
    for i in range(self.rows)])

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 340, in <listcomp>
    for i in range(self.rows)])

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 339, in <listcomp>
    for j in range(self.cols)]

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 289, in __getitem__
    return self._entry(i, j)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 248, in _entry
    return self.blocks[row_block, col_block][i, j]

TypeError: 'One' object is not subscriptable
```

## Test case

```python
import sympy

def test_blockdiagmatrix_single_block_to_matrix():
    M = sympy.Matrix([[1, 2], [3, 4]])
    D = sympy.BlockDiagMatrix(M)
    B = sympy.Matrix(D)  # raises TypeError in SymPy 1.5.1
    assert B == M

def test_blockdiagmatrix_two_blocks_to_matrix():
    # Works as expected (control case)
    M = sympy.Matrix([[1, 2], [3, 4]])
    D = sympy.BlockDiagMatrix(M, M)
    B = sympy.Matrix(D)
    assert B == sympy.Matrix([
        [1, 2, 0, 0],
        [3, 4, 0, 0],
        [0, 0, 1, 2],
        [0, 0, 3, 4]])
```

## Code example

```python
import sympy

M = sympy.Matrix([[1, 2], [3, 4]])
D = sympy.BlockDiagMatrix(M)
B = sympy.Matrix(D)  # TypeError: 'One' object is not subscriptable
```

## Version and environment

- SymPy 1.5.1: affected
- SymPy 1.4: not affected
- Python 3.7, based on the installation path in the traceback
- Run from IPython, based on `<ipython-input-...>` in the traceback
- Operating system: Not provided in the original report.