## Summary

`UnitSystem._collect_factor_and_dimension` (called here as `SI._collect_factor_and_dimension`) raises a `ValueError` when adding quantities whose dimensions are equivalent but written differently. In `a1*t1 + v1`, the term `a1*t1` has dimension `acceleration*time`, which is equivalent to `velocity`. The function does not treat these as the same dimension and rejects the addition.

## Steps to reproduce

1. Import `sympy.physics.units` and the SI unit system (`sympy.physics.units.systems.si.SI`).
2. Define a quantity `v1` with dimension `units.velocity` and scale factor `2 * meter / second`.
3. Define a quantity `a1` with dimension `units.acceleration` and scale factor `-9.8 * meter / second**2`.
4. Define a quantity `t1` with dimension `units.time` and scale factor `5 * second`.
5. Build the expression `expr1 = a1*t1 + v1`.
6. Call `SI._collect_factor_and_dimension(expr1)`.

## Observed behavior

The call raises:

```
ValueError: Dimension of "v1" is Dimension(velocity), but it should be Dimension(acceleration*time)
```

## Expected behavior

`acceleration*time` is dimensionally equivalent to `velocity`, so `a1*t1 + v1` is a valid addition. `_collect_factor_and_dimension` should recognize the two dimensions as equivalent and process the expression without raising a `ValueError`.

## Stack trace / error output

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python\Python310\lib\site-packages\sympy\physics\units\unitsystem.py", line 179, in _collect_factor_and_dimension
    raise ValueError(
ValueError: Dimension of "v1" is Dimension(velocity), but it should be Dimension(acceleration*time)
```

## Test case

Minimal test derived from the reproduction snippet. It currently fails because a `ValueError` is raised:

```python
from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_collect_factor_and_dimension_equivalent_dims_in_add():
    v1 = units.Quantity('v1')
    SI.set_quantity_dimension(v1, units.velocity)
    SI.set_quantity_scale_factor(v1, 2 * units.meter / units.second)

    a1 = units.Quantity('a1')
    SI.set_quantity_dimension(a1, units.acceleration)
    SI.set_quantity_scale_factor(a1, -9.8 * units.meter / units.second**2)

    t1 = units.Quantity('t1')
    SI.set_quantity_dimension(t1, units.time)
    SI.set_quantity_scale_factor(t1, 5 * units.second)

    expr1 = a1*t1 + v1
    # Should not raise ValueError, since acceleration*time is equivalent to velocity
    SI._collect_factor_and_dimension(expr1)
```

## Code example

```python
from sympy.physics import units
from sympy.physics.units.systems.si import SI

v1 = units.Quantity('v1')
SI.set_quantity_dimension(v1, units.velocity)
SI.set_quantity_scale_factor(v1, 2 * units.meter / units.second)

a1 = units.Quantity('a1')
SI.set_quantity_dimension(a1, units.acceleration)
SI.set_quantity_scale_factor(a1, -9.8 * units.meter / units.second**2)

t1 = units.Quantity('t1')
SI.set_quantity_dimension(t1, units.time)
SI.set_quantity_scale_factor(t1, 5 * units.second)

expr1 = a1*t1 + v1
SI._collect_factor_and_dimension(expr1)
```

## Version and environment

- SymPy version: Not provided in the original report.
- Python: the traceback path (`C:\Python\Python310\...`) suggests Python 3.10 on Windows. The report does not state this explicitly.
- Affected file (from the traceback): `sympy/physics/units/unitsystem.py`, line 179, in `_collect_factor_and_dimension`