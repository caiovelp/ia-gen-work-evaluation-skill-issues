## Summary

`convert_to` returns an incorrect result with a fractional exponent when the target unit is not dimensionally compatible with the expression being converted. Converting `joule*second` to `joule` returns `joule**(7/9)` instead of a meaningful result.

## Steps to reproduce

1. Use sympy 1.4.
2. Call `convert_to(joule*second, joule)`.
3. Observe the returned expression.

Background: `J = kg*m**2/s**2`, so `J*s = kg*m**2/s`. This is not dimensionally equivalent to `J`, so no exact conversion to `joule` exists.

## Observed behavior

```
>>> convert_to(joule*second, joule)
    joule**(7/9)
```

The result has a fractional exponent and is dimensionally wrong. The reporter suspects that `convert_to` only handles conversions correctly when the whole unit expression can be validly expressed in the target unit.

For comparison, these related conversions give sensible results:

```
>>> convert_to(joule*second, joule*second)
    joule*second
```
```
>>> convert_to(J*s, kg*m**2/s)
    kg*m**2/s
```
```
>>> convert_to(J*s, mins)
    J*mins/60
```

## Expected behavior

When the target unit is not compatible with the expression, `convert_to(joule*second, joule)` should do one of the following:
- return the original expression unchanged (`joule*second`),
- return the expression in base units (e.g. `kg*m**2/s`), or
- raise an error.

It should not return `joule**(7/9)`.

## Stack trace / error output

Not provided in the original report. No error is raised; the call returns the incorrect value shown above.

## Test case

Minimal check based on the report. Imports and the definitions of `J`, `s`, `kg`, `m` and `mins` are not given in the original report.

```python
result = convert_to(joule*second, joule)
# Observed: joule**(7/9)
# Expected: joule*second (unchanged), an expression in base units, or an error
assert result != joule**(Rational(7, 9))
```

## Code example

From the report:

```
>>> convert_to(joule*second, joule)
    joule**(7/9)
>>> convert_to(joule*second, joule*second)
    joule*second
>>> convert_to(J*s, kg*m**2/s)
    kg*m**2/s
>>> convert_to(J*s, mins)
    J*mins/60
```

## Version and environment

- sympy 1.4 (the reporter could not test 1.5 or later)
- OS / Python version: Not provided in the original report.