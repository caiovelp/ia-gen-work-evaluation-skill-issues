## Summary
`decompose()` in the `intpoly` module returns its result in arbitrary order when called with `separate=True`. It returns `list(poly_dict.values())`, so the order of the list depends on the internal ordering of a dictionary. The reporter says this causes test failures after some changes to the core. The reporter also asks what this list output is used for. (CC: @ArifAhmed1995, @certik)

## Steps to reproduce
1. Call `decompose()` from `intpoly` on a polynomial with `separate=True`.
2. Inspect the order of the elements in the returned list.
3. Compare that order across environments or after changes to the core that affect dictionary ordering.

The original report does not include a concrete polynomial input.

## Observed behavior
With `separate=True`, `decompose()` returns `list(poly_dict.values())`. The order of this list is arbitrary. Tests that rely on a specific order of the returned elements fail after some changes to the core.

## Expected behavior
The output of `decompose(..., separate=True)` should not depend on arbitrary dictionary ordering. The result should have a well-defined order, or its type should not imply any order.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

## Code example
The relevant return statement, as quoted in the report:

```python
list(poly_dict.values())
```

## Version and environment
Not provided in the original report. The reporter only mentions that the failures appeared after unspecified changes to the core.