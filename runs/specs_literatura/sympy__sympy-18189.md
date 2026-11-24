## Summary

With `permute=True`, `diophantine` returns an incomplete set of solutions depending on the order of symbols passed in `syms`. For the equation `n**4 + m**4 - 2**4 - 3**4`, `syms=(m, n)` returns all 8 signed and permuted solutions, but `syms=(n, m)` returns only `{(3, 2)}`.

## Steps to reproduce

1. Make `m` and `n` available as symbols. The original report does not show how they were defined.
2. Run:
   ```python
   diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m, n), permute=True)
   ```
   and note the result.
3. Run the same call with the symbol order reversed:
   ```python
   diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n, m), permute=True)
   ```
4. Compare the two results.

## Observed behavior

With `syms=(m, n)`, the full set of 8 solutions is returned:
```
{(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}
```

With `syms=(n, m)`, only one solution is returned:
```
{(3, 2)}
```

## Expected behavior

The result should not depend on the order of `syms`, except for the order of values within each tuple. With `syms=(n, m)` and `permute=True`, the call should return the complete set of solutions, the same as with `syms=(m, n)`. Because the equation is symmetric in `m` and `n`, the expected set is:
```
{(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}
```

## Stack trace / error output

Not provided in the original report. No error is raised; the function returns incomplete results.

## Test case

Minimal test derived from the report's snippet. The symbol setup is assumed, since the report does not show it.

```python
# assumes m, n are symbols and diophantine is imported (setup not shown in the original report)
full = {(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}
eq = n**4 + m**4 - 2**4 - 3**4

assert diophantine(eq, syms=(m, n), permute=True) == full  # passes per report
assert diophantine(eq, syms=(n, m), permute=True) == full  # fails: returns {(3, 2)}
```

## Code example

```
In [10]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m,n), permute=True)
Out[10]: {(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}

In [11]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n,m), permute=True)
Out[11]: {(3, 2)}
```

## Version and environment

Not provided in the original report.