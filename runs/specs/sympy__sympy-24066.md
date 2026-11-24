# Spec: `_collect_factor_and_dimension` must recognize dimensionless function arguments

## Objective

`UnitSystem._collect_factor_and_dimension()` (called here as `SI._collect_factor_and_dimension`) does not recognize that a function argument such as the exponent of `exp(...)` is dimensionless. It fails when the argument's dimension is equivalent to `Dimension(1)` but is not written that way.

**Reproduction (from the issue):**

```python
from sympy import exp
from sympy.physics import units
from sympy.physics.units.systems.si import SI

expr = units.second / (units.ohm * units.farad)
dim = SI._collect_factor_and_dimension(expr)[1]

assert SI.get_dimension_system().is_dimensionless(dim)   # passes

buggy_expr = 100 + exp(expr)
SI._collect_factor_and_dimension(buggy_expr)
# ValueError: Dimension of "exp(second/(farad*ohm))" is
# Dimension(time/(capacitance*impedance)), but it should be Dimension(1)
```

**Observed behavior:**
- The dimension system correctly reports that `time/(capacitance*impedance)` is dimensionless.
- `_collect_factor_and_dimension` handles `exp(expr)` by passing the argument's raw dimension (`time/(capacitance*impedance)`) up as the dimension of the whole function call.
- The `Add` handling then compares that dimension with the dimension of `100`, which is `Dimension(1)`. They do not match structurally, so a `ValueError` is raised.

**Expected behavior:**
- If a function argument's dimension is dimensionless according to the unit system's dimension system, treat it as `Dimension(1)`.
- So `exp(second/(farad*ohm))` has dimension `Dimension(1)`.
- So `100 + exp(second/(farad*ohm))` evaluates without error and has dimension `Dimension(1)`.

**Users:** People who use `sympy.physics.units` to check dimensions of physical formulas. RC-circuit expressions like `exp(-t/(R*C))` are a typical case.

## Assumptions

1. The method under test is `UnitSystem._collect_factor_and_dimension` in SymPy's units package. I believe it lives in `sympy/physics/units/unitsystem.py`, but I have not seen the repository, so this path is unverified.
2. The faulty logic is the branch that handles `Function` instances (e.g. `exp`). It returns the arguments' dimensions without checking whether they are dimensionless in the dimension system. Other branches (`Add`, `Mul`, `Pow`, `Derivative`) are not the root cause, although `Add` is where the error surfaces.
3. "Dimensionless" means `DimensionSystem.is_dimensionless(dim)` returns `True`. That is the API the issue already uses. No new definition of dimensionlessness is introduced.
4. The fix should apply to every `Function`, not only `exp`. Examples include `sin`, `cos` and `log`.
5. Arguments that are genuinely dimensional, e.g. `exp(units.second)`, are out of scope. Their behavior (currently: return the argument's dimension) should not change in this issue.
6. Factor (scale) computation for functions stays the same. Only the reported dimension changes.
7. The `Add` mismatch check is not loosened. It continues to raise for truly incompatible dimensions.

## Tech Stack

- Python, SymPy (`sympy.physics.units`, `sympy.physics.units.systems.si`)
- Supported Python and SymPy versions: **unknown** (not stated in the issue)

## Commands

All unknown; none are given in the issue.

- Build: unknown (pure Python, likely none)
- Test: unknown (SymPy commonly uses `bin/test` or `pytest`; the exact invocation has not been verified)
- Lint: unknown
- Reproduce: run the snippet above in a Python interpreter with the SymPy checkout on the path

## Project Structure

Unknown; I have no repository access. Likely relevant locations (unverified):

- `sympy/physics/units/unitsystem.py`: `UnitSystem._collect_factor_and_dimension`
- `sympy/physics/units/dimensions.py`: `DimensionSystem.is_dimensionless`
- `sympy/physics/units/tests/`: existing unit tests for the units package

## Code Style

Follow the existing SymPy conventions in the surrounding module. I have no code snippet beyond the issue's reproduction to cite.

## Testing Strategy

- **Level:** Unit tests in the units package's existing test module. The exact file is unknown, likely near the existing `_collect_factor_and_dimension` tests.
- **Regression test:** The issue's reproduction, asserting that `SI._collect_factor_and_dimension(100 + exp(second/(farad*ohm)))` returns dimension `Dimension(1)` and raises no error.
- **Additional cases:**
  - `exp(expr)` alone returns dimension `Dimension(1)`.
  - At least one other function with an equivalent-dimensionless argument (e.g. `sin(expr)`) returns `Dimension(1)`.
  - A function with a plainly dimensionless argument (e.g. `exp(2)`) is unchanged at `Dimension(1)`.
  - `100 + units.second` (a truly incompatible `Add`) still raises `ValueError`.
- **Coverage:** The existing units test suite must pass unchanged.

## Boundaries

**Always:**
- Use the dimension system's `is_dimensionless` to decide dimensionlessness.
- Add the regression test from the issue.
- Run the existing units test suite before considering the change done.

**Ask first:**
- Changing behavior for functions with genuinely dimensional arguments, e.g. raising an error for `exp(second)`.
- Changing the `Add` dimension-equality check or the public `get_dimensional_expr` behavior.
- Changing the method's return signature.

**Never:**
- Special-case only `exp` or only this specific unit combination.
- Suppress or weaken the `Add` `ValueError` for truly incompatible dimensions.
- Remove or modify existing tests to make them pass.

## Success Criteria

1. The issue's reproduction script runs to completion without raising.
2. `SI._collect_factor_and_dimension(exp(second/(farad*ohm)))[1] == Dimension(1)`.
3. `SI._collect_factor_and_dimension(100 + exp(second/(farad*ohm)))[1] == Dimension(1)`.
4. The same holds for at least one other elementary function (e.g. `sin`) with an equivalent-dimensionless argument.
5. `SI._collect_factor_and_dimension(100 + units.second)` still raises `ValueError`.
6. The scale factors returned for the cases above match the values before the fix.
7. All pre-existing tests in the units package pass.

## Open Questions

1. Should functions with **dimensional** arguments (e.g. `exp(second)`) raise an error, or keep their current permissive behavior? This spec assumes no change.
2. For multi-argument functions where some arguments are dimensionless and others are not, what dimension should be reported? The current tuple-of-dimensions behavior is assumed to be kept for non-dimensionless arguments.
3. Should `get_dimensional_expr` (if it has a parallel `Function` branch) get the same fix, or is it out of scope?
4. Should the related `Pow` handling of exponents (e.g. `2**(second/(farad*ohm))`) also be checked for the same problem?
5. Which test command and which test file should hold the regression test? Both are unknown without repository access.
6. Should the result be normalized to `Dimension(1)` exactly, or is any dimension for which `is_dimensionless` is `True` acceptable to callers?