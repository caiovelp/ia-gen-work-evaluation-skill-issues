## Summary
When a fixture changes the current working directory, pytest shows the failing test's file path relative to the *new* directory, not the original one. The failure location appears as `../test_path_error.py:29` instead of `test_path_error.py:29`. Editors and compilation buffers don't know about the directory change, so they can't jump to the error. The path should stay relative to the original directory. The same thing happens when using `monkeypatch.chdir(out_dir)` instead of `os.chdir`.

## Steps to reproduce
1. Create a project directory (in the report: `~/src/pytest_path_error/`) containing `test_path_error.py` and `noxfile.py` from the Code example section below.
2. From that directory, run `nox`. This installs `pytest>=5.3` into a Python 3.7 virtualenv and runs `pytest`. Running `pytest` directly runs the same test.
3. The fixture `private_dir` creates a subdirectory `ddd` and `chdir`s into it before the test runs.
4. The test `test_show_wrong_path` fails with `assert False`.
5. Look at the file location reported for the failure.

## Observed behavior
The failure location is shown relative to the directory the fixture changed into (`ddd`):

```
../test_path_error.py:29: AssertionError
```

An editor or compilation mode working from the original directory (`~/src/pytest_path_error/`) cannot resolve this path, so you can't jump to the error.

## Expected behavior
The failure location should be shown relative to the original directory, regardless of any `chdir` done in a fixture:

```
test_path_error.py:29: AssertionError
```

## Stack trace / error output
```
-*- mode: compilation; default-directory: "~/src/pytest_path_error/" -*-
Compilation started at Fri Jan 10 00:05:52

nox
nox > Running session test
nox > Creating virtual environment (virtualenv) using python3.7 in .nox/test
nox > pip install pytest>=5.3
nox > pip freeze
attrs==19.3.0
importlib-metadata==1.3.0
more-itertools==8.0.2
packaging==20.0
pluggy==0.13.1
py==1.8.1
pyparsing==2.4.6
pytest==5.3.2
six==1.13.0
wcwidth==0.1.8
zipp==0.6.0
nox > pytest 
================================= test session starts =================================
platform linux -- Python 3.7.5, pytest-5.3.2, py-1.8.1, pluggy-0.13.1
rootdir: /home/lhn/src/pytest_path_error
collected 1 item                                                                      

test_path_error.py F                                                            [100%]

====================================== FAILURES =======================================
________________________________ test_show_wrong_path _________________________________

private_dir = 'ddd'

    def test_show_wrong_path(private_dir):
>       assert False
E       assert False

../test_path_error.py:29: AssertionError
================================== 1 failed in 0.03s ==================================
nox > Command pytest  failed with exit code 1
nox > Session test failed.

Compilation exited abnormally with code 1 at Fri Jan 10 00:06:01
```

## Test case
`test_path_error.py` from the report is a minimal reproducing test. When run from the directory that contains it, the failure location should read `test_path_error.py:29: AssertionError`, but it reads `../test_path_error.py:29: AssertionError`.

```python
import os
import errno
import shutil

import pytest


@pytest.fixture
def private_dir():  # or (monkeypatch)
    out_dir = 'ddd'

    try:
        shutil.rmtree(out_dir)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise
    os.mkdir(out_dir)

    old_dir = os.getcwd()
    os.chdir(out_dir)
    yield out_dir
    os.chdir(old_dir)

    # Same issue if using:
    # monkeypatch.chdir(out_dir)


def test_show_wrong_path(private_dir):
    assert False
```

## Code example
`noxfile.py` used to run the test:

```python
import nox

@nox.session(python='3.7')
def test(session):
    session.install('pytest>=5.3')
    session.run('pip', 'freeze')
    session.run('pytest')
```

## Version and environment
- Platform: Linux
- Python: 3.7.5
- pytest: 5.3.2
- py: 1.8.1
- pluggy: 0.13.1
- Other installed packages (`pip freeze`): attrs 19.3.0, importlib-metadata 1.3.0, more-itertools 8.0.2, packaging 20.0, pyparsing 2.4.6, six 1.13.0, wcwidth 0.1.8, zipp 0.6.0
- Run via `nox` in a virtualenv (`.nox/test`); output viewed in an editor compilation buffer with default directory `~/src/pytest_path_error/`
- pytest rootdir: `/home/lhn/src/pytest_path_error`