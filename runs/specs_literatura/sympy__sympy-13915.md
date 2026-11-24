## Summary

In SymPy 1.1.1, `subs` returns `1` for an expression that is undefined at the substituted value. With `r = (1/(a+b) + 1/(a-b))/(1/(a+b) - 1/(a-b))`, `r.subs(b, a)` returns `1`. Substituting `b = a` makes the subexpression `1/(a-b)` undefined, so `r` itself should be undefined. For comparison, the limit `r.limit(b, a)` evaluates to `-1`, not `1`.

## Steps to reproduce

1. Start a Python session with SymPy 1.1.1 installed.
2. Run `from sympy import *`.
3. Define the symbols: `a, b = symbols('a,b')`.
4. Build the expression: `r = (1/(a+b) + 1/(a-b))/(1/(a+b) - 1/(a-b))`.
5. Evaluate `r.subs(b, a)`.

## Observed behavior

`r.subs(b, a)` returns `1`:

```
In [4]: r.subs(b,a)
Out[4]: 1
```

## Expected behavior

The result should be undefined. When `b` is replaced by `a`, the subexpression `1/(a-b)` becomes `1/0`. As the reporter puts it: "whenever a subexpression of r is undefined, r itself is undefined."

The reporter also notes that the limit `r.limit(b, a)` gives `-1`. This shows that `1` is not the value of the expression as `b` approaches `a` either.

## Stack trace / error output

Not provided in the original report. No error is raised; the call silently returns `1`.

## Test case

```python
from sympy import symbols

def test_subs_into_undefined_subexpression():
    a, b = symbols('a,b')
    r = (1/(a+b) + 1/(a-b))/(1/(a+b) - 1/(a-b))
    # 1/(a-b) is undefined at b == a, so r is undefined there;
    # currently this returns 1
    assert r.subs(b, a) != 1
```

## Code example

From the original IPython session:

```python
from sympy import *

a, b = symbols('a,b')
r = (1/(a+b) + 1/(a-b))/(1/(a+b) - 1/(a-b))

r.subs(b, a)    # returns 1 (expected: undefined)
r.limit(b, a)   # -1
```

## Version and environment

- SymPy: 1.1.1
- Python: 3.6.4 | Anaconda custom (64-bit) | (default, Dec 21 2017, 15:39:08)
- IPython: 6.2.1
- Operating system: Not provided in the original report.