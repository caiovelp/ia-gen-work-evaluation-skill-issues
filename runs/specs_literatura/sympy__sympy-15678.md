## Summary

`idiff` (in `sympy/geometry/util.py`) fails in two cases:

1. The equation is passed as an `Eq` object instead of an expression. It raises `IndexError: list index out of range`.
2. The dependent variable is given as a function such as `f(x)` instead of a symbol such as `y`. It raises `ValueError: expecting x-dependent symbol(s) but got: f(x)`.

The same equation passed as a plain expression with a symbol `y` works.

## Steps to reproduce

The report does not show how `x`, `y` and `f` were defined. Presumably `x` and `y` are symbols and `f` is an undefined function.

1. Call `idiff` with an `Eq`:
   `idiff(Eq(y*exp(y), x*exp(x)), y, x)`
2. Call `idiff` with `f(x)` as the dependent variable:
   `idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)`
3. For comparison, call `idiff` with the equivalent plain expression and symbol `y`:
   `idiff(y*exp(y) - x*exp(x), y, x)`

## Observed behavior

- Step 1 raises `IndexError: list index out of range`.
- Step 2 raises `ValueError: expecting x-dependent symbol(s) but got: f(x)`.
- Step 3 works and returns `(x + 1)*exp(x - y)/(y + 1)`.

## Expected behavior

`idiff` should support:

- `Eq` objects as the equation argument. Step 1 should give the same result as the equivalent expression form in step 3.
- A function of `x`, such as `f(x)`, as the dependent variable instead of a symbol. The call in step 2 should return the derivative rather than raising `ValueError`.

## Stack trace / error output

```
>>> idiff(Eq(y*exp(y), x*exp(x)), y, x)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/geometry/util.py", line 582, in idiff
    yp = solve(eq.diff(x), dydx)[0].subs(derivs)
IndexError: list index out of range
```

```
>>> idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/geometry/util.py", line 574, in idiff
    raise ValueError("expecting x-dependent symbol(s) but got: %s" % y)
ValueError: expecting x-dependent symbol(s) but got: f(x)
```

## Test case

This is a minimal test derived from the report's examples. The setup of `x`, `y` and `f` is not shown in the original report.

```python
# Eq should behave like the equivalent expression
assert idiff(Eq(y*exp(y), x*exp(x)), y, x) == idiff(y*exp(y) - x*exp(x), y, x)

# f(x) should be accepted as the dependent variable (currently raises ValueError)
idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)
```

## Code example

```python
>>> idiff(Eq(y*exp(y), x*exp(x)), y, x)           # IndexError
>>> idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)     # ValueError
>>> idiff(y*exp(y) - x*exp(x), y, x)              # works
(x + 1)*exp(x - y)/(y + 1)
```

## Version and environment

Not provided in the original report. The traceback paths (`./sympy/geometry/util.py`) suggest the code was run from a SymPy source checkout.