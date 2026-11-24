## Summary

Evaluating `is_zero` on the expression `cosh(acos(-i + acosh(-g + i)))`, created with `sympify`, raises `RecursionError: maximum recursion depth exceeded while calling a Python object` instead of returning a result.

## Steps to reproduce

1. Create the expression from a string with `sympify`:
   ```python
   expr = sympify("cosh(acos(-i + acosh(-g + i)))")
   ```
2. Query whether the expression is zero:
   ```python
   expr.is_zero
   ```

## Observed behavior

Accessing `expr.is_zero` raises a `RecursionError`:

```
RecursionError: maximum recursion depth exceeded while calling a Python object
```

## Expected behavior

The report does not state the expected value. It implies only that `expr.is_zero` should return a result instead of raising `RecursionError`.

## Stack trace / error output

Only the final error message is given:

```
RecursionError: maximum recursion depth exceeded while calling a Python object
```

The full stack trace is not provided in the original report.

## Test case

A minimal test derived from the reproduction snippet. The original snippet shows no imports, so `sympify` is assumed to be available.

```python
def test_cosh_acos_acosh_is_zero_no_recursion_error():
    expr = sympify("cosh(acos(-i + acosh(-g + i)))")
    # Must not raise RecursionError
    expr.is_zero
```

## Code example

From the original report:

```python
expr =sympify("cosh(acos(-i + acosh(-g + i)))")
expr.is_zero
```

## Version and environment

Not provided in the original report. The use of `sympify` suggests the library is SymPy, but no library, Python or OS versions are given.