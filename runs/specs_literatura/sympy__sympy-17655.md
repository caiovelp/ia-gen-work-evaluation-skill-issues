## Summary

Adding a `sympy.geometry.Point` to the product of a number and another `Point` fails when the number is on the left (`number * point`). The same expression with the number on the right (`point * number`) works. With `sympy.sympify(2.0) * point2`, `Point.__add__` raises a `GeometryError`.

## Steps to reproduce

1. Import the modules and create two points:
   ```python
   from sympy import geometry as ge
   import sympy

   point1 = ge.Point(0, 0)
   point2 = ge.Point(1, 1)
   ```
2. Evaluate the expression with the number on the right. It works:
   ```python
   point1 + point2 * sympy.sympify(2.0)
   ```
3. Evaluate the same expression with the number on the left. It raises an exception:
   ```python
   point1 + sympy.sympify(2.0) * point2
   ```

## Observed behavior

- `point1 + point2 * sympy.sympify(2.0)` evaluates without error.
- `point1 + sympy.sympify(2.0) * point2` raises `GeometryError: Don't know how to add 2.0*Point2D(1, 1) and a Point object`.

The traceback shows that `sympy.sympify(2.0) * point2` evaluates to a `Mul` object (`2.0*Point2D(1, 1)`), not a `Point`. `Point.__add__` then tries to convert this `Mul` into a `Point`. That conversion raises `TypeError: Expecting sequence of coordinates, not 'Mul'`, which is re-raised as a `GeometryError`.

## Expected behavior

Both expressions should give the same result. `point1 + sympy.sympify(2.0) * point2` should work like `point1 + point2 * sympy.sympify(2.0)`.

## Stack trace / error output

```
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
~/.virtualenvs/test/lib/python3.6/site-packages/sympy/geometry/point.py in __add__(self, other)
    219         try:
--> 220             s, o = Point._normalize_dimension(self, Point(other, evaluate=False))
    221         except TypeError:

~/.virtualenvs/test/lib/python3.6/site-packages/sympy/geometry/point.py in __new__(cls, *args, **kwargs)
    128                 Expecting sequence of coordinates, not `{}`'''
--> 129                                        .format(func_name(coords))))
    130         # A point where only `dim` is specified is initialized

TypeError: 
Expecting sequence of coordinates, not `Mul`

During handling of the above exception, another exception occurred:

GeometryError                             Traceback (most recent call last)
<ipython-input-20-6dcbddac1ee2> in <module>
----> 1 point1 + sympy.sympify(2.0)* point2

~/.virtualenvs/test/lib/python3.6/site-packages/sympy/geometry/point.py in __add__(self, other)
    220             s, o = Point._normalize_dimension(self, Point(other, evaluate=False))
    221         except TypeError:
--> 222             raise GeometryError("Don't know how to add {} and a Point object".format(other))
    223 
    224         coords = [simplify(a + b) for a, b in zip(s, o)]

GeometryError: Don't know how to add 2.0*Point2D(1, 1) and a Point object
```

## Test case

Minimal test based on the snippet in the report:

```python
from sympy import geometry as ge
import sympy

def test_point_add_number_times_point():
    point1 = ge.Point(0, 0)
    point2 = ge.Point(1, 1)

    right = point1 + point2 * sympy.sympify(2.0)   # works
    left = point1 + sympy.sympify(2.0) * point2    # currently raises GeometryError

    assert left == right
```

## Code example

```python
from sympy import geometry as ge
import sympy

point1 = ge.Point(0, 0)
point2 = ge.Point(1, 1)

# Works
point1 + point2 * sympy.sympify(2.0)

# Raises GeometryError
point1 + sympy.sympify(2.0) * point2
```

## Version and environment

- SymPy version: Not provided in the original report.
- Python 3.6. This comes from the traceback path `~/.virtualenvs/test/lib/python3.6/site-packages/sympy/...`.
- The code was run in an IPython session (`<ipython-input-20-...>`) inside a virtualenv.
- Operating system: Not provided in the original report.