## Summary
`pylint` fails on a package directory without an `__init__.py` when that directory contains a module with the same name as the directory (for example, `a/a.py`). Pylint reports a parse error because it looks for the missing `a/__init__.py`. This also breaks module resolution for other modules linted in the same run. Renaming `a/a.py` to another name (for example, `a/c.py`) makes the problem go away.

## Steps to reproduce
**Scenario 1: linting the directory alone**
1. Create this layout, with all files empty:
   ```
   .
   `-- a/
       |-- a.py
       `-- b.py
   ```
   Note that there is no `a/__init__.py`.
2. Run `pylint a`.
3. Observe the `F0010` parse error.
4. For comparison, run `mv a/a.py a/c.py`, then run `pylint a` again. It succeeds with no output.

**Scenario 2: side effects on module resolution**
1. Using the layout above (with `a/a.py` present), add a top-level file `r.py`:
   ```
   .
   |-- a
   |   |-- a.py
   |   `-- b.py
   `-- r.py
   ```
   `r.py` contains:
   ```python
   from a import b
   ```
2. Run `pylint -E r`. It runs fine.
3. Run `pylint -E r a`. It fails for both module `r` and module `a`.
4. For comparison, rename `a/a.py` to `a/c.py`. After that, `pylint -E r a` works perfectly.

## Observed behavior
- With `a/a.py` present, `pylint a` fails while searching for an `a/__init__.py` file that does not exist. It reports `F0010` (parse-error).
- With `a/a.py` present, `pylint -E r a` reports two errors:
  - A spurious `E0611` (no-name-in-module) for `from a import b` in `r.py`.
  - The same `F0010` parse error for module `a`.
- `pylint -E r` on its own works fine.
- If `a/a.py` is renamed (for example, to `a/c.py`), both commands succeed.
- Running `touch a/__init__.py` also works around the problem. The reporter says this should no longer be necessary.

## Expected behavior
- `pylint a` should succeed when `a/a.py` is present, without requiring an `a/__init__.py`.
- `pylint -E r a` should succeed, as it does when the inner module has a different name.

## Stack trace / error output
Output of `pylint a`:
```
$ pylint a
************* Module a
a/__init__.py:1:0: F0010: error while code parsing: Unable to load file a/__init__.py:
[Errno 2] No such file or directory: 'a/__init__.py' (parse-error)
$
```

Output of `pylint -E r a`:
```
************* Module r
r.py:1:0: E0611: No name 'b' in module 'a' (no-name-in-module)
************* Module a
a/__init__.py:1:0: F0010: error while code parsing: Unable to load file a/__init__.py:
[Errno 2] No such file or directory: 'a/__init__.py' (parse-error)
```

## Test case
This minimal shell reproduction is derived from the report:
```sh
mkdir a
touch a/a.py a/b.py
echo "from a import b" > r.py

pylint a          # expected: success; observed: F0010 parse-error for a/__init__.py
pylint -E r       # works fine
pylint -E r a     # expected: success; observed: E0611 in r.py and F0010 for a

mv a/a.py a/c.py
pylint a          # succeeds
pylint -E r a     # succeeds
```

## Code example
Contents of `r.py`:
```python
from a import b
```
All files under `a/` (`a.py`, `b.py`) are empty.

## Version and environment
```
pylint 3.0.0a3
astroid 2.5.6
Python 3.8.5 (default, Jan 27 2021, 15:41:15)
[GCC 9.3.0]
```
The operating system is not provided in the original report.