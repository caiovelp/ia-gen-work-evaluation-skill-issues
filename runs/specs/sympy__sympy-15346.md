# Spec: `simplify()` should combine sin/cos products with Rational arguments

## Objective

`simplify()` already rewrites the symbolic form `sin(x)*sin(y) + cos(x)*cos(y)` as `cos(x - y)`. It does not do this when the arguments are numeric Rationals.

**Reported behaviour** (latest cloned SymPy, Python 3, Windows):

| Input | `simplify()` output today | Expected |
|---|---|---|
| `sin(x)*sin(y) + cos(x)*cos(y)` with `x, y` real symbols | `cos(x - y)` | `cos(x - y)` (no change) |
| `Rational(1,50) - Rational(1,25)` | `-1/50` | `-1/50` (no change) |
| `sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25)` | unchanged | `cos(1/50)` |
| `Matrix([sin(1/50), cos(1/50), 0]).dot(Matrix([sin(1/25), cos(1/25), 0]))` | unchanged | `cos(1/50)` |
| `acos(sin(1/50)*sin(1/25) + cos(1/50)*cos(1/25))` | unchanged | `1/50` |

`cos(1/50 - 1/25)` is `cos(-1/50)`, which equals `cos(1/50)` because cos is even. In the last row, 1/50 lies in [0, π], so `acos(cos(1/50))` equals `1/50`.

**Users affected:** anyone who runs `simplify` or `trigsimp` on expressions where the trig functions have concrete rational arguments. A common case is vector geometry: taking the angle between unit vectors built from rational angles.

**Success means:** the sum and difference identities are applied to numeric Rational arguments in the same way they are applied to symbolic arguments.

## Assumptions

1. The root cause is in SymPy's trig simplification pipeline, which `simplify` calls through `trigsimp`/`futrig` and the `fu` rules. Some guard or pattern there skips terms whose arguments are numbers rather than symbols. This has not been confirmed because the source code was not available.
2. The expected output for the core case is the canonical `cos(1/50)` and not `cos(-1/50)`. SymPy's automatic evaluation normally turns `cos(-a)` into `cos(a)`.
3. The `Matrix.dot` case is the same bug, because `dot` produces the same scalar expression. No Matrix-specific fix is expected.
4. The `acos` case does not need its own fix. It should resolve once the inner expression simplifies to `cos(1/50)`, assuming `acos(cos(r))` already evaluates to `r` for rational `r` in [0, π].
5. The analogous identities should also work with Rational arguments:
   - `sin(a)cos(b) ± cos(a)sin(b) → sin(a ± b)`
   - `cos(a)cos(b) − sin(a)sin(b) → cos(a + b)`
6. Integer and other exact numeric arguments probably share the same code path. Floats are out of scope.
7. The behaviour is not Windows-specific.

## Tech Stack

- Python 3. The minimum supported version is unknown.
- SymPy at the latest master; the exact commit is unknown.
- Probably relevant modules: `sympy.simplify.trigsimp` and `sympy.simplify.fu`. Not verified.

## Commands

Unknown, because the repository was not inspected. Likely candidates to confirm:

- Test: unknown (possibly `bin/test sympy/simplify` or `pytest sympy/simplify`)
- Doctest: unknown (possibly `bin/doctest`)
- Lint/quality: unknown

## Project Structure

Unknown. Presumed locations, to be confirmed:

- Simplification source: `sympy/simplify/` (trigsimp, fu)
- Tests: `sympy/simplify/tests/` (e.g. trigsimp/fu test files)

## Code Style

Unknown. Follow the existing SymPy conventions found in the module being modified. Regression tests should be plain `def test_...():` functions using `assert` equality on exact SymPy expressions.

## Testing Strategy

- **Unit and regression tests** in the existing trigsimp/fu test modules. Each one asserts exact expression equality:
  - `simplify(sin(R(1,50))*sin(R(1,25)) + cos(R(1,50))*cos(R(1,25))) == cos(R(1,50))`
  - The same expression built via `Matrix.dot`.
  - `simplify(acos(<that expr>)) == R(1,50)`
  - The sin sum/difference variants with Rational arguments.
- **Non-regression:**
  - The symbolic case still gives `cos(x - y)`.
  - The existing trigsimp/fu suites pass.
  - No significant slowdown in simplify benchmarks. The benchmark tooling is unknown.
- **Numerical sanity check:** before and after simplification, `.evalf()` gives equal values to high precision.

## Boundaries

- **Always:**
  - Keep exact arithmetic.
  - Add regression tests reproducing the issue.
  - Run the full simplify test suite.
- **Ask first:**
  - Changing the public signatures or default options of `simplify`, `trigsimp` or `fu`.
  - Changing which simplification is chosen for existing symbolic cases.
  - Any change with measurable performance impact on simplify.
- **Never:**
  - Convert the expression to floats to "simplify" it.
  - Special-case the literal values 1/50 or 1/25.
  - Weaken or delete existing tests.

## Success Criteria

1. `simplify(sin(R(1,50))*sin(R(1,25)) + cos(R(1,50))*cos(R(1,25)))` returns `cos(1/50)`.
2. The `Matrix.dot` version of the expression returns the same result.
3. `simplify(acos(...))` of that expression returns `1/50`.
4. The sin/cos sum and difference identities apply to Rational arguments generally, not only to the reported values.
5. All existing simplify, trigsimp and fu tests pass, and the symbolic examples keep their current outputs.
6. No meaningful performance regression in simplify on existing tests.

## Open Questions

1. Where exactly is the numeric-argument case filtered out? For example: a `has(Symbol)` or free-symbols check, a pattern requiring symbolic args, or eager evaluation of `a - b` changing the match. This needs investigation in `trigsimp`/`fu`.
2. Should the fix be in `trigsimp` (affecting `simplify` and `trigsimp`) or only in `fu`'s TR10i-style rule? Is calling `fu()` directly expected to behave the same?
3. Should other exact numeric arguments also be covered, such as Integers, `pi`-multiples and algebraic numbers like `sqrt(2)`? What about Floats?
4. Does `acos(cos(Rational))` already auto-evaluate for arguments in [0, π]? If not, is that in scope here or a separate issue?
5. For arguments where `a - b` produces a negative value, is `cos(|a - b|)` the required canonical output, or is any equivalent form acceptable?
6. What are the exact test and doctest commands, and is there a performance benchmark gate for simplify?