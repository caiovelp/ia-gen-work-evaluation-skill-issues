## Summary

`_estimate_mi` compares `discrete_features` to a string with `discrete_features == 'auto'`. However, `discrete_features` can also be an array of indices or a boolean mask. In those cases the code compares a string to an array, which will raise an error in future versions of numpy. The reporter also suspects that the function is never tested with `discrete_features` set to anything other than `'auto'`.

## Steps to reproduce

1. Call `_estimate_mi` with `discrete_features` set to an array of indices or a boolean mask, rather than `'auto'`.
2. The code evaluates `discrete_features == 'auto'`, which compares a string to an array.

## Observed behavior

When `discrete_features` is an array of indices or a boolean mask, `_estimate_mi` compares that array to the string `'auto'`. According to the reporter, this comparison will error in future versions of numpy. The reporter also notes that this case does not appear to be covered by tests, since the function seems never to be tested with `discrete_features != 'auto'`.

## Expected behavior

`_estimate_mi` should handle all supported forms of `discrete_features` without comparing an array to a string:

- `'auto'`
- an array of indices
- a boolean mask

This should keep working in future numpy versions. The non-`'auto'` cases should also be covered by tests.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. The reporter notes that there seem to be no tests calling `_estimate_mi` with `discrete_features` set to an array of indices or a boolean mask.

## Code example

The problematic expression in `_estimate_mi`:

```python
discrete_features == 'auto'
```

## Version and environment

Not provided in the original report. The report only states that the problem will arise in future versions of numpy.