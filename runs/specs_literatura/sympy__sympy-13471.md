## Summary

Unpickling a SymPy expression that contains a Float fails across Python versions. If the expression is pickled in Python 2 and loaded in Python 3, `pickle.loads` raises a `ValueError` in `sympy/core/numbers.py`.

## Steps to reproduce

1. Use SymPy at git commit `3546ac7` (master at the time of the report).
2. In Python 2.7, create the expression `x + 1.0`, where `x = sympy.symbols("x")`.
3. Pickle it with protocol 2 (`pickle.dumps(x + 1.0, 2)`) and write the result to stdout.
4. Pipe that output into Python 3.6.
5. In Python 3.6, read the bytes from stdin and call `pickle.loads` on them.

The whole sequence as a single shell command:

```sh
python2 -c 'import pickle; import sympy; x = sympy.symbols("x"); print pickle.dumps(x + 1.0, 2)' | python3 -c 'import pickle; import sys; print(pickle.loads(sys.stdin.buffer.read()))'
```

## Observed behavior

Loading the pickle in Python 3 fails with `ValueError: invalid literal for int() with base 16: '1L'`. The error is raised in `Float.__new__` (`sympy/core/numbers.py`, line 1045) while it handles the pickled float data.

## Expected behavior

An expression with a float that was pickled in Python 2 should load in Python 3 without error, giving the same expression (`x + 1.0`).

## Stack trace / error output

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/alex/git/VU/sympy/sympy/core/numbers.py", line 1045, in __new__
    num[1] = long(num[1], 16)
ValueError: invalid literal for int() with base 16: '1L'
```

## Test case

This minimal test comes from the report's reproduction command. It needs both Python 2 and Python 3 with SymPy installed:

```sh
# Step 1 (Python 2.7): produce the pickle
python2 -c 'import pickle; import sympy; x = sympy.symbols("x"); print pickle.dumps(x + 1.0, 2)' > expr.pickle

# Step 2 (Python 3.6): load it; currently raises ValueError
python3 -c 'import pickle; import sys; print(pickle.loads(sys.stdin.buffer.read()))' < expr.pickle
```

The test passes if step 2 loads the expression without raising an exception.

## Code example

The code from the report that triggers the error:

```python
# Python 2
import pickle
import sympy
x = sympy.symbols("x")
print pickle.dumps(x + 1.0, 2)
```

```python
# Python 3
import pickle
import sys
print(pickle.loads(sys.stdin.buffer.read()))
```

## Version and environment

- SymPy: git commit `3546ac7` (master at the time of the report)
- Pickling side: Python 2.7
- Unpickling side: Python 3.6
- Pickle protocol: 2
- Operating system: Not provided in the original report.