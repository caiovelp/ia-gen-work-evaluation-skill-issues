## Summary

`trigsimp` incorrectly simplifies `cos(x) + sqrt(sin(x)**2)` to `cos(x) + sin(x)` when `x` is a general complex symbol. This is invalid because `sqrt(sin(x)**2)` is not equal to `sin(x)` for general complex `x`. The reporter says the result is correct when `x` is declared real.

## Steps to reproduce

1. Define a symbol `x` with no assumptions, so it is a general complex symbol.
2. Build the expression `cos(x) + sqrt(sin(x)**2)`.
3. Call `trigsimp` on the expression.
4. For comparison, repeat steps 1–3 with `x` declared real.

## Observed behavior

- **General complex `x`:** `trigsimp` simplifies the expression as though it were `cos(x) + sin(x)`. In effect, it replaces `sqrt(sin(x)**2)` with `sin(x)`.
- **Real `x`:** the reporter says the simplification is correct. The exact output was not given.

## Expected behavior

For general complex `x`, `trigsimp` should not rewrite `sqrt(sin(x)**2)` as `sin(x)`. The simplified result should remain mathematically equivalent to `cos(x) + sqrt(sin(x)**2)`.

## Stack trace / error output

Not provided in the original report. No exception is raised; the problem is an incorrect result.

## Test case

Not provided in the original report. A minimal test derived from the description:

```python
from sympy import symbols, cos, sin, sqrt, trigsimp

def test_trigsimp_sqrt_sin_squared_complex():
    x = symbols('x')  # no assumptions -> general complex
    expr = cos(x) + sqrt(sin(x)**2)
    assert trigsimp(expr) != cos(x) + sin(x)
```

## Code example

Not provided in the original report. The expression involved is `cos(x) + sqrt(sin(x)**2)`, simplified with `trigsimp`.

## Version and environment

- SymPy: "various versions, including 1.5"
- Python version, OS and other environment details: Not provided in the original report.