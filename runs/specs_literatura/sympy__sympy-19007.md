## Summary

Indexing a `BlockMatrix` with a symbolic row index returns an element of the wrong block. For `C = BlockMatrix([[A], [B]])`, where `A` is a 1×1 `MatrixSymbol` and `B` is an n×1 `MatrixSymbol`, `C[i, 0]` with symbolic integer `i` evaluates to `(A)[i, 0]`. Depending on the value of `i`, that element may come from either `A` or `B`, so it should not be reduced to an element of `A`.

## Steps to reproduce

1. Define integer symbols `n` and `i`.
2. Create a 1×1 matrix symbol `A` and an n×1 matrix symbol `B`.
3. Stack them vertically into a block matrix: `C = BlockMatrix([[A], [B]])`.
4. Pretty-print `C`, then pretty-print `C[i, 0]`.

## Observed behavior

`C` prints as expected, but `C[i, 0]` is simplified to `(A)[i, 0]`, an element of block `A`:

```
C is
⎡A⎤
⎢ ⎥
⎣B⎦
C[i, 0] is
(A)[i, 0]
```

## Expected behavior

`C[i, 0]` should not be simplified to an element of `A`. Because `i` is symbolic, the element may come from either `A` or `B`, so the result should not commit to a single block.

## Stack trace / error output

Not provided in the original report. No exception is raised. The problem is an incorrect result, shown under "Observed behavior".

## Test case

Minimal test derived from the reproduction snippet in the report:

```python
from sympy import symbols, MatrixSymbol, BlockMatrix

def test_blockmatrix_symbolic_index_not_resolved_to_first_block():
    n, i = symbols('n, i', integer=True)
    A = MatrixSymbol('A', 1, 1)
    B = MatrixSymbol('B', n, 1)
    C = BlockMatrix([[A], [B]])
    # The element may come from either A or B, so it must not be A[i, 0]
    assert C[i, 0] != A[i, 0]
```

## Code example

Original snippet from the report:

```python
from sympy import *
n, i = symbols('n, i', integer=True)
A = MatrixSymbol('A', 1, 1)
B = MatrixSymbol('B', n, 1)
C = BlockMatrix([[A], [B]])
print('C is')
pprint(C)
print('C[i, 0] is')
pprint(C[i, 0])
```

## Version and environment

Not provided in the original report.