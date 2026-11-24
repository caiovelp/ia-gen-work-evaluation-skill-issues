## Summary

With pytest's `--import-mode=importlib`, a module is imported twice. Two different module objects for `pmxbot.logging` exist at the same time. One is in `sys.modules['pmxbot.logging']`. The other is the `logging` name referenced inside the test module `tests.unit.test_commands`. Both point to the same file, `/Users/jaraco/code/pmxbot/pmxbot/pmxbot/logging.py`.

As a result, `core.initialize()` appears to have no effect. The initializer does run and sets the class variable `pmxbot.logging.Logger.store`, but the test module sees a different copy of `pmxbot.logging` that never received that attribute.

This happened while switching pmxbot from `pkg_resources`-style namespace packaging to PEP 420 namespace packages. That switch required `import-mode=importlib` and a reorganization of the tests to avoid import errors.

## Steps to reproduce

1. Check out pmxbot/pmxbot at commit `7f189ad`. At this commit the project uses PEP 420 namespace packages and the tests have been reorganized.
2. Configure pytest to use `import-mode=importlib`.
3. Run the test suite, for example the tests in `tests/unit/test_commands.py`.
4. Observe the error in `TestCommands.setup_class`.

Note: the reporter has not yet produced a minimal reproducer.

## Observed behavior

- `TestCommands.setup_class` fails with `AttributeError: type object 'Logger' has no attribute 'store'` immediately after `core.initialize(config)` returns.
- Inspection in PDB shows that `logging` in the test module and `sys.modules['pmxbot.logging']` are both `<module 'pmxbot.logging' from '/Users/jaraco/code/pmxbot/pmxbot/pmxbot/logging.py'>`.
- However, they are not the same object: `sys.modules['pmxbot.logging'] is logging` evaluates to `False`.
- The initializer sets `Logger.store` on the class in one copy of the module. The test accesses the class in the other copy.

## Expected behavior

`pmxbot.logging` should be imported only once. The `logging` module referenced in `tests.unit.test_commands` should be the same object as `sys.modules['pmxbot.logging']`. Then `logging.Logger.store` set by `core.initialize()` would be visible to the test.

## Stack trace / error output

```
=========================================================================== test session starts ===========================================================================
platform darwin -- Python 3.11.1, pytest-7.2.0, pluggy-1.0.0
cachedir: .tox/python/.pytest_cache
rootdir: /Users/jaraco/code/pmxbot/pmxbot, configfile: pytest.ini
plugins: black-0.3.12, mypy-0.10.3, jaraco.test-5.3.0, checkdocs-2.9.0, flake8-1.1.1, enabler-2.0.0, jaraco.mongodb-11.2.1, pmxbot-1122.14.3.dev13+g7f189ad
collected 421 items / 180 deselected / 241 selected
run-last-failure: rerun previous 240 failures (skipped 14 files)

tests/unit/test_commands.py E
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> traceback >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

cls = <class 'tests.unit.test_commands.TestCommands'>

    @classmethod
    def setup_class(cls):
        path = os.path.dirname(os.path.abspath(__file__))
        configfile = os.path.join(path, 'testconf.yaml')
        config = pmxbot.dictlib.ConfigDict.from_yaml(configfile)
        cls.bot = core.initialize(config)
>       logging.Logger.store.message("logged", "testrunner", "some text")
E       AttributeError: type object 'Logger' has no attribute 'store'

tests/unit/test_commands.py:37: AttributeError
```

PDB session at the point of failure:

```
> /Users/jaraco/code/pmxbot/pmxbot/tests/unit/test_commands.py(37)setup_class()
-> logging.Logger.store.message("logged", "testrunner", "some text")
(Pdb) logging.Logger
<class 'pmxbot.logging.Logger'>
(Pdb) logging
<module 'pmxbot.logging' from '/Users/jaraco/code/pmxbot/pmxbot/pmxbot/logging.py'>
(Pdb) import sys
(Pdb) sys.modules['pmxbot.logging']
<module 'pmxbot.logging' from '/Users/jaraco/code/pmxbot/pmxbot/pmxbot/logging.py'>
(Pdb) sys.modules['pmxbot.logging'] is logging
False
```

## Test case

No standalone minimal test case was provided. The reporter states they have not yet made a minimal reproducer. The failing test is `tests/unit/test_commands.py::TestCommands` in pmxbot at commit `7f189ad`. It fails in `setup_class`, and the code is shown below.

## Code example

`setup_class` from `tests/unit/test_commands.py`, as shown in the traceback:

```python
@classmethod
def setup_class(cls):
    path = os.path.dirname(os.path.abspath(__file__))
    configfile = os.path.join(path, 'testconf.yaml')
    config = pmxbot.dictlib.ConfigDict.from_yaml(configfile)
    cls.bot = core.initialize(config)
    logging.Logger.store.message("logged", "testrunner", "some text")
```

## Version and environment

- Platform: darwin (macOS)
- Python: 3.11.1
- pytest: 7.2.0
- pluggy: 1.0.0
- Import mode: `importlib`
- Config file: `pytest.ini`
- Project: pmxbot/pmxbot at commit `7f189ad` (installed as `pmxbot-1122.14.3.dev13+g7f189ad`), using PEP 420 namespace packages
- Run via tox (cachedir `.tox/python/.pytest_cache`)
- Plugins: black-0.3.12, mypy-0.10.3, jaraco.test-5.3.0, checkdocs-2.9.0, flake8-1.1.1, enabler-2.0.0, jaraco.mongodb-11.2.1, pmxbot-1122.14.3.dev13+g7f189ad