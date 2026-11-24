## Summary
`bell(n).limit(n, oo)` returns the unevaluated expression `bell(oo)` instead of infinity (`oo`). The Bell numbers count the partitions of a set, so the limit as `n → oo` should evaluate to `oo` rather than stay unevaluated. The reporter notes that similar limits for the Fibonacci and Lucas numbers were recently fixed to behave this way.

## Steps to reproduce
1. Import SymPy and define a symbol `n`.
2. Compute the limit of `bell(n)` as `n` approaches infinity with `bell(n).limit(n, oo)`.
3. Look at the returned value.

## Observed behavior
The result is the unevaluated expression:
```
bell(oo)
```

## Expected behavior
The result should be `oo` (infinity).

## Stack trace / error output
Not provided in the original report. (No error is raised; the problem is the unevaluated result shown above.)

## Test case
Minimal test derived from the reproduction snippet in the report:
```python
from sympy import bell, symbols, oo

def test_bell_limit_at_infinity():
    n = symbols('n')
    assert bell(n).limit(n, oo) == oo
```

## Code example
```python
from sympy import *
n = symbols('n')
bell(n).limit(n,oo)

Output:
bell(oo)
```

## Version and environment
Not provided in the original report.