## Summary

Collection fails with `TypeError: argument of type 'int' is not iterable` when the first expression in a test file is a number. pytest's assertion rewriter appears to treat the number as the module docstring, then runs a `"PYTEST_DONT_REWRITE" in docstring` check against an `int`.

## Steps to reproduce

1. Have a test module whose first expression is a number. The reporter's file was `testcases/基线/代理策略/SOCKS二级代理迭代二/在线用户/在线用户更新/上线用户/test_socks_user_011.py`. Its contents were not included in the report.
2. Run pytest with a keyword filter: `pytest -k xxx`.
3. Observe that collection of that module fails.

## Observed behavior

Collection of the module errors out with `TypeError: argument of type 'int' is not iterable`. The error comes from `is_rewrite_disabled` in `_pytest/assertion/rewrite.py`, which is called while pytest imports and rewrites the module.

## Expected behavior

The report does not state this explicitly. The title implies that pytest should not treat a number as the module docstring, and that the module should be collected and its assertions rewritten without error.

## Stack trace / error output

```
==================================== ERRORS ====================================
_ ERROR collecting testcases/基线/代理策略/SOCKS二级代理迭代二/在线用户/在线用户更新/上线用户/test_socks_user_011.py _
/usr/local/lib/python3.8/site-packages/_pytest/runner.py:341: in from_call
    result: Optional[TResult] = func()
/usr/local/lib/python3.8/site-packages/_pytest/runner.py:372: in <lambda>
    call = CallInfo.from_call(lambda: list(collector.collect()), "collect")
/usr/local/lib/python3.8/site-packages/_pytest/python.py:531: in collect
    self._inject_setup_module_fixture()
/usr/local/lib/python3.8/site-packages/_pytest/python.py:545: in _inject_setup_module_fixture
    self.obj, ("setUpModule", "setup_module")
/usr/local/lib/python3.8/site-packages/_pytest/python.py:310: in obj
    self._obj = obj = self._getobj()
/usr/local/lib/python3.8/site-packages/_pytest/python.py:528: in _getobj
    return self._importtestmodule()
/usr/local/lib/python3.8/site-packages/_pytest/python.py:617: in _importtestmodule
    mod = import_path(self.path, mode=importmode, root=self.config.rootpath)
/usr/local/lib/python3.8/site-packages/_pytest/pathlib.py:565: in import_path
    importlib.import_module(module_name)
/usr/local/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1014: in _gcd_import
    ???
<frozen importlib._bootstrap>:991: in _find_and_load
    ???
<frozen importlib._bootstrap>:975: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:671: in _load_unlocked
    ???
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:169: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:352: in _rewrite_test
    rewrite_asserts(tree, source, strfn, config)
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:413: in rewrite_asserts
    AssertionRewriter(module_path, config, source).run(mod)
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:695: in run
    if self.is_rewrite_disabled(doc):
/usr/local/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:760: in is_rewrite_disabled
    return "PYTEST_DONT_REWRITE" in docstring
E   TypeError: argument of type 'int' is not iterable
```

## Test case

Not provided in the original report. The title says the trigger is a test file whose first expression is a number, but the report includes no file contents.

## Code example

Not provided in the original report.

## Version and environment

- pytest 7.4.0
- Python 3.8, based on the `/usr/local/lib/python3.8/site-packages/` paths in the traceback
- Operating system: not explicitly stated in the original report
- Other installed packages that may be relevant: pluggy 1.2.0, iniconfig 2.0.0, packaging 23.1, exceptiongroup 1.1.1, tomli 2.0.1, py 1.11.0, pytest-check 2.1.5, pytest-html 3.2.0, pytest-metadata 3.0.0, pytest-rerunfailures 11.1.2, allure-pytest 2.13.2
- The original report includes the full package list as `pip install` output.