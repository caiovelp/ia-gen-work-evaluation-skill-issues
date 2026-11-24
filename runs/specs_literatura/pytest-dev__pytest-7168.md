## Summary

pytest crashes with an `INTERNALERROR` instead of reporting a normal test failure when a test fails on an object whose `__repr__` raises an exception. The crash happens while pytest builds the failure report. `saferepr` calls `repr()` on the object, which raises. pytest then handles that exception in `_format_repr_exception`, which accesses `obj.__class__`. Because the object's `__getattribute__` also raises, this fails too, and the error escapes as an `INTERNALERROR`. The session ends with "no tests ran".

## Steps to reproduce

1. Create a test file (named `test_pytest.py` in the original report) with the contents from the **Test case** section below.
2. Run pytest on that file.
3. Observe that pytest aborts with an `INTERNALERROR` while reporting the failure of `test_pytest.py::test`.

## Observed behavior

- The test is collected (`collected 1 item`).
- pytest does not report a test result. It crashes with an `INTERNALERROR` inside its failure-reporting code (`TestReport.from_item_and_call` → `repr_failure` → `repr_args` → `saferepr`).
- The final error is `RuntimeError: No active exception to reraise`, raised from the user's `__repr__`. It occurs while pytest is formatting the exception from the earlier `repr()` failure (`_format_repr_exception` → `obj.__class__`).
- The session summary reads: `no tests ran in 0.09s`.

## Expected behavior

The original report does not state this explicitly. The title ("INTERNALERROR when exception in __repr__") implies that pytest should not crash with an `INTERNALERROR` when an object's `__repr__` raises. It should instead report the test as failed in the usual way.

## Stack trace / error output

