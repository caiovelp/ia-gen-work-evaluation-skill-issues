## Summary

`simplify()` does not reduce the difference of two equivalent power expressions to `0` when one uses a floating-point exponent (`x**2.5`) and the other a rational exponent (`x**(S(5)/2)`), even after `evalf()` is applied. The result is printed as `-0.5*x**2.5 + 0.5*x**2.5`.

## Steps to reproduce

1. Create a symbol `x = Symbol('x')`.
2. Build `expr1 = S(1)/2*x**2.5`, which uses a float exponent.
3. Build `expr2 = S(1)*x**(S(5)/2)/2`, which uses a rational exponent.
4. Compute `res = expr1 - expr2`.
5. Evaluate numerically and simplify: `res = simplify(res.evalf(5))`.
6. Print `res`.

## Observed behavior

The printed result is:

```
-0.5*x**2.5 + 0.5*x**2.5
```

The two terms look identical but do not cancel.

## Expected behavior

The expression should simplify to `0`. The reporter asks: "How do I simplify it to 0?"

## Stack trace / error output

Not provided in the original report. No error is raised; the problem is the unsimplified output shown above.

## Test case

A minimal test case built from the reporter's snippet:

```python
from sympy import Symbol, S, simplify

def test_float_and_rational_exponent_cancel():
    x = Symbol('x')
    expr1 = S(1)/2*x**2.5
    expr2 = S(1)*x**(S(5)/2)/2
    res = simplify((expr1 - expr2).evalf(5))
    assert res == 0  # currently gives -0.5*x**2.5 + 0.5*x**2.5
```

## Code example

The original snippet from the report (it uses Python 2 `print` syntax):

```python
import sympy
from sympy import *
x=Symbol('x')
expr1 = S(1)/2*x**2.5
expr2 = S(1)*x**(S(5)/2)/2
res = expr1-expr2
res= simplify(res.evalf(5))
print res
```

## Version and environment

Not provided in the original report. The `print res` statement suggests Python 2, but no SymPy or Python version is stated.