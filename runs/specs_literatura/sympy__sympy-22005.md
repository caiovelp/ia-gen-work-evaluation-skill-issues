## Summary

`solve_poly_system` fails to detect that a system has infinitely many solutions in one case. With generators `x, y`, the system `(x - 1,)` correctly raises `NotImplementedError`, since only zero-dimensional systems are supported. The equivalent system `(y - 1,)` does not raise. It returns `[(1,)]`, which ignores the free variable `x`.

## Steps to reproduce

1. Import `solve_poly_system` and define the symbols `x` and `y`.
2. Call `solve_poly_system((x - 1,), x, y)`. It raises `NotImplementedError`, which is correct.
3. Call `solve_poly_system((y - 1,), x, y)`. It returns a result instead of raising.

## Observed behavior

- `solve_poly_system((x - 1,), x, y)` raises:
  `NotImplementedError: only zero-dimensional systems supported (finite number of solutions)`
- `solve_poly_system((y - 1,), x, y)` returns `[(1,)]` without any error.

## Expected behavior

`solve_poly_system((y - 1,), x, y)` should raise `NotImplementedError`, just as `solve_poly_system((x - 1,), x, y)` does. The system has infinitely many solutions because `x` is unconstrained, so it is not zero-dimensional.

## Stack trace / error output

Error raised in the correctly handled case. The traceback was abbreviated in the original report.

```
>>> solve_poly_system((x - 1,), x, y)
Traceback (most recent call last):
...
NotImplementedError:
only zero-dimensional systems supported (finite number of solutions)
```

No error is raised in the faulty case:

```
>>> solve_poly_system((y - 1,), x, y)
[(1,)]
```

## Test case

The report includes these assertions, intended for `test_solve_poly_system` in `sympy/solvers/tests/test_polysys.py`:

```python
raises(NotImplementedError, lambda: solve_poly_system(
    Poly(x - 1, x, y), (x, y)))
raises(NotImplementedError, lambda: solve_poly_system(
    Poly(y - 1, x, y), (x, y)))
```

The second assertion currently fails because no exception is raised.

## Code example

```python
>>> solve_poly_system((x - 1,), x, y)
Traceback (most recent call last):
...
NotImplementedError:
only zero-dimensional systems supported (finite number of solutions)
>>> solve_poly_system((y - 1,), x, y)  # not handled correctly
[(1,)]
```

## Version and environment

Not provided in the original report. The affected code is in `sympy/solvers/polysys.py`.