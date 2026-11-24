## Summary

On Python 3.9, when an `assert` fails, pytest's failure report shows an extra source line after the failing assertion. The extra line is the decorator line (`@t`) of a nested decorated function defined after the assertion. On Python 3.7 the same test shows only the failing `assert` line. The reporter asks whether the statement line number is being calculated incorrectly.

## Steps to reproduce

1. Create `test_statement.py` with the contents shown under **Test case**.
2. Run the test with pytest 6.2.5 on Python 3.9 (the reporter used 3.9.6 on Windows 10).
3. Look at the failure details for `test_right_statement`, which fails at its first assertion.
4. For comparison, run the same test with pytest 6.2.5 on Python 3.7 (the reporter used 3.7.10).

## Observed behavior

On Python 3.9.6 the failure excerpt includes an extra blank line and the `@t` decorator line from the nested function that follows the failing assertion. The `E` error lines appear after that decorator line:

```
    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
    
        @t
E       assert 1 == 75
```

## Expected behavior

The failure excerpt should end at the failing `assert` statement, with no following code. This is what happens on Python 3.7.10:

```
    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
E       assert 1 == 75
```

## Stack trace / error output

Python 3.9.6 (incorrect output):

```
============================= test session starts =============================
platform win32 -- Python 3.9.6, pytest-6.2.5, py-1.10.0, pluggy-0.13.1 -- 
cachedir: .pytest_cache
rootdir: 
plugins: allure-pytest-2.9.45
collecting ... collected 1 item

test_statement.py::test_right_statement FAILED                           [100%]

================================== FAILURES ===================================
____________________________ test_right_statement _____________________________

foo = 1

    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
    
        @t
E       assert 1 == 75
E         +1
E         -75

test_statement.py:14: AssertionError
=========================== short test summary info ===========================
FAILED test_statement.py::test_right_statement - assert 1 == 75
============================== 1 failed in 0.12s ==============================
```

Python 3.7.10 (correct output):

```
============================= test session starts =============================
platform win32 -- Python 3.7.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- 
cachedir: .pytest_cache
rootdir: 
collecting ... collected 1 item

test_statement.py::test_right_statement FAILED                           [100%]

================================== FAILURES ===================================
____________________________ test_right_statement _____________________________

foo = 1

    def test_right_statement(foo):
>       assert foo == (3 + 2) * (6 + 9)
E       assert 1 == 75
E         +1
E         -75

test_statement.py:14: AssertionError
=========================== short test summary info ===========================
FAILED test_statement.py::test_right_statement - assert 1 == 75
============================== 1 failed in 0.03s ==============================
```

## Test case

`test_statement.py`, as given in the original report:

```python
from pytest import fixture


def t(foo):
    return foo


@fixture
def foo():
    return 1


def test_right_statement(foo):
    assert foo == (3 + 2) * (6 + 9)

    @t
    def inner():
        return 2

    assert 2 == inner


@t
def outer():
    return 2
```

Expected result: the failure report for `test_right_statement` shows only the `assert foo == (3 + 2) * (6 + 9)` line as context, without the following `@t` line.

## Code example

The relevant pattern is a failing `assert` followed by a decorated nested function in the same test function (excerpt from the test case above):

```python
def test_right_statement(foo):
    assert foo == (3 + 2) * (6 + 9)

    @t
    def inner():
        return 2
```

## Version and environment

- OS: Windows 10 (`platform win32`)
- pytest: 6.2.5
- **Affected:** Python 3.9.6, with py 1.10.0, pluggy 0.13.1, and plugin allure-pytest 2.9.45 (from the session header)
- **Not affected:** Python 3.7.10, with py 1.11.0, pluggy 1.0.0, and no plugins listed (from the session header)
- `pip list` from the reporter's virtual environment (the report does not say which Python version it belongs to; its py and pluggy versions match the 3.7.10 session):

```
atomicwrites       1.4.0
attrs              21.2.0
colorama           0.4.4
importlib-metadata 4.8.2
iniconfig          1.1.1
packaging          21.3
pip                21.3.1
pluggy             1.0.0
py                 1.11.0
pyparsing          3.0.6
pytest             6.2.5
setuptools         59.4.0
toml               0.10.2
typing_extensions  4.0.0
zipp               3.6.0
```