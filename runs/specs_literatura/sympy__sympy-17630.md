## Summary

Block-multiplying a `BlockMatrix` that contains `ZeroMatrix` blocks works once but raises `AttributeError: 'Zero' object has no attribute 'cols'` when done a second time, e.g. `block_collapse(b * b * b)` or `b._blockmul(b)._blockmul(b)`.

The reporter found that after one multiplication the zero blocks of the result are `sympy.core.numbers.Zero` rather than `ZeroMatrix`. The reporter believes this is the cause but does not know why it happens.

## Steps to reproduce

1. Define a block matrix with zero blocks:
   ```python
   from sympy import *
   a = MatrixSymbol("a", 2, 2)
   z = ZeroMatrix(2, 2)
   b = BlockMatrix([[a, z], [z, z]])
   ```
2. Block-multiply once. This works:
   ```python
   block_collapse(b * b)
   b._blockmul(b)
   ```
3. Block-multiply twice. This raises an exception:
   ```python
   block_collapse(b * b * b)
   b._blockmul(b)._blockmul(b)
   ```
4. Optionally, inspect the type of a zero block after one multiplication:
   ```python
   type(b._blockmul(b).blocks[0, 1])
   ```

## Observed behavior

- A single multiplication succeeds. Both `block_collapse(b * b)` and `b._blockmul(b)` return:
  ```
  Matrix([
  [a**2, 0],
  [0, 0]])
  ```
- A double multiplication fails. Both `block_collapse(b * b * b)` and `b._blockmul(b)._blockmul(b)` raise `AttributeError: 'Zero' object has no attribute 'cols'`.
- The zero blocks in the result of one multiplication are `Zero`, not `ZeroMatrix`:
  ```
  >>> type(b._blockmul(b).blocks[0, 1])
  <class 'sympy.core.numbers.Zero'>
  ```

## Expected behavior

Multiplying the block matrix more than once should work the same way a single multiplication does, without raising an exception.

## Stack trace / error output

`block_collapse(b * b * b)`:
```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 297, in block_collapse
    result = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 44, in chain_rl
    expr = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 33, in conditioned_rl
    return rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 95, in switch_rl
    return rl(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 361, in bc_matmul
    matrices[i] = A._blockmul(B)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
```

`b._blockmul(b)._blockmul(b)`:
```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
```

## Test case

This minimal test is derived from the reproduction in the report. It checks only that no exception is raised, because the report does not state the expected result value.

```python
from sympy import MatrixSymbol, ZeroMatrix, BlockMatrix, block_collapse

def test_blockmatrix_zero_blocks_multiply_twice():
    a = MatrixSymbol("a", 2, 2)
    z = ZeroMatrix(2, 2)
    b = BlockMatrix([[a, z], [z, z]])

    # Single multiplication works (per the report)
    block_collapse(b * b)
    b._blockmul(b)

    # Double multiplication currently raises AttributeError
    block_collapse(b * b * b)
    b._blockmul(b)._blockmul(b)
```

## Code example

```python
>>> from sympy import *
>>> a = MatrixSymbol("a", 2, 2)
>>> z = ZeroMatrix(2, 2)
>>> b = BlockMatrix([[a, z], [z, z]])
>>> block_collapse(b * b)          # works
>>> b._blockmul(b)                 # works
>>> block_collapse(b * b * b)      # AttributeError
>>> b._blockmul(b)._blockmul(b)    # AttributeError
>>> type(b._blockmul(b).blocks[0, 1])
<class 'sympy.core.numbers.Zero'>
```

## Version and environment

- SymPy 1.4, installed with pip
- Python 3.7.4, installed via pyenv (based on the traceback paths)
- Operating system: not stated; the paths (`/home/jan/...`) suggest a Unix-like system