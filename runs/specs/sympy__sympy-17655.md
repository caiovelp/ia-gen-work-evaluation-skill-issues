# Spec: Commutative scalar multiplication for `sympy.geometry.Point`

## Objective

Make `scalar * Point` behave the same as `Point * scalar` in `sympy.geometry`, so that expressions using either order can be combined with other `Point` operations, such as addition.

**Who is affected:** SymPy users who do vector-style arithmetic on `Point` objects and put the scalar on the left (`2.0 * p`). This is ordinary mathematical notation.

**Current behaviour (from the issue):**

```python
from sympy import geometry as ge
import sympy

point1 = ge.Point(0, 0)
point2 = ge.Point(1, 1)

point1 + point2 * sympy.sympify(2.0)   # works
point1 + sympy.sympify(2.0) * point2   # raises GeometryError
```

- `sympy.sympify(2.0) * point2` does not produce a `Point`. It produces an unevaluated SymPy `Mul` (`2.0*Point2D(1, 1)`).
- `Point.__add__` (in `sympy/geometry/point.py`) then tries `Point(other, evaluate=False)` on that `Mul`. That raises `TypeError: Expecting sequence of coordinates, not Mul`, which is re-raised as `GeometryError: Don't know how to add 2.0*Point2D(1, 1) and a Point object`.

**Desired behaviour:** Both lines give the same result. In this example that is `Point2D(2.0, 2.0)`, or whatever the existing `point2 * 2.0` path returns, since that path is the reference.

**User stories / acceptance criteria:**

- As a user, I can write `k * p` for a SymPy number `k` and a `Point` `p`, and get a result equal to `p * k`.
- As a user, I can use `p1 + k * p2` and get the same result as `p1 + p2 * k`.
- Existing behaviour of `p * k`, `p1 + p2`, and other `Point` operations is unchanged.

## Assumptions

1. The reference semantics for `k * p` are exactly those of the existing `Point.__mul__` (`p * k`), including any simplification and the handling of float vs. rational coordinates. No new numeric semantics are being defined.
2. "Number" covers at least SymPy numbers produced by `sympify` (`Float`, `Integer`, `Rational`) and plain Python `int`/`float`. Whether symbolic scalars (e.g. `Symbol('x') * p`) are in scope is an open question.
3. The fix belongs in `sympy/geometry/point.py`, the only source file visible in the issue. Other files may need changes, which is unknown.
4. The bug affects `Point` in general (`Point2D` and `Point3D` and n-dimensional `Point`), not just `Point2D`.
5. The Python version in the report (3.6) is incidental. The fix must work on whatever Python versions SymPy currently supports (unknown).
6. Whether plain Python `2.0 * point2` (no `sympify`) already works is not stated in the issue. It is assumed to need verification, not assumed to be broken.

## Tech Stack

- Python (supported versions: unknown; the report used 3.6)
- SymPy, module `sympy.geometry`, class `Point` (and subclasses `Point2D`/`Point3D`)
- SymPy version in the report: unknown

## Commands

Unknown, since the repository is not visible. To be filled in from the SymPy project's contributor docs.

- Build: unknown
- Test: unknown (likely a pytest- or SymPy-test-runner invocation targeting the geometry tests, unconfirmed)
- Lint: unknown

## Project Structure

Known from the traceback:

```
sympy/geometry/point.py   → Point class: __new__, __add__, _normalize_dimension, __mul__
```

Unknown:
- The location of the geometry test file(s)
- Whether `Point` participates in SymPy's core operator dispatch (e.g. `_op_priority`, `sympify` hooks) via other modules

## Code Style

Unknown beyond what the traceback shows. Follow the existing conventions in `sympy/geometry/point.py`:
- Error messages use `GeometryError` with a descriptive message.
- Coordinates are combined element-wise, with `simplify` applied (as seen in `__add__`).

## Testing Strategy

- **Framework / location:** unknown (SymPy's existing geometry test module).
- **Regression tests to add (unit level):**
  - `sympify(2.0) * Point(1, 1) == Point(1, 1) * sympify(2.0)`
  - `Point(0, 0) + sympify(2.0) * Point(1, 1) == Point(0, 0) + Point(1, 1) * sympify(2.0)`
  - The same checks with an `Integer` and a `Rational` scalar
  - The same checks with plain Python `int` and `float` scalars
  - The same checks for a 3D point
  - The type of `k * p` is a `Point` (not `Mul`)
- **Non-regression:** The existing geometry test suite passes unchanged.
- Coverage expectations: unknown. At minimum, every new code path is exercised by the tests above.

## Boundaries

- **Always:**
  - Add regression tests reproducing the exact snippet from the issue.
  - Keep `p * k` behaviour byte-for-byte identical.
  - Run the full geometry test suite before submitting.
- **Ask first:**
  - Changing `Point.__add__` to accept or unwrap arbitrary `Mul` expressions, rather than making `k * p` produce a `Point`.
  - Changing SymPy core (`Expr`/`Mul`) dispatch or `_op_priority` behaviour that affects classes outside `geometry`.
  - Extending the scope to symbolic scalars or other operators (`/`, unary `-`, `-` with left scalar).
  - Changing the text or type of existing `GeometryError` messages.
- **Never:**
  - Change the result type or values of currently-working operations.
  - Remove or weaken existing tests.
  - Special-case only `Float` (`2.0`) when the issue is about scalars in general.

## Success Criteria

1. `point1 + sympy.sympify(2.0) * point2` returns the same value as `point1 + point2 * sympy.sympify(2.0)` and raises no exception.
2. For each scalar `k` in {`sympify(2.0)`, `sympify(2)`, `Rational(1, 2)`, `2`, `2.0`} and each point `p` in {`Point(1, 1)`, `Point(1, 2, 3)`}:
   - `k * p == p * k`
   - `isinstance(k * p, Point)`
3. All pre-existing `sympy.geometry` tests pass.
4. New regression tests covering criteria 1–2 are added and pass.

## Open Questions

1. Should symbolic scalars (`x * p` with `x = Symbol('x')`) also return a `Point`? Is this consistent with how `p * x` behaves today?
2. Does plain Python `2.0 * point2` (without `sympify`) currently work? If yes, why does the SymPy-number case differ? This determines whether the root cause is a missing reflected multiplication on `Point` or SymPy's `Expr.__mul__` taking precedence.
3. Should the same commutativity guarantee cover other mixed operators (`k / p` is likely invalid, but what about `-p`, or `k * p - q`)?
4. If a `Mul` containing a `Point` reaches `Point.__add__` by some other route, should it be supported? Or should it keep raising `GeometryError`, possibly with a clearer message?
5. What are the exact test and lint commands, the test file location, and the minimum supported Python version for the target SymPy branch?
6. Which SymPy version or branch should the fix target? The reported version is not given.