## Summary

`Intersection` gives different results when one of its arguments is duplicated. `Intersection({1},{1},{x})` evaluates to `EmptySet()`, but `Intersection({1},{x})` evaluates to `{1}`. Duplicate arguments should not change the result. Neither result is correct, because the outcome depends on whether `x` equals `1`.

## Steps to reproduce

1. In an interactive session where `x` is a symbol, evaluate `Intersection({1},{1},{x})`.
2. Evaluate `Intersection({1},{x})`.
3. Compare the two results.

## Observed behavior

```python
>>> Intersection({1},{1},{x})
EmptySet()
>>> Intersection({1},{x})
{1}
```

- With the duplicated argument `{1}`, the result is `EmptySet()`.
- Without the duplicate, the result is `{1}`.
- The results differ, and neither accounts for the case distinction on `x`.

## Expected behavior

- Both calls should return the same result, because duplicate arguments should not affect an intersection.
- That result should be one of:
  - `Piecewise(({1}, Eq(x, 1)), (S.EmptySet, True))`, or
  - an unevaluated `Intersection`.

## Stack trace / error output

Not provided in the original report. No error is raised; the problem is an incorrect result.

## Test case

This minimal check is derived from the report's snippet. It uses the same names as the report's session, where `x` is a symbol.

```python
# Duplicate arguments must not change the result
assert Intersection({1}, {1}, {x}) == Intersection({1}, {x})

# Result should be either the Piecewise below or remain unevaluated
assert Intersection({1}, {x}) == Piecewise(({1}, Eq(x, 1)), (S.EmptySet, True))  # or unevaluated
```

## Code example

```python
>>> Intersection({1},{1},{x})
EmptySet()
>>> Intersection({1},{x})
{1}
```

## Version and environment

Not provided in the original report.