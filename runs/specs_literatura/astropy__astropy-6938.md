## Summary

In `io.fits`, the code in `fitsrec.py` that replaces the exponent separator `E` with `D` in floating point numbers (for `D` formats) appears to have no effect. `replace` does not seem to be an in-place operation for `chararray`; it returns a copy, and that copy is never used. The code also appears to be untested, because commenting it out does not cause any tests to fail.

## Steps to reproduce

The issue was found by reading the code, not by running a reproduction.

1. Open `fitsrec.py` in `io.fits`.
2. Find the block that replaces the exponent separator when `'D'` is in `format` (see Code example below).
3. Note that `output_field.replace(...)` is called but its return value is not used. The reporter's understanding is that `chararray.replace` returns a copy rather than changing the array in place.
4. Comment out this block and run the test suite.

## Observed behavior

- The reporter believes the `replace` call returns a modified copy that is thrown away. If so, `output_field` would keep `E` as the exponent separator even when the format contains `D`.
- Commenting out the block does not cause any tests to fail. This suggests the code path is not covered by tests.

## Expected behavior

When the format contains `D`, the exponent separator in `output_field` should change from `E` to `D`, as the code comment says. Tests should also cover this behavior.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. The reporter notes that no existing test fails when this code is commented out.

## Code example

From `fitsrec.py`:

```python
        # Replace exponent separator in floating point numbers
        if 'D' in format:
            output_field.replace(encode_ascii('E'), encode_ascii('D'))
```

## Version and environment

Not provided in the original report. The affected component is `io.fits`, file `fitsrec.py`.