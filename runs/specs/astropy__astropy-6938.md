# Spec: Fix D-exponent replacement for ASCII table columns in `io.fits`

## Objective

`fitsrec.py` in `io.fits` contains this code:

```python
        # Replace exponent separator in floating point numbers
        if 'D' in format:
            output_field.replace(encode_ascii('E'), encode_ascii('D'))
```

The intent is to write floating-point values with a `D` exponent separator (for example `1.0D+05`) when a column's format specifies `D`. The reporter believes `chararray.replace` returns a new array and does not modify the original. The returned value is discarded, so the replacement probably never happens.

The reporter also found that commenting out these lines causes no test failures. So this behavior currently has no tests.

**Who is affected:** Anyone who writes FITS ASCII tables whose columns use `D` formats. They may be getting files with `E` exponents where they expect `D`.

**Goal:**
1. Confirm whether the bug is real.
2. If it is, make the `E`→`D` replacement take effect.
3. Add tests that would have caught the bug.

**Acceptance criteria:**
- A test shows the problem before the fix. It writes a table with a `D`-format column, and the serialized field still contains `E`.
- After the fix, values in `D`-format columns are written with `D` as the exponent separator.
- Columns that are not `D`-format are unchanged.
- Data written with `D` exponents reads back to the same numeric values.
- The test fails if the replacement line is commented out or made ineffective again.

## Assumptions

1. The code is in astropy's `io.fits` package, in the file `fitsrec.py`. The full path and the enclosing function are unknown; the issue gives only the file name.
2. `output_field` is a `numpy.char.chararray` or a similar view onto the record buffer being written. Changes are meant to reach the output only by modifying it in place.
3. `chararray.replace` returns a copy and does not modify in place. This is standard numpy behavior, but it must be verified for the numpy versions astropy supports.
4. The `'D' in format` check targets ASCII table (`TableHDU`) columns with `Dw.d` TFORMs. FITS ASCII tables allow `D` as the exponent separator for these.
5. `encode_ascii` is an existing helper that converts `str` to `bytes`.
6. The fix belongs inside `io.fits`. No public API changes are expected.

## Tech Stack

- Python, with astropy `io.fits` and numpy (`numpy.char.chararray`). The supported versions of both are unknown.
- Test framework: unknown. The issue does not say; it is likely pytest, but this needs confirming.

## Commands

All unknown; the issue does not specify them.
- Build: unknown
- Test (whole suite): unknown
- Test (`io.fits` only): unknown
- Lint: unknown

## Project Structure

Only the following is known from the issue:
```
.../io/fits/fitsrec.py   → contains the faulty replacement (full path unknown)
```
The location of the `io.fits` tests is unknown. New tests should go next to the existing tests for ASCII tables and table writing in `io.fits`.

## Code Style

Follow the existing conventions in `fitsrec.py`. The only style shown in the issue is the snippet above. It uses `encode_ascii(...)` for byte literals and short `#` comments that explain intent. Other conventions are unknown.

## Testing Strategy

- **Level:** Unit and integration tests within the `io.fits` test suite (location unknown).
- **Regression test (required):**
  - Create an ASCII table HDU with a float column whose format is `D`.
  - Use values that need an exponent, such as very large or very small numbers.
  - Write it to a file or buffer.
  - Assert that the raw serialized bytes for that column contain `D` and not `E` as the exponent separator.
- **Round-trip test:** Read the written file back. Check that the values match the originals within float tolerance.
- **Negative test:** An `E`/`F`-format column in the same table keeps its original formatting.
- **Mutation check:** Comment out the fixed line and confirm the new test fails. This guards against the original "no test fails" situation.
- Coverage target: unknown. At minimum, the `'D' in format` branch must be exercised.

## Boundaries

- **Always:**
  - Write the failing regression test before changing `fitsrec.py`.
  - Run the existing `io.fits` test suite.
  - Keep the change limited to the D-exponent handling.
- **Ask first:**
  - Changing how `D` exponents are handled on the read path.
  - Changing behavior for binary tables.
  - Any change to public API or default output formatting for non-`D` columns.
  - Adding dependencies.
- **Never:**
  - Delete the replacement code just because no test covers it, without confirming the intended FITS behavior.
  - Weaken or remove existing tests.
  - Change unrelated formatting logic in `fitsrec.py`.

## Success Criteria

- [ ] There is a reproduction showing that `chararray.replace` returns a copy and the current code leaves `E` in `D`-format output. Alternatively, there is evidence that the code works, in which case the issue is closed with an explanation.
- [ ] `D`-format ASCII table columns are written with a `D` exponent separator.
- [ ] Non-`D` columns produce output identical to before the change.
- [ ] Written `D`-exponent values round-trip to the same numeric values when read.
- [ ] The new tests fail when the replacement is disabled and pass with the fix.
- [ ] The full `io.fits` test suite passes.

## Open Questions

1. Is the intended behavior really to write `D` exponents for `D`-format ASCII columns? Or would standard-compliant `E` output be acceptable, so that the code should simply be removed?
2. Does this code path also run for binary tables, or only for ASCII tables? What is the enclosing function?
3. Is `output_field` always a view into the output buffer? If so, an in-place assignment would propagate. If it is sometimes a copy, the result must be written back somewhere else.
4. Is there matching handling on the read side that converts `D` exponents back to `E` before parsing? Does it have tests?
5. Could fixing this change output that downstream users currently rely on, given the code has silently been a no-op? Does it need a changelog entry?
6. What test command and test file location should be used for `io.fits`?
7. Which numpy versions must be supported? Are there any where `chararray.replace` behaves differently?