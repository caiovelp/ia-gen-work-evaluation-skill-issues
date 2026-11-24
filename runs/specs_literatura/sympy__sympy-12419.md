## Summary

Under the assumption that `M` is orthogonal, SymPy correctly simplifies `M.T * M` to an identity matrix. The sum of its diagonal elements is correctly `n`. However, the double sum over all elements returns `0` instead of the expected `n`.

## Steps to reproduce

1. Define a positive integer symbol `n`, integer symbols `i` and `j`, and an `n x n` `MatrixSymbol` `M`.
2. Assume `M` is orthogonal (`Q.orthogonal(M)`) and compute `e = refine((M.T * M).doit())`.
3. Check that `e` is an identity matrix:
   - Print the matrix and its elements `e[0, 0]`, `e[0, 1]`, `e[1, 0]` and `e[1, 1]`.
   - Query `ask(Q.diagonal(e))` and `ask(Q.integer_elements(e))`.
   - Sum the diagonal with `Sum(e[i, i], (i, 0, n-1)).doit()`.

   All of these give the expected results. The sum of the diagonal is `n`.
4. Compute the sum of all elements with `Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit()`.

## Observed behavior

- `e` is recognized as an identity matrix.
- The element-wise checks give the expected results.
- `ask(Q.diagonal(e))` and `ask(Q.integer_elements(e))` both return `True`.
- The sum of the diagonal elements is `n`.
- The double sum over all elements returns `0`.

## Expected behavior

The sum of all elements of an `n x n` identity matrix should be `n`.

## Stack trace / error output

Not provided in the original report. No exception is raised. The result is wrong: it is `0`.

## Test case

Minimal test derived from the reproduction snippet in the report:

```python
from sympy import *
from sympy import Q as Query

def test_sum_of_identity_matrix_elements():
    n = Symbol('n', integer=True, positive=True)
    i, j = symbols('i j', integer=True)
    M = MatrixSymbol('M', n, n)

    with assuming(Query.orthogonal(M)):
        e = refine((M.T * M).doit())

    # Passes according to the report
    assert Sum(e[i, i], (i, 0, n-1)).doit() == n

    # Fails according to the report: the result is 0
    assert Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit() == n
```

## Code example

Original snippet from the report:

```python
from sympy import *
from sympy import Q as Query

n = Symbol('n', integer=True, positive=True)
i, j = symbols('i j', integer=True)
M = MatrixSymbol('M', n, n)

e = None
with assuming(Query.orthogonal(M)):
    e = refine((M.T * M).doit())

# Correct: M.T * M is an identity matrix.
print(e, e[0, 0], e[0, 1], e[1, 0], e[1, 1])

# Correct: The output is True True
print(ask(Query.diagonal(e)), ask(Query.integer_elements(e)))

# Correct: The sum of the diagonal elements is n
print(Sum(e[i, i], (i, 0, n-1)).doit())

# So far so good
# Total sum of the elements is expected to be 'n' but the answer is 0!
print(Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit())
```

## Version and environment

Not provided in the original report.