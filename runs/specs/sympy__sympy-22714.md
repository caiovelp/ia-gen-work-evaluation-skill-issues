# Spec: `Point2D` construction must not fail under a global `evaluate(False)` context

## Objective

Constructing a `Point2D` with real, numeric coordinates inside a `with sympy.evaluate(False):` block raises `ValueError: Imaginary coordinates are not permitted.`. The same input works in two other cases:

```python
sp.S('Point2D(Integer(1),Integer(2))')                  # works
sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)  # works
```

It fails here:

```python
import sympy as sp
with sp.evaluate(False):
    sp.S('Point2D(Integer(1),Integer(2))')              # ValueError
```

**Users affected:** anyone who parses or builds geometry objects while a global non-evaluation context is active.

**Root area (from the traceback):**
- `sympy/core/sympify.py` (`sympify`) calls `sympy/parsing/sympy_parser.py` (`parse_expr`, then `eval_expr`).
- That calls `sympy/geometry/point.py` `Point2D.__new__` (line ~912), which calls `Point.__new__`.
- `Point.__new__` raises at line ~153 with `'Imaginary coordinates are not permitted.'`.

**Desired behaviour:** the imaginary-coordinate validation in `Point.__new__` gives the same result whatever the global evaluation state. Real coordinates are accepted. Genuinely imaginary coordinates are still rejected.

**Acceptance criteria:**
1. With `evaluate(False)` active, `sp.S('Point2D(Integer(1),Integer(2))')` returns a `Point2D` with coordinates `1` and `2` and raises no error.
2. The two forms that already work keep working and give equivalent results.
3. With `evaluate(False)` active, direct construction works: `Point2D(1, 2)`, `Point(1, 2)` and `Point3D(1, 2, 3)` all succeed.
4. Imaginary coordinates still raise `ValueError('Imaginary coordinates are not permitted.')`, both with and without `evaluate(False)`. Examples: `Point(1, I)` and `Point2D(I, 2)`.
5. No existing geometry or parsing tests regress.

## Assumptions

1. **Suspected cause (hypothesis, not verified).** The validation at `point.py:153` uses an expression whose result changes under global `evaluate(False)`. A likely example is a call like `im(coord)`. Under `evaluate(False)` such a call may return an unevaluated, truthy object instead of `0`. That would make a real coordinate look imaginary.
2. **Global flag vs. keyword.** `sympify(..., evaluate=False)` passes `evaluate` to `parse_expr`, which rewrites the code. The `with evaluate(False)` context instead sets a global flag that also affects calls made inside `Point.__new__`. This difference is why only the context-manager form fails.
3. **Scope of the fix.** The fix belongs in `sympy/geometry/point.py`, in the coordinate validation. It does not belong in `sympify` or `parse_expr`.
4. **Other checks.** Other checks in `Point.__new__` may be sensitive to the global flag in the same way. Examples could include zero or dimension handling, or float conversion. These are in scope only if they break the acceptance criteria above.
5. **Unevaluated arguments.** Under `evaluate(False)`, coordinates may stay unevaluated. Point still validates them, and does not skip validation entirely.
6. **Version.** The reporter uses Python 3.8. The exact SymPy version is not given.

## Tech Stack

- Python (the reporter uses 3.8; the supported range is unknown)
- SymPy (version unknown, a recent master is assumed)

## Commands

All commands are unknown because they cannot be seen in the issue:

- **Build:** unknown (pure Python, likely no build step)
- **Test:** unknown (a test runner such as `pytest` or `bin/test` is likely, but not confirmed)
- **Lint:** unknown
- **Repro:** the snippet in the Objective section, run in a Python interpreter

## Project Structure

Known from the traceback:

```
sympy/core/sympify.py            → sympify entry point
sympy/parsing/sympy_parser.py    → parse_expr / eval_expr
sympy/geometry/point.py          → Point, Point2D (and presumably Point3D)
```

Test locations are unknown. A geometry test module is likely, for example `sympy/geometry/tests/test_point.py`, but this is unconfirmed.

## Code Style

Unknown. Follow the style of the surrounding code in `sympy/geometry/point.py`.

## Testing Strategy

- Add regression tests next to the existing Point tests (location to be confirmed). They should cover:
  - Parsing `Point2D(...)` via `S`/`sympify` inside `with evaluate(False)`.
  - Direct construction of `Point`, `Point2D` and `Point3D` inside `with evaluate(False)`.
  - The negative case: imaginary coordinates still raise under both evaluation modes.
- Run the full geometry and parsing test suites to check for regressions.
- Unit level is enough. No integration or e2e tests are needed.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue before changing any code.
  - Keep the existing error message text.
  - Run the geometry and parsing tests.
- **Ask first:**
  - Changing the semantics of the global `evaluate` context.
  - Modifying `sympify` or `parse_expr`.
  - Changing the public `Point` constructor signature or its `evaluate` keyword behaviour.
- **Never:**
  - Remove or weaken the imaginary-coordinate check.
  - Delete or skip failing tests.
  - Silently change behaviour when `evaluate=True`.

## Success Criteria

- The reproduction snippet runs without error and returns `Point2D(1, 2)`.
- Every acceptance criterion in the Objective section passes as an automated test.
- The existing test suite passes with no new failures.

## Open Questions

1. Which SymPy version or branch should the fix target?
2. Under `evaluate(False)`, should `Point` also keep its coordinates unevaluated? Or should it apply its usual normalisation, such as converting floats to rationals or simplifying, even when the global flag is off?
3. Should other geometry entities that build Points (for example `Line`, `Segment`, `Polygon`) be audited for the same global-flag sensitivity, or is that out of scope?
4. How should symbolic coordinates whose realness is unknown behave under `evaluate(False)`? Should they keep their current treatment, which is presumably to accept them?
5. What are the project's exact test and lint commands, and where are the Point tests located?