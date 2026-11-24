## Summary

`expr.subs({1: 1.0})` raises `PolynomialError: Piecewise generators do not make sense` for expressions of the form `exp(sinh(Piecewise(...) / z))` when `x` and `y` are declared `real=True`. The failure depends on the cache: running the same `subs` call again without clearing the cache succeeds.

The reporter found this while casting every integer atom to float across many expressions, before lambdifying them for TensorFlow, to avoid TensorFlow type errors. In the real use case the expression has a `+ 1` at the end. The snippet below is the minimal example they could produce.

## Steps to reproduce

1. Import SymPy and `clear_cache` from `sympy.core.cache`.
2. Define `x, y, z = symbols('x y z', real=True)`.
3. Call `clear_cache()`.
4. Build `expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))`.
5. Call `expr.subs({1: 1.0})`. This raises the error.
6. Call `expr.subs({1: 1.0})` again without clearing the cache. This succeeds.

For comparison, the same steps with plain symbols (`symbols('x y z')`, no `real=True`) do not raise.

The reporter observed these conditions:

- **Function:** The error occurs with `sinh`, `cosh` or `tanh`. As far as the reporter knows, other functions in that position succeed.
- **Division by `z`:** Removing `/ z` makes the error go away.
- **Outer `exp`:** Removing the outer `exp` makes the error go away. Replacing `exp` with most other unary functions (for example `sin` or `log`) keeps the error.
- **Real assumptions:** The error only happens when `x` and `y` are real. `z` does not need to be real.

## Observed behavior

With `x` and `y` real, the first call to `expr.subs({1: 1.0})` after `clear_cache()` raises:

```
PolynomialError: Piecewise generators do not make sense
```

Running `expr.subs({1: 1.0})` again without clearing the cache (for example in isympy) works without error.

## Expected behavior

`expr.subs({1: 1.0})` should complete without raising, whatever the symbol assumptions and cache state are. It should behave the way it does with non-real symbols, or on the second call.

## Stack trace / error output

Only the error message was given; the full traceback is not provided in the original report.

```
PolynomialError: Piecewise generators do not make sense
```

## Test case

Minimal test case derived from the report's snippet:

```python
from sympy import symbols, exp, sinh, Piecewise
from sympy.core.cache import clear_cache

def test_subs_piecewise_sinh_real_symbols():
    clear_cache()
    x, y, z = symbols('x y z', real=True)
    expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
    # Currently raises PolynomialError: Piecewise generators do not make sense
    expr.subs({1: 1.0})
```

## Code example

The reporter's original snippet:

```python
from sympy import *
from sympy.core.cache import clear_cache

x, y, z = symbols('x y z')

clear_cache()
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
# This works fine
expr.subs({1: 1.0})

clear_cache()
x, y, z = symbols('x y z', real=True)
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
# This fails with "PolynomialError: Piecewise generators do not make sense"
expr.subs({1: 1.0})  # error
# Now run it again (isympy...) w/o clearing cache and everything works as expected without error
expr.subs({1: 1.0})
```

## Version and environment

- SymPy version: 1.8.dev
- Python version, operating system and other environment details: Not provided in the original report.