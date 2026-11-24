## Summary

Passing an unrecognized command-line option to pylint (e.g. `pylint -Q`) correctly reports `E0015: Unrecognized option found`, but pylint then also prints a Python traceback ending in `pylint.config.exceptions._UnrecognizedOptionError`. The traceback is unexpected and not user-friendly.

## Steps to reproduce

1. Install pylint `2.14.0-dev0` (with astroid `2.11.3`, Python `3.10.0b2`).
2. Run pylint with an option it does not recognize:
   ```shell
   pylint -Q
   ```
3. Look at the console output.

## Observed behavior

Pylint prints the expected `unrecognized-option` message:

```
************* Module Command line
Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)
```

It then prints a full Python traceback for an uncaught `_UnrecognizedOptionError`, raised from `_config_initialization` in `pylint/config/config_initialization.py` (see the stack trace below).

## Expected behavior

- The `E0015` line (`Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)`) is useful and should still be shown.
- No Python traceback should be printed for an unrecognized option.
- The reporter suggests a user-friendly message instead, such as a usage hint. For comparison, mypy prints:
  ```
  $ mypy -Q
  usage: mypy [-h] [-v] [-V] [more options; see below]
              [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT] [files ...]
  mypy: error: unrecognized arguments: -Q
  ```

## Stack trace / error output

```
************* Module Command line
Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)
Traceback (most recent call last):
  File "/Users/markbyrne/venv310/bin/pylint", line 33, in <module>
    sys.exit(load_entry_point('pylint', 'console_scripts', 'pylint')())
  File "/Users/markbyrne/programming/pylint/pylint/__init__.py", line 24, in run_pylint
    PylintRun(argv or sys.argv[1:])
  File "/Users/markbyrne/programming/pylint/pylint/lint/run.py", line 135, in __init__
    args = _config_initialization(
  File "/Users/markbyrne/programming/pylint/pylint/config/config_initialization.py", line 85, in _config_initialization
    raise _UnrecognizedOptionError(options=unrecognized_options)
pylint.config.exceptions._UnrecognizedOptionError
```

## Test case

Minimal check based on the reproduction command:

```shell
pylint -Q 2>&1 | tee output.txt
# Expected: output contains the E0015 message
grep -q "E0015: Unrecognized option found: Q (unrecognized-option)" output.txt
# Expected: output contains no traceback (currently fails)
! grep -q "Traceback (most recent call last)" output.txt
```

## Code example

Not provided in the original report. The reproduction needs only the command line `pylint -Q`; no source file or configuration is involved.

## Version and environment

```
pylint 2.14.0-dev0
astroid 2.11.3
Python 3.10.0b2 (v3.10.0b2:317314165a, May 31 2021, 10:02:22) [Clang 12.0.5 (clang-1205.0.22.9)]
```

- pylint run from a development checkout inside a virtualenv (paths in the traceback: `/Users/markbyrne/venv310/...`, `/Users/markbyrne/programming/pylint/...`).
- OS: Not provided in the original report (the paths and Clang build suggest macOS, but this is not stated).
- Configuration / additional dependencies: Not provided in the original report.