```
============================= test session starts ==============================
platform darwin -- Python 3.8.1, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /usr/local/opt/python@3.8/bin/python3.8
cachedir: .pytest_cache
rootdir: ******
plugins: asyncio-0.10.0, mock-3.0.0, cov-2.8.1
collecting ... collected 1 item

test_pytest.py::test 
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/main.py", line 191, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/main.py", line 247, in _main
INTERNALERROR>     config.hook.pytest_runtestloop(session=session)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/hooks.py", line 286, in __call__
INTERNALERROR>     return self._hookexec(self, self.get_hookimpls(), kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 93, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook, methods, kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 84, in <lambda>
INTERNALERROR>     self._inner_hookexec = lambda hook, methods, kwargs: hook.multicall(
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 208, in _multicall
INTERNALERROR>     return outcome.get_result()
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 80, in get_result
INTERNALERROR>     raise ex[1].with_traceback(ex[2])
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 187, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/main.py", line 272, in pytest_runtestloop
INTERNALERROR>     item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/hooks.py", line 286, in __call__
INTERNALERROR>     return self._hookexec(self, self.get_hookimpls(), kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 93, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook, methods, kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 84, in <lambda>
INTERNALERROR>     self._inner_hookexec = lambda hook, methods, kwargs: hook.multicall(
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 208, in _multicall
INTERNALERROR>     return outcome.get_result()
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 80, in get_result
INTERNALERROR>     raise ex[1].with_traceback(ex[2])
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 187, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/runner.py", line 85, in pytest_runtest_protocol
INTERNALERROR>     runtestprotocol(item, nextitem=nextitem)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/runner.py", line 100, in runtestprotocol
INTERNALERROR>     reports.append(call_and_report(item, "call", log))
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/runner.py", line 188, in call_and_report
INTERNALERROR>     report = hook.pytest_runtest_makereport(item=item, call=call)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/hooks.py", line 286, in __call__
INTERNALERROR>     return self._hookexec(self, self.get_hookimpls(), kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 93, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook, methods, kwargs)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/manager.py", line 84, in <lambda>
INTERNALERROR>     self._inner_hookexec = lambda hook, methods, kwargs: hook.multicall(
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 203, in _multicall
INTERNALERROR>     gen.send(outcome)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/skipping.py", line 129, in pytest_runtest_makereport
INTERNALERROR>     rep = outcome.get_result()
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 80, in get_result
INTERNALERROR>     raise ex[1].with_traceback(ex[2])
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/pluggy/callers.py", line 187, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/runner.py", line 260, in pytest_runtest_makereport
INTERNALERROR>     return TestReport.from_item_and_call(item, call)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/reports.py", line 294, in from_item_and_call
INTERNALERROR>     longrepr = item.repr_failure(excinfo)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/python.py", line 1513, in repr_failure
INTERNALERROR>     return self._repr_failure_py(excinfo, style=style)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/nodes.py", line 355, in _repr_failure_py
INTERNALERROR>     return excinfo.getrepr(
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_code/code.py", line 634, in getrepr
INTERNALERROR>     return fmt.repr_excinfo(self)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_code/code.py", line 879, in repr_excinfo
INTERNALERROR>     reprtraceback = self.repr_traceback(excinfo_)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_code/code.py", line 823, in repr_traceback
INTERNALERROR>     reprentry = self.repr_traceback_entry(entry, einfo)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_code/code.py", line 784, in repr_traceback_entry
INTERNALERROR>     reprargs = self.repr_args(entry) if not short else None
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_code/code.py", line 693, in repr_args
INTERNALERROR>     args.append((argname, saferepr(argvalue)))
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 82, in saferepr
INTERNALERROR>     return SafeRepr(maxsize).repr(obj)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 51, in repr
INTERNALERROR>     s = _format_repr_exception(exc, x)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 23, in _format_repr_exception
INTERNALERROR>     exc_info, obj.__class__.__name__, id(obj)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 47, in repr
INTERNALERROR>     s = super().repr(x)
INTERNALERROR>   File "/usr/local/Cellar/python@3.8/3.8.1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/reprlib.py", line 52, in repr
INTERNALERROR>     return self.repr1(x, self.maxlevel)
INTERNALERROR>   File "/usr/local/Cellar/python@3.8/3.8.1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/reprlib.py", line 62, in repr1
INTERNALERROR>     return self.repr_instance(x, level)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 60, in repr_instance
INTERNALERROR>     s = _format_repr_exception(exc, x)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 23, in _format_repr_exception
INTERNALERROR>     exc_info, obj.__class__.__name__, id(obj)
INTERNALERROR>   File "/usr/local/lib/python3.8/site-packages/_pytest/_io/saferepr.py", line 56, in repr_instance
INTERNALERROR>     s = repr(x)
INTERNALERROR>   File "/Users/stiflou/Documents/projets/apischema/tests/test_pytest.py", line 6, in __repr__
INTERNALERROR>     raise
INTERNALERROR> RuntimeError: No active exception to reraise

============================ no tests ran in 0.09s ============================
```

## Test case

Minimal reproducing test file (`test_pytest.py`), taken from the original report:

```python
class SomeClass:
    def __getattribute__(self, attr):
        raise
    def __repr__(self):
        raise
def test():
    SomeClass().attr
```

Running pytest on this file yields an `INTERNALERROR` instead of a reported failure for `test_pytest.py::test`.

## Code example

The key ingredients are in the class from the test case above:

- `__repr__` raises an exception (here a bare `raise` with no active exception, which produces `RuntimeError: No active exception to reraise`).
- `__getattribute__` also raises, so attribute access such as `obj.__class__` fails as well.

The test triggers a failure through attribute access on an instance (`SomeClass().attr`). While building the failure report, pytest calls `saferepr` on the `self` argument of the traceback frames, and that call leads to the crash.

## Version and environment

- OS: macOS (`platform darwin`)
- Python: 3.8.1 (Homebrew, `/usr/local/opt/python@3.8/bin/python3.8`)
- pytest: 5.4.1
- py: 1.8.1
- pluggy: 0.13.1
- Plugins: asyncio-0.10.0, mock-3.0.0, cov-2.8.1