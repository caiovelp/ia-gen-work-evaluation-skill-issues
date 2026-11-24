# Spec: `UnitSystem._collect_factor_and_dimension` should accept equivalent dimensions in addition

## Objective

`SI._collect_factor_and_dimension` raises `ValueError` when an `Add` expression combines terms whose dimensions are physically equivalent but written differently. For example, `acceleration*time` and `velocity` should be accepted together.

**Reproduction (from the issue):**

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

**Observed:**

```
File ".../sympy/physics/units/unitsystem.py", line 179, in _collect_factor_and_dimension
ValueError: Dimension of "v1" is Dimension(velocity), but it should be Dimension(acceleration*time)
```

**Expected:** The call returns a `(factor, dimension)` tuple and does not raise. The factor is `-9.8*5 + 2 = -47` (in SI base scale). The dimension is one equivalent to `velocity` / `acceleration*time`.

**Users:** People using `sympy.physics.units` who add quantities with derived dimensions. This also covers public APIs that may call `_collect_factor_and_dimension` internally (unverified).

**User story:** As a user, when I add quantities whose dimensions reduce to the same base dimensions in the active unit system, I get a combined factor and dimension instead of a spurious dimension-mismatch error.

## Tech Stack

- Python. The traceback shows Python 3.10 on Windows.
- SymPy, `sympy.physics.units` package. Affected version: unknown.
- Classes involved, as named in the issue: `UnitSystem` via `SI`, `Quantity`, `Dimension`.

## Commands

- Build: unknown (none needed for pure Python, presumably)
- Test: unknown. The project test runner and invocation are not visible in the issue.
- Lint: unknown
- Repro: run the snippet above with a Python interpreter that imports the SymPy checkout under test.

## Project Structure

- `sympy/physics/units/unitsystem.py` contains `_collect_factor_and_dimension`. The `Add` dimension check raises at about line 179 in the reporter's version. This path comes from the traceback.
- `sympy/physics/units/systems/si.py` defines `SI`. This is inferred from the import path.
- Test location: unknown. It is presumably an existing units test module, which is not visible.

## Code Style

Unknown beyond the repro snippet. Follow the existing conventions in `unitsystem.py` and the surrounding SymPy code.

## Testing Strategy

- Add a regression test that reproduces the issue exactly. It should assert no exception and check the returned factor and dimension.
  - Factor equals `-47`, or the equivalent SymPy number. Exact numeric form (float vs. rational) is an open question.
  - The returned dimension is equivalent to `velocity` in the SI dimension system.
- Keep a negative test: adding truly incompatible dimensions, such as `velocity + time`, must still raise `ValueError`.
- Run the existing `sympy.physics.units` test suite to confirm no regressions. The command is unknown.
- Test level: unit tests only.

## Boundaries

- **Always:**
  - Keep the `ValueError` for genuinely incompatible dimensions.
  - Base equivalence on the active unit system's dimension system, not on purely symbolic equality.
  - Add a regression test.
- **Ask first:**
  - Changing the dimension that is returned. For example, returning the first term's dimension versus a canonical one may affect callers.
  - Changing the public API or behavior of `Dimension` or the dimension system.
  - Touching other branches of `_collect_factor_and_dimension`, such as `Mul`, `Pow`, `Function`, or `Derivative`.
- **Never:**
  - Remove or weaken the dimension check entirely.
  - Delete or modify existing tests to make them pass.
  - Hard-code SI-specific equivalences.

## Success Criteria

1. The reproduction snippet runs without raising.
2. It returns a factor numerically equal to `-47` and a dimension equivalent to `velocity` under `SI`.
3. Commutation: `v1 + a1*t1` (reversed order) also succeeds with the same factor and an equivalent dimension.
4. Additions of non-equivalent dimensions still raise `ValueError` with a descriptive message.
5. All existing `sympy.physics.units` tests pass.

## Assumptions

1. The unit system or its dimension system already provides a way to decide whether two dimensions are equivalent. For example, it may reduce both to base dimensions and compare their dependencies. This is unverified, since no repository access was available.
2. The bug is limited to the `Add` branch of `_collect_factor_and_dimension`, where dimensions are compared by direct equality.
3. The same comparison issue may exist in sibling code paths, such as a deprecated public `collect_factor_and_dimension` or the `Derivative`/`Function` branches. These are out of scope unless confirmed.
4. Returning the first addend's dimension is acceptable, as long as it is equivalent to the others.

## Open Questions

1. Which dimension should be returned for an `Add` of equivalent dimensions: the first term's dimension, a canonical or base-reduced form, or something else?
2. Should the same equivalence check apply to other places that compare dimensions, such as `Function` arguments or `Piecewise`?
3. Which SymPy version or branch should the fix target, and what is the test command and test file location?
4. Should the factor be checked as an exact value or with float tolerance, given the `-9.8` float input?
5. Is the private `_collect_factor_and_dimension` the intended entry point to fix, or is there a public wrapper that also needs changes or tests?