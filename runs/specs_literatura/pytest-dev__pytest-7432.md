## Summary

With `@pytest.mark.skip` / `skipif`, pytest normally reports the location of the skipped test item. When `--runxfail` is added, the reported skip location points to pytest's own internals (`src/_pytest/skipping.py:238`) instead. `--runxfail` only concerns xfail and should not affect skip location reporting.

The reporter notes that the bug is in the `pytest_runtest_makereport` hook in `src/_pytest/skipping.py`.

## Steps to reproduce

1. Create a file `test_it.py` with this content:
   ```py
   import pytest
   @pytest.mark.skip
   def test_skip_location() -> None:
       assert 0
   ```
2. Run `pytest -rs`. The skip location is reported correctly as `test_it.py:3`.
3. Run `pytest -rs --runxfail`. The skip location is now wrong.

## Observed behavior

With `pytest -rs --runxfail`, the skip summary points to pytest's internal source file instead of the test:

```
SKIPPED [1] src/_pytest/skipping.py:238: unconditional skip
```

## Expected behavior

The skip location should point to the test item itself, as it does without `--runxfail`:

```
SKIPPED [1] test_it.py:3: unconditional skip
```

Adding `--runxfail` should not change skip location reporting, because the option only relates to xfail.

## Stack trace / error output

There is no stack trace. Here is the relevant output from the original report.

`pytest -rs` (correct):
```
SKIPPED [1] test_it.py:3: unconditional skip
```

`pytest -rs --runxfail` (incorrect):
```
SKIPPED [1] src/_pytest/skipping.py:238: unconditional skip
```

## Test case

A minimal test case based on the reproduction in the report:

1. Use `test_it.py` from the code example below.
2. Run `pytest -rs --runxfail`.
3. Assert that the output contains `SKIPPED [1] test_it.py:3: unconditional skip`.
4. Assert that the output does not contain `src/_pytest/skipping.py`.

The same assertion holds today for `pytest -rs` without `--runxfail`. It fails today with `--runxfail`.

## Code example

```py
import pytest
@pytest.mark.skip
def test_skip_location() -> None:
    assert 0
```

The report says the same problem applies to `@pytest.mark.skipif`.

## Version and environment

- pytest versions: 5.4.x and current master (at the time of the report)
- Python version, OS and plugins: Not provided in the original report.