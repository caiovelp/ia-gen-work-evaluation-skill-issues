# Spec: `refine()` support for `arg()` under sign assumptions

## Objective

`refine()` simplifies `Abs(a)` to `a` under `Q.positive(a)`, but it leaves `arg(a)` unchanged under the same assumption. Because of this, expressions that depend on `arg()` do not simplify. A common example is the convergence condition `2*Abs(arg(a)) < pi` that `Integral(...).doit()` places inside a `Piecewise`.

**User:** someone who calls `refine(expr, assumptions)` to simplify results, such as integral results, using known properties of symbols.

**Goal:** `refine()` evaluates `arg(x)` when the assumptions determine it. Expressions that contain `arg()` should then simplify through normal evaluation, including the `Piecewise` from the issue.

Reproduction from the issue:

```python
>>> from sympy import *
>>> var('a,x')
>>> J = Integral(sin(x)*exp(-a*x),(x,0,oo))
>>> J.doit()
Piecewise((1/(a**2 + 1), 2*Abs(arg(a)) < pi), (Integral(exp(-a*x)*sin(x), (x, 0, oo)), True))
>>> refine(J.doit(), Q.positive(a))   # currently unchanged
>>> refine(abs(a), Q.positive(a))     # a  (works today)
>>> refine(arg(a), Q.positive(a))     # arg(a)  (should be 0)
```

**Acceptance criteria (user stories):**
- As a user, when I call `refine(arg(a), Q.positive(a))`, I get `0`.
- As a user, when I call `refine(arg(a), Q.negative(a))`, I get `pi`.
- As a user, when I call `refine(J.doit(), Q.positive(a))`, I get `1/(a**2 + 1)`.
- As a user, when the assumptions do not determine `arg(a)`, I get `arg(a)` back unchanged rather than a wrong value.

## Assumptions

1. The project is SymPy. The bug is in the assumptions-based `refine()` machinery, not in `Integral.doit()`.
2. `refine()` works through per-function handlers. A handler already exists for `Abs` and none exists for `arg`. This is inferred from the behaviour shown, not from the source.
3. The required values follow the standard definition of `arg` on the principal branch (−π, π]:
   - `arg(x) = 0` for positive real `x`
   - `arg(x) = pi` for negative real `x`
4. Once `arg(a)` refines to `0`, the condition `2*Abs(0) < pi` evaluates to `True` automatically. A `Piecewise` whose first condition is `True` then collapses to that branch. This depends on `refine()` recursing into the `Piecewise` arguments and on `Piecewise` re-evaluating after rebuild. Both still need to be verified.
5. No new public API is needed. Only `refine()`'s output changes.
6. The fix is limited to `arg`. Refining other functions, such as `re`, `im` and `sign`, is out of scope unless it is needed for the acceptance criteria.

## Tech Stack

- Python, SymPy. Supported Python and SymPy versions: **unknown** (not stated in the issue).
- Dependencies: none beyond what SymPy already uses (unknown). Adding new dependencies is not expected.

## Commands

The exact commands are **unknown**, because the issue does not show the repository tooling. To be filled in from the repository:

- Test: unknown (likely the project's standard test runner, targeted at the refine/assumptions tests)
- Lint / code quality: unknown
- Build: unknown
- Doctests: unknown

## Project Structure

**Unknown.** The repository was not visible. Paths to identify:

- The module that implements `refine()` and its per-function handlers
- The module that defines `arg`
- The test file(s) that cover `refine()`

## Code Style

**Unknown.** Follow the conventions of the existing `refine()` handlers, especially the existing `Abs` handler, which is the closest analogue. Specific rules for any new handler:

- Use `ask(Q.<predicate>(arg), assumptions)` to test the assumptions.
- Return a simplified expression only when the assumptions determine the result.
- Otherwise return the original expression or `None`, whichever convention the existing handlers use.

## Testing Strategy

- **Framework:** SymPy's existing test framework. The exact runner and location are unknown.
- **Unit tests** for `refine(arg(...), ...)`:
  - `Q.positive(a)` → `0`
  - `Q.negative(a)` → `pi`
  - No assumptions, `Q.real(a)` alone, `Q.complex(a)` alone → `arg(a)` unchanged
- **Integration test:** the exact scenario from the issue. `refine(Integral(sin(x)*exp(-a*x),(x,0,oo)).doit(), Q.positive(a))` should equal `1/(a**2 + 1)`.
- **Composite tests:**
  - `refine(Abs(arg(a)), Q.positive(a))` → `0`
  - `refine(2*Abs(arg(a)) < pi, Q.positive(a))` → `True`
- **Regression:** the existing refine and assumptions test suites still pass.
- **Coverage expectations:** unknown. At minimum, every new branch in the handler is exercised by a test.

## Boundaries

- **Always:**
  - Return only values that are mathematically guaranteed by the given assumptions.
  - Add tests for every new simplification.
  - Run the existing refine and assumptions tests before committing.
- **Ask first:**
  - Changing how `refine()` traverses or rebuilds `Piecewise` or relational objects.
  - Changing the definition or auto-evaluation of `arg` itself.
  - Extending the change to other functions (`re`, `im`, `sign`, etc.).
- **Never:**
  - Return `0` or `pi` when the assumptions only partially determine the argument.
  - Change the output of `Integral.doit()`.
  - Remove or weaken existing tests.

## Success Criteria

1. `refine(arg(a), Q.positive(a)) == 0`
2. `refine(arg(a), Q.negative(a)) == pi`
3. `refine(arg(a))` and `refine(arg(a), Q.real(a))` return `arg(a)`, because the result is not determined.
4. `refine(J.doit(), Q.positive(a)) == 1/(a**2 + 1)`, where `J = Integral(sin(x)*exp(-a*x),(x,0,oo))`.
5. All existing refine and assumptions tests pass.

## Open Questions

1. What should `refine(arg(a), Q.zero(a))` return? Is `arg(0)` defined in SymPy (for example `nan` or `0`), or should the expression be left unrefined?
2. Should `Q.real(a) & Q.nonzero(a)` yield anything? It cannot be resolved to a single value, but a `Piecewise` result is possible. Or should the expression stay unchanged? (Proposed: unchanged.)
3. Should other branch-related cases be handled in this change? Examples are `Q.imaginary(a)`, which gives `±pi/2` depending on the sign of `im(a)`, and `arg` of products or powers. Or should they be deferred?
4. Does `refine()` already recurse into `Piecewise` conditions and relationals? Will the `Piecewise` collapse once `arg` is handled, or is extra work needed there (see Assumption 4)?
5. Should this be extended to sibling functions that `refine()` may not handle (`re`, `im`, `sign`) as part of the same change, or tracked separately?
6. What are the repository's test and lint commands and file locations? (Commands and Project Structure are currently unknown.)