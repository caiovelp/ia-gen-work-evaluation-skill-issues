# Spec: Fix incorrect `trigsimp` simplification of `cos(x) + sqrt(sin(x)**2)` for complex `x`

## Objective

`trigsimp` returns a result that is **not mathematically equivalent** to its input when given `cos(x) + sqrt(sin(x)**2)` with `x` a general (complex) symbol. It treats `sqrt(sin(x)**2)` as `sin(x)` and returns `cos(x) + sin(x)`. That rewrite is valid only on part of the domain, so the output is wrong for other values of `x`.

When `x` is declared real, the reporter says the result is correct. The expected correct result there is presumably `cos(x) + Abs(sin(x))`.

**Who is affected:** Any SymPy user who relies on `trigsimp` (and possibly `simplify`, which can call it) to return an equivalent expression. The reporter found this while writing teaching material, so wrong results here can mislead learners.

**What success looks like:**
- `trigsimp` never replaces `sqrt(f(x)**2)` with `f(x)` unless the assumptions on `x` justify it. More generally, it never applies `(z**a)**b → z**(a*b)` where that is invalid for the given assumptions.
- For complex `x`, the expression is either left alone or rewritten into a form that is truly equivalent.
- The real-`x` behavior that already works keeps working.

**Acceptance criteria (user-visible):**
1. With `x = Symbol('x')` (no assumptions), `trigsimp(cos(x) + sqrt(sin(x)**2))` does **not** return `cos(x) + sin(x)`. The result must equal the input for all complex `x`.
2. With `x = Symbol('x', real=True)`, `trigsimp(cos(x) + sqrt(sin(x)**2))` still returns a correct result. The expected form is `cos(x) + Abs(sin(x))`, but the exact form is to be confirmed.
3. Results that stay equivalent and that the current tests already check do not regress.

## Assumptions

1. The behavior described applies to the current development branch, not only to 1.5. The issue says "various versions, including 1.5", so the bug is assumed to still be present.
2. "General complex x" means a `Symbol` created with no assumptions.
3. The bad rewrite happens somewhere in the `trigsimp` pipeline, possibly in the `fu`-style transformation rules or in power/exponent handling. The exact location is **unknown** because the source has not been inspected.
4. The correct mathematical rule is `sqrt(z**2) == z` only when `z` is known to be nonnegative, or more generally when `z` lies in the principal-branch half-plane. For real `z`, `sqrt(z**2) == Abs(z)`. For general complex `z`, no simplification is valid in general.
5. Other even-power/root combinations (e.g. `sqrt(cos(x)**2)`, `(sin(x)**4)**(1/4)`, `sqrt(tan(x)**2)`) probably go through the same faulty path. The fix should cover them, not only the exact expression in the report.
6. `simplify` may show the same wrong result if it calls `trigsimp`. This is not confirmed.
7. Changing the output for complex inputs is acceptable. Returning a less "simplified" but correct expression is preferred over returning a wrong one.

## Tech Stack

- Python, SymPy (affected version reported: 1.5; current version unknown).
- Specific modules involved: **unknown**. Likely candidates are the trig simplification and `fu` modules, but this is unverified.

## Commands

All commands are **unknown** because the repository was not inspected. To be confirmed:
- Test: unknown (likely the project's standard test runner, applied to the trig simplification tests)
- Lint/style check: unknown
- Build: unknown / not applicable

Minimal reproduction, taken from the issue:
```python
from sympy import Symbol, cos, sin, sqrt, trigsimp
x = Symbol('x')
trigsimp(cos(x) + sqrt(sin(x)**2))          # observed: cos(x) + sin(x)  (wrong)

xr = Symbol('xr', real=True)
trigsimp(cos(xr) + sqrt(sin(xr)**2))        # reported correct (expected: cos(xr) + Abs(sin(xr)))
```

## Project Structure

**Unknown.** The exact paths for the trigsimp implementation and its tests still need to be identified. The fix should live in the simplification module where the faulty rewrite occurs, and the regression tests should go in that module's existing test file.

## Code Style

**Unknown.** Follow the conventions of the surrounding SymPy code. Regression tests should follow the existing pattern in the trigsimp test file, which has not been inspected.

## Testing Strategy

- **Regression tests (unit):**
  - Unassumed `x`: assert that `trigsimp(cos(x) + sqrt(sin(x)**2))` is not `cos(x) + sin(x)`. Also assert that the result is equivalent to the input. This can be checked with numeric evaluation at complex points where `sin(x)` lies in the left half-plane (e.g. `x = -1`, `x = 2 + I`). Note that `x = -1` is real but valid as a test point for an unassumed symbol.
  - Real `x`: assert the correct result. The expected value is `cos(x) + Abs(sin(x))`, pending confirmation.
  - Positive/restricted cases: if `x` carries assumptions that guarantee `sin(x) >= 0`, a simplification to `sin(x)` may be allowed. Test this only if such assumptions can actually be expressed.
  - Sibling cases: `sqrt(cos(x)**2)`, `sqrt(sin(x)**2)` alone, and higher even powers with matching roots.
- **Numerical equivalence check:** compare input and output at several random complex points to catch any other invalid rewrites in the same path.
- **Regression of existing behavior:** the full existing trigsimp/fu (and possibly simplify) test suites must still pass. If an existing test asserts an incorrect result of this kind, report it as an open question rather than silently changing it.
- Coverage expectations: unknown.

## Boundaries

- **Always:**
  - Keep results mathematically equivalent under the symbol's assumptions.
  - Add regression tests that reproduce the issue.
  - Run the existing simplification test suites.
- **Ask first:**
  - Changing the output of existing tests whose expected results are equivalent but different in form.
  - Changing public function signatures.
  - Altering behavior of general power simplification outside trig contexts (e.g. `powsimp`, `powdenest`), if the root cause turns out to be there.
  - Noticeable performance impact on trigsimp.
- **Never:**
  - Special-case the literal expression from the issue instead of fixing the underlying rule.
  - Delete or weaken existing tests to make them pass.
  - Introduce new rewrites that are only valid for real or positive arguments without checking assumptions.

## Success Criteria

1. `trigsimp(cos(x) + sqrt(sin(x)**2))` with unassumed `x` returns an expression that equals the input for all complex `x`. It must not return `cos(x) + sin(x)`.
2. The same expression with real `x` returns a correct result, expected to be `cos(x) + Abs(sin(x))`.
3. Analogous cases (`sqrt(cos(x)**2)`, other even power/root pairs of trig functions) are equally safe for complex arguments.
4. Numeric spot checks at complex points show equal values for input and output in all new tests.
5. All pre-existing tests in the affected modules pass, or any change to them has been explicitly approved.

## Open Questions

1. Which internal step produces the invalid `sqrt(sin(x)**2) → sin(x)` rewrite (e.g. a specific `fu` transformation, a `Pow` handling routine, `powdenest`/`powsimp` called with `force`-like behavior)? Where does the real-`x` path diverge?
2. Is the bug still present on the current development branch?
3. Does `simplify(cos(x) + sqrt(sin(x)**2))` also produce the wrong result? Should it be covered by the same fix and tests?
4. For unassumed `x`, what is the preferred output? Options are leaving `sqrt(sin(x)**2)` untouched, or some equivalent canonical form.
5. For real `x`, is `cos(x) + Abs(sin(x))` the exact expected output form?
6. Do other trigsimp methods (e.g. the `method=` options, if they exist in the current version) share the faulty path and need coverage?
7. Do any existing tests currently encode this incorrect behavior?
8. Repository commands, file paths, and test locations are all unknown and need to be filled in.