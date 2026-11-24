## Summary

Since pytest 6.0.0rc, adding an `xfail` marker to a test at runtime with `request.node.add_marker(...)` no longer marks the test as expected-to-fail. A failing assertion after the marker is added is reported as a normal failure (`F`) instead of an expected failure (`x`). In pytest 5.x, a dynamically added `xfail` marker behaved like a statically applied `@pytest.mark.xfail`.

## Steps to reproduce

1. Create `test_foo.py` with the contents shown under **Test case** below.
2. Run `pytest -rsx test_foo.py` with pytest 5.4.3. The test is reported as `XFAIL`.
3. Run the same command with pytest 6.0.0rc1. The test is reported as `FAILED`.

## Observed behavior

With pytest 6.0.0rc1, the test is reported as a failure (`test_foo.py F`) with an `AssertionError` on `assert 0`. The dynamically added `xfail` marker is ignored.

## Expected behavior

The test should be treated as if it were statically marked with `xfail`, as in pytest 5.4.3:

```
$ pytest -rsx test_foo.py
=============================== test session starts ================================
platform darwin -- Python 3.7.6, pytest-5.4.3, py-1.9.0, pluggy-0.13.0
hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase('/Users/taugspurger/sandbox/.hypothesis/examples')
rootdir: /Users/taugspurger/sandbox
plugins: xdist-1.29.0, hypothesis-4.36.2, forked-1.0.2, repeat-0.8.0, asyncio-0.10.0, cov-2.8.1
collected 1 item

test_foo.py x                                                                [100%]

============================= short test summary info ==============================
XFAIL test_foo.py::test_xfail_test
  xfail
================================ 1 xfailed in 0.07s ================================
```

## Stack trace / error output

Output with pytest 6.0.0rc1:

```
$ pytest -rsx test_foo.py
=============================== test session starts ================================
platform darwin -- Python 3.7.6, pytest-6.0.0rc1, py-1.9.0, pluggy-0.13.0
hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase('/Users/taugspurger/sandbox/.hypothesis/examples')
rootdir: /Users/taugspurger/sandbox
plugins: xdist-1.29.0, hypothesis-4.36.2, forked-1.0.2, repeat-0.8.0, asyncio-0.10.0, cov-2.8.1
collected 1 item

test_foo.py F                                                                [100%]

===================================== FAILURES =====================================
_________________________________ test_xfail_test __________________________________

request = <FixtureRequest for <Function test_xfail_test>>

    def test_xfail_test(request):
        mark = pytest.mark.xfail(reason="xfail")
        request.node.add_marker(mark)
>       assert 0
E       assert 0

test_foo.py:7: AssertionError
```

## Test case

```python
# file: test_foo.py
import pytest


def test_xfail_test(request):
    mark = pytest.mark.xfail(reason="xfail")
    request.node.add_marker(mark)
    assert 0
```

Run with: `pytest -rsx test_foo.py`

- Expected result: `1 xfailed`
- Actual result on pytest 6.0.0rc1: `1 failed`

## Code example

The pattern that changed behavior is adding the marker to the test's node from inside the test:

```python
mark = pytest.mark.xfail(reason="xfail")
request.node.add_marker(mark)
```

## Version and environment

- **Working version:** pytest 5.4.3
- **Failing version:** pytest 6.0.0rc1, according to the session header in the output. The report text also mentions "6.0.0rc0" and "6.0.1rc0", which is inconsistent.
- **Python:** 3.7.6
- **OS:** macOS 10.14.5 (platform `darwin`)
- **Other packages:** py 1.9.0, pluggy 0.13.0
- **Plugins:** xdist-1.29.0, hypothesis-4.36.2, forked-1.0.2, repeat-0.8.0, asyncio-0.10.0, cov-2.8.1
- The full `pip list` output is in the original report. It shows pytest 5.4.3 installed at the time it was captured.