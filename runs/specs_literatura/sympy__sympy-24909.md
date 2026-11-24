## Summary

Multiplying the `milli` prefix by a unit (e.g. `milli*W`) evaluates to the number `1` instead of milliwatts (`mW`). The reverse order, `W*milli`, returns an unevaluated product. The reporter has seen this with watts (`W`) and volts, and does not know which other units are affected.

## Steps to reproduce

1. Start a Python session (the reporter used IPython) with SymPy installed.
2. Import the prefix and unit:
   ```python
   from sympy.physics.units import milli, W
   ```
3. Evaluate `milli*W == 1`.
4. Evaluate `W*milli`.

## Observed behavior

- `milli*W == 1` returns `True`, so `milli*W` evaluates to the number `1`.
- `W*milli` returns `watt*Prefix(milli, m, -3, 10)`.
- The reporter saw the same problem with volts.

## Expected behavior

`milli*W` should evaluate to milliwatts (`mW`), not to `1`.

## Stack trace / error output

No exception is raised. The reported session output is:

```
In [1]: from sympy.physics.units import milli, W
In [2]: milli*W == 1
Out[2]: True
In [3]: W*milli
Out[3]: watt*Prefix(milli, m, -3, 10)
```

## Test case

Minimal test based on the reporter's session:

```python
from sympy.physics.units import milli, W

def test_milli_times_unit_is_not_one():
    # Reported: evaluates to True; expected milli*W to represent milliwatts (mW)
    assert (milli*W == 1) is False
```

## Code example

```python
from sympy.physics.units import milli, W

milli*W == 1   # True (unexpected)
W*milli        # watt*Prefix(milli, m, -3, 10)
```

## Version and environment

- SymPy: 1.11.1-1 (Arch Linux package)
- Python: 3.10.9
- OS: Arch Linux