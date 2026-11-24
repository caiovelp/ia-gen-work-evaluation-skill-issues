# Spec: `(-x/4 - S(1)/12)**x - 1` and its `simplify` result disagree at `x = 9/5`

## Objective

`simplify()` is reported to turn `e = (-x/4 - 1/12)**x - 1` into an inequivalent expression, `f = 12**(-x)*(-12**x + (-3*x - 1)**x)`. At `x = 9/5` the two expressions give different numbers:

| Expression | Exact result (as reported) | `N(...)` (as reported) |
|---|---|---|
| `e.subs(x, 9/5)` | `-1 - 32*15**(1/5)*2**(2/5)/225` | `-1.32255049319339` (real) |
| `f.subs(x, 9/5)` | `-1 - 32*(-1)**(4/5)*60**(1/5)/225` | `-0.739051169462523 - 0.189590423018741*I` |

**Initial analysis. The faulty side may be the substitution, not `simplify`.**

- At `x = 9/5` the base of `e` is `-9/20 - 1/12 = -8/15`. That is negative, so `e.subs(x, 9/5)` should be the principal value of `(-8/15)**(9/5) - 1`.
- Computed by hand, `(-8/15)**(9/5) = (8/15)**(9/5) · e^{iπ·9/5}`, which is about `0.3226 · (0.809 − 0.588i)`, or about `0.261 − 0.190i`.
- So the principal value of `e(9/5)` is about `-0.739 − 0.190i`. This matches `f(9/5)`.
- The real value `-1.3226` equals `-1 − 0.3226`. That looks like `(-8/15)**(9/5)` was evaluated as `-(8/15)**(9/5)`, a real root, instead of the principal branch.
- Rewriting `(-(3x+1)/12)**x` as `(-3x-1)**x * 12**(-x)` is valid for any `x`, because 12 is positive. So `f` is plausibly equivalent to `e`.

**Working hypothesis (must be confirmed first):** the defect is in the automatic evaluation of a negative `Rational` raised to a non-integer `Rational` power, e.g. `Pow(Rational(-8, 15), Rational(9, 5))`. It is not in `simplify`. The issue title may misattribute the bug.

**Who benefits:** SymPy users who rely on exact power evaluation and on `simplify` keeping expressions equivalent.

**Success means:**
- Every exact and numeric form of `e` and `f` at `x = 9/5` agrees.
- They agree on the principal-branch value SymPy uses for `Pow`.

## Assumptions

1. SymPy defines `b**r` for negative real `b` and non-integer rational `r` as the principal value, `exp(r·log(b))` with `arg(b) = π`. Any automatic evaluation that returns a real root for such inputs is a bug.
2. The outputs in the issue are reproducible on the SymPy version used. That version is not stated.
3. The `N()` results in the issue are accurate. My hand computation, which agrees with the `f` value, relies on this.
4. `simplify`'s rewrite to `12**(-x)*((-3x-1)**x - 12**x)` is mathematically valid for all complex `x` under principal branches, because 12 is positive. If the fix is in power evaluation, `simplify` itself needs no change.
5. The fix should not change results for positive bases, integer exponents, or cases that already evaluate correctly.

## Tech Stack

- Python and SymPy, version unknown.
- Relevant SymPy objects (from the issue): `Symbol`, `S`/`Rational`, `Pow`, `simplify`, `subs`, `N`.
- The module or function where the faulty `Rational**Rational` evaluation lives is **unknown**. It must be found by investigation, not assumed.

## Commands

- Build: unknown (no build step expected for pure Python).
- Test: unknown. Presumably the project's standard test runner, but the exact command and flags are not visible.
- Lint: unknown.
- Reproduction is available from the issue and runs in a Python REPL:
  ```python
  from sympy import *
  x = Symbol('x')
  e = (-x/4 - S(1)/12)**x - 1
  f = simplify(e)
  a = S(9)/5
  N(e.subs(x, a)), N(f.subs(x, a))
  ```

## Project Structure

Unknown. No repository access. The locations of the power-evaluation code, the `simplify` code, and their test files must be identified before implementation.

## Code Style

Unknown beyond the issue snippet. Follow the existing SymPy conventions in whichever module is changed. Regression tests should use exact SymPy objects (`S`, `Rational`), not floats, wherever possible.

## Testing Strategy

- **Regression tests (required):**
  - `(-x/4 - S(1)/12)**x - 1` and its `simplify` result agree numerically at `x = 9/5`.
  - Both values match the principal value, approximately `-0.739051169462523 - 0.189590423018741*I`.
  - The exact value of `Pow(Rational(-8, 15), Rational(9, 5))` matches the principal branch numerically. Compare `N()` of the exact result with high-precision evaluation of `exp((9/5)·log(-8/15))`.
- **Property-style checks:** for a sample of negative rational bases and non-integer rational exponents (for example, odd and even denominators, and `p/q` with `|p| > q`), the exact auto-evaluated `Pow` agrees numerically with the principal value.
- **Non-regression:**
  - Positive rational bases with rational exponents are unchanged.
  - Negative bases with integer exponents are unchanged.
  - Existing power and simplify tests still pass.
- Test framework, test file locations and coverage expectations: unknown.

## Boundaries

- **Always:**
  - Confirm which side is wrong, `e.subs` or `f`, before changing code.
  - Check exact results against high-precision numerics.
  - Add regression tests that reproduce the issue.
- **Ask first:**
  - Changing the documented branch convention for powers of negative numbers.
  - Changing `simplify`'s output form if the root cause turns out to be elsewhere.
  - Any change that alters many existing expected outputs in the test suite.
- **Never:**
  - Mask the discrepancy by special-casing this expression.
  - Delete or loosen existing tests to make them pass.
  - "Fix" `simplify` to match a wrong numeric value.

## Success Criteria

- [ ] Root cause identified and documented. Specifically, it is confirmed (or refuted) that `Rational(-8,15)**Rational(9,5)` auto-evaluates to a real value instead of the principal value.
- [ ] `N(e.subs(x, S(9)/5))` and `N(f.subs(x, S(9)/5))` agree to working precision.
- [ ] The exact forms `simplify(e.subs(x, a))` and `simplify(f.subs(x, a))` are numerically equal.
- [ ] For every negative rational base `b` and non-integer rational `r` in the test sample, the auto-evaluated `b**r` is numerically equal to `exp(r*log(b))` with the principal log.
- [ ] If `simplify` itself is found to be at fault after all, `simplify(e)` returns an expression equivalent to `e` for all `x` (spot-checked at several real and complex points).
- [ ] No existing tests regress.

## Open Questions

1. Which SymPy version produced these outputs? Does it still reproduce on the current development version?
2. Should the issue be retitled or re-scoped if the root cause is confirmed to be negative-`Rational`-to-`Rational`-power evaluation rather than `simplify`?
3. Is the principal-branch convention the intended semantics for `Pow` with a negative rational base everywhere? Are there documented exceptions, for example real-root behaviour?
4. Are there other entry points that share the faulty logic, and should they be fixed in the same change? Examples are `Integer**Rational`, `Float` bases, and `nsimplify`/`powsimp` paths.
5. What are the test command, the test file locations, and the conventions for where regression tests for this area belong?