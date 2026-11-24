## Summary

The `ascii.qdp` reader in astropy only recognizes QDP commands written in upper case (for example `READ SERR 1 2`). QDP itself is not case sensitive and accepts lower-case commands such as `read serr 1 2`. Because many QDP files are written by hand, lower-case commands are common, and reading such files with `Table.read(..., format='ascii.qdp')` fails with a `ValueError`.

## Steps to reproduce

1. Create a file `test.qdp` with the following content (the command line is in lower case):
   ```
   read serr 1 2 
   1 0.5 1 0.5
   ```
2. Start Python and run:
   ```python
   from astropy.table import Table
   Table.read('test.qdp', format='ascii.qdp')
   ```
3. Observe that a `ValueError` is raised.
4. For comparison, run `qdp test.qdp` with the QDP program itself. It processes the file without problems.

## Observed behavior

A warning is printed, followed by a `ValueError` stating that the lower-case `read serr 1 2` line is an unrecognized QDP line. No table is returned.

## Expected behavior

The file should be read into a `Table` with errors, rather than crashing. QDP commands should be accepted regardless of case, as QDP itself does, so `read serr 1 2` should be treated the same as `READ SERR 1 2`.

## Stack trace / error output

The original report shortened the traceback (marked with `...`):

```
WARNING: table_id not specified. Reading the first available table [astropy.io.ascii.qdp]
Traceback (most recent call last):
...
    raise ValueError(f'Unrecognized QDP line: {line}')
ValueError: Unrecognized QDP line: read serr 1 2
```

## Test case

Minimal test case based on the reproduction in the report:

Input file `test.qdp`:
```
read serr 1 2 
1 0.5 1 0.5
```

Check:
```python
from astropy.table import Table
t = Table.read('test.qdp', format='ascii.qdp')
# Expected: reads successfully into a Table with errors (no ValueError)
```

The same file with the command written as `READ SERR 1 2` is the upper-case form the reader currently expects.

## Code example

```python
>>> from astropy.table import Table
>>> Table.read('test.qdp', format='ascii.qdp')
```

## Version and environment

- OS: macOS (darwin)
- Python 3.10.9 (main, Dec 7 2022, 02:03:23) [Clang 13.0.0 (clang-1300.0.29.30)]
- astropy 5.1
- Numpy 1.24.1
- pyerfa 2.0.0.1
- Scipy 1.10.0
- Matplotlib 3.6.3