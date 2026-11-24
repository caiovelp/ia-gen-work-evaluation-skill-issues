# Spec: Correct `Mod(x**n, x)` auto-evaluation for non-integer bases

## Objective

`Mod`'s automatic evaluation currently simplifies `Mod(p, q)` to `0` when `p` is a power whose base equals `q` and whose exponent is an Integer. This is only valid when the base is known to be an integer. For example, `1.5**2 % 1.5 == 0.75`, not `0`. As a result, `Mod(x**2, x)` returns `0` for a plain `Symbol('x')`, which has no integer assumption. The result is wrong for some substitutions of `x`.

**Goal:** `Mod` should only auto-simplify to `0` when the simplification is mathematically valid for every value the symbols' assumptions allow.

**Users:** Anyone using SymPy's `Mod`, and code that relies on it, such as simplification, `%` on expressions, and the solvers.

**Acceptance criteria (user-level):**
- `Mod(x**2, x)` with `x = Symbol('x')` (no assumptions) stays unevaluated. It must not return `0`.
- `Mod(x**2, x)` with `x = Symbol('x', integer=True)` still returns `0`.
- Substituting a non-integer numeric value into an unevaluated result gives the numerically correct value. For example, `Mod(x**2, x).subs(x, Rational(3, 2))` equals `Rational(3, 4)`.
- The other existing zero-shortcuts (`p == q`, `p == -q`, `p.is_integer and q == 1`) keep their current behaviour. Fixing their validity is out of scope unless an Open Question is resolved otherwise.

## Assumptions

1. The project is SymPy, and the faulty logic is the `eval` classmethod of the `Mod` class. Its location in the repository is **unknown** because it is not shown in the issue.
2. The shown condition is the only place causing this incorrect shortcut.
3. The issue's numeric example (`x = S(1.5)`) returns `0.75` because `x**2` is evaluated to the Float `2.25` before `Mod` sees a `Pow`. That numeric result is already correct. The real bug is the **symbolic** case, where the shortcut fires for a base with unknown integrality.
4. "Integer base" should be checked with SymPy's assumption system (`base.is_integer` being `True`). When it is `None` (unknown), the expression should be left unevaluated rather than simplified.
5. The fix should be minimal and limited to the `Pow`-with-base-equal-to-`q` branch.
6. Adding a regression test to SymPy's existing test suite for `Mod` is expected.

## Tech Stack

- Python, SymPy core (`Mod`, `Pow`, `S`, `Symbol`, the assumptions system).
- Supported Python and SymPy versions: **unknown**.

## Commands

All of these are **unknown** because the issue shows none of them:
- Build: not applicable (pure Python), or unknown.
- Test: unknown. Presumably SymPy's test runner or pytest, run on the `Mod`/arithmetic test module.
- Lint: unknown.

## Project Structure

- Source file containing `Mod.eval`: **unknown**.
- Test file covering `Mod`: **unknown**.

## Code Style

- Follow the existing style of the surrounding `Mod.eval` condition, a compound boolean returning `S.Zero`.
- Use SymPy assumption queries (`.is_integer`, `.is_Integer`) consistently with the existing code. The existing code is the only snippet available:

  ```python
  if (p == q or p == -q or
          p.is_Pow and p.exp.is_Integer and p.base == q or
          p.is_integer and q == 1):
      return S.Zero
  ```

## Testing Strategy

- **Framework:** SymPy's existing test suite. The exact runner and location are unknown.
- **Regression tests to add:**
  - `Mod(x**2, x)` with no assumptions on `x`: result is not `S.Zero`.
  - `Mod(x**2, x)` with `x` integer: result is `S.Zero`.
  - Substitution check: `Mod(x**2, x).subs(x, Rational(3, 2)) == Rational(3, 4)`.
  - Numeric sanity check: `Mod(S(1.5)**2, S(1.5)) == 0.75` still holds.
- **Non-regression:** the full existing `Mod` test suite must pass unchanged. Any existing test that asserts `Mod(x**2, x) == 0` for a non-integer symbol is itself wrong and must be flagged for review, not silently changed.

## Boundaries

- **Always:**
  - Keep the change confined to the incorrect shortcut.
  - Add regression tests.
  - Run the existing `Mod` tests.
- **Ask first:**
  - Changing the other shortcut branches (`p == -q`, negative exponents, `q == 0`).
  - Changing behaviour for non-integer but rational bases.
  - Altering other `Mod` simplification paths.
  - Modifying existing tests' expected values.
- **Never:**
  - Return `0` when its correctness depends on unknown assumptions.
  - Remove or weaken failing tests without approval.
  - Introduce new dependencies.

## Success Criteria

1. `Mod(Symbol('x')**2, Symbol('x'))` does not evaluate to `0`.
2. `Mod(Symbol('x', integer=True)**2, Symbol('x', integer=True))` evaluates to `0`.
3. `Mod(x**2, x).subs(x, Rational(3, 2)) == Rational(3, 4)` for a plain symbol `x`.
4. New regression tests exist for criteria 1–3 and pass.
5. The existing `Mod` test suite passes. Any expected-value changes are listed and justified.

## Open Questions

1. **Negative exponents:** `p.exp.is_Integer` also matches negative exponents. For example, `Mod(x**-2, x)` with an integer `x` is generally not `0`. Should the condition also require `p.exp.is_positive`, or should this be a separate issue?
2. **Exponent `0` / base `0`:** `x**0 == 1`, so `Mod(1, x)` is not `0` in general. Does `Pow` auto-evaluation make this unreachable, or does it need an explicit guard? Also, what is the intended result when `q` may be zero (`Mod(0, 0)` → `nan`)?
3. **Other shortcuts:** Should `p == q` and `p == -q` also be guarded against `q == 0`, or is that out of scope?
4. **Integrality check:** Should the check be `base.is_integer` (assumption-based, `True` only), or should other cases also qualify, such as `q` being an integer and the exponent ≥ 1?
5. **Test location and commands:** Where do the `Mod` tests live, and what is the exact command to run them?
6. **Downstream behaviour:** Do any downstream callers (simplify, solvers) currently rely on `Mod(x**n, x) == 0` for symbols without assumptions, and is that behaviour change acceptable?