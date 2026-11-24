## Summary
`SI._collect_factor_and_dimension()` does not recognize that the argument of `exp()` is dimensionless when that argument is a unit expression whose dimension reduces to dimensionless (here `second / (ohm * farad)`). It raises a `ValueError` instead.

## Steps to reproduce
1. Import `exp`, `sympy.physics.units` and the `SI` unit system.
2. Build `expr = units.second / (units.ohm * units.farad)`.
3. Call `SI._collect_factor_and_dimension(expr)` and take the dimension (index `[1]`).
4. Confirm with `SI.get_dimension_system().is_dimensionless(dim)` that the dimension is dimensionless. The assertion passes.
5. Build `buggy_expr = 100 + exp(expr)`.
6. Call `SI._collect_factor_and_dimension(buggy_expr)`.

## Observed behavior
Step 6 raises a `ValueError`. The error says the dimension of `exp(second/(farad*ohm))` is `Dimension(time/(capacitance*impedance))` and that it should be `Dimension(1)`. This happens even though the dimension system confirms in step 4 that `time/(capacitance*impedance)` is dimensionless.

## Expected behavior
`SI._collect_factor_and_dimension()` should detect that the exponent `second/(farad*ohm)` is dimensionless and process `100 + exp(expr)` without raising an error.

## Stack trace / error output
```
ValueError: Dimension of "exp(second/(farad*ohm))" is Dimension(time/(capacitance*impedance)), but it should be Dimension(1)
```
(Full traceback not provided in the original report.)

## Test case
```python
from sympy import exp
from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_collect_factor_and_dimension_dimensionless_exponent():
    expr = units.second / (units.ohm * units.farad)
    dim = SI._collect_factor_and_dimension(expr)[1]
    assert SI.get_dimension_system().is_dimensionless(dim)

    buggy_expr = 100 + exp(expr)
    # Currently raises ValueError; expected to succeed
    SI._collect_factor_and_dimension(buggy_expr)
```

## Code example
```python
from sympy import exp
from sympy.physics import units
from sympy.physics.units.systems.si import SI

expr = units.second / (units.ohm * units.farad)
dim = SI._collect_factor_and_dimension(expr)[1]

assert SI.get_dimension_system().is_dimensionless(dim)

buggy_expr = 100 + exp(expr)
SI._collect_factor_and_dimension(buggy_expr)

# results in ValueError: Dimension of "exp(second/(farad*ohm))" is Dimension(time/(capacitance*impedance)), but it should be Dimension(1)
```

## Version and environment
Not provided in the original report.