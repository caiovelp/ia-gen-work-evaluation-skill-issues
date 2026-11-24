## Summary

pytest caches the evaluation of string conditions in `skipif`/`xfail` marks, such as `@pytest.mark.skipif("sys.platform == 'win32'")`. The cache key is only the condition string (see `cached_eval` in `_pytest/mark/evaluate.py`). The result of the evaluation also depends on the test item's module globals. When two modules use the same condition string but define different values for the referenced globals, the cached result from the first module is reused for the second, which gives the wrong outcome.

## Steps to reproduce

1. Create `test_module_1.py`, which defines a module-level `skip = True` and a test marked `@pytest.mark.skipif("skip")` (see Test case below).
2. Create `test_module_2.py`, which defines a module-level `skip = False` and a test marked with the same `@pytest.mark.skipif("skip")` (see Test case below).
3. Run:
   ```
   pytest test_module_1.py test_module_2.py
   ```
4. Check whether each test is skipped.

## Observed behavior

Both `test_should_skip` and `test_should_not_skip` are skipped.

## Expected behavior

- `test_should_skip` (in `test_module_1.py`, where `skip = True`) is skipped.
- `test_should_not_skip` (in `test_module_2.py`, where `skip = False`) is **not** skipped. It runs, and because its body is `assert False`, it fails.

## Stack trace / error output

Not provided in the original report.

## Test case

```py
# test_module_1.py
import pytest

skip = True

@pytest.mark.skipif("skip")
def test_should_skip():
    assert False
```

```py
# test_module_2.py
import pytest

skip = False

@pytest.mark.skipif("skip")
def test_should_not_skip():
    assert False
```

Run both modules in one session:

```
pytest test_module_1.py test_module_2.py
```

## Code example

Not provided in the original report. The report names `cached_eval` in `_pytest/mark/evaluate.py` as the function where the cache key is only the condition string, but it does not include that function's code.

## Version and environment

- pytest 5.4.3
- Also reported as affecting current master at the time of the report
- Operating system and Python version: Not provided in the original report.