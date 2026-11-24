## Summary

When pylint runs with `--recursive=y`, the `ignore-paths` option set in `pyproject.toml` has no effect. Files under `src/gen/`, which match the configured `ignore-paths` pattern, are still linted and reported.

## Steps to reproduce

1. Create a project with a `src/` directory that contains Python modules, including auto-generated modules in `src/gen/` (in the report: `about.py`, `design.py`, `resources_rc.py`, `settings.py`, `update_checker.py`).
2. Add this configuration to `pyproject.toml`:
   ```toml
   [tool.pylint.MASTER]
   ignore-paths = [
     # Auto generated
     "^src/gen/.*$",
   ]
   ```
3. From the project root, run:
   ```shell
   pylint --recursive=y src/
   ```
4. Look at the reported modules in the output.

## Observed behavior

Pylint lints and reports messages for every module under `src/gen/` (`about`, `design`, `resources_rc`, `settings`, `update_checker`), as well as for modules outside that directory (for example `region_selection`). The `ignore-paths` setting appears to be ignored entirely.

The output shows file paths with Windows-style backslash separators (for example `src\gen\about.py`).

## Expected behavior

Files matching `ignore-paths` (`src\gen\*`) should not be checked when running with `--recursive=y`.

## Stack trace / error output

No stack trace occurs. Below is an excerpt of the pylint output from the original report. Most of the repeated messages for `src\gen\*` are omitted.

```shell
************* Module region_selection
src\region_selection.py:170:0: R0914: Too many local variables (17/15) (too-many-locals)
************* Module about
src\gen\about.py:2:0: R2044: Line with empty comment (empty-comment)
src\gen\about.py:4:0: R2044: Line with empty comment (empty-comment)
src\gen\about.py:57:0: C0301: Line too long (504/120) (line-too-long)
src\gen\about.py:12:0: C0103: Class name "Ui_AboutAutoSplitWidget" doesn't conform to '_?_?[a-zA-Z]+?$' pattern (invalid-name)
...
************* Module design
src\gen\design.py:2:0: R2044: Line with empty comment (empty-comment)
...
************* Module resources_rc
src\gen\resources_rc.py:1:0: C0302: Too many lines in module (2311/1000) (too-many-lines)
...
************* Module settings
src\gen\settings.py:2:0: R2044: Line with empty comment (empty-comment)
...
************* Module update_checker
src\gen\update_checker.py:2:0: R2044: Line with empty comment (empty-comment)
...
src\gen\update_checker.py:1:0: R0401: Cyclic import (AutoSplit -> menu_bar -> error_messages) (cyclic-import)

--------------------------------------------------------------------------
Your code has been rated at -158.32/10 (previous run: -285.20/10, +126.88)
```

## Test case

This test case is derived from the reproduction in the report:

- **Setup:** a project with `src/` containing at least one Python file, and `src/gen/` containing at least one Python file. `pyproject.toml` contains `[tool.pylint.MASTER]` with `ignore-paths = ["^src/gen/.*$"]`.
- **Action:** run `pylint --recursive=y src/` from the project root.
- **Assertion:** the output contains no messages for files under `src/gen/` (`src\gen\` on Windows).
- **Currently:** the assertion fails, because messages for `src\gen\*.py` are reported.

## Code example

Configuration used (`pyproject.toml`):

```toml
[tool.pylint.MASTER]
ignore-paths = [
  # Auto generated
  "^src/gen/.*$",
]
```

Command used:

```shell
pylint --recursive=y src/
```

## Version and environment

- pylint 2.14.1
- astroid 2.11.5
- Python 3.9.6 (tags/v3.9.6:db3ff76, Jun 28 2021, 15:26:21) [MSC v.1929 64 bit (AMD64)]
- OS: Windows 10.0.19044
- Additional dependencies: none reported