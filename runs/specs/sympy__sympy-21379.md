# Spec: `subs()` raises `PolynomialError` on hyperbolic functions of Piecewise arguments with real symbols

## Assumptions

1. The bug is in SymPy itself, not in user code. The reporter is on SymPy `1.8.dev`; the exact commit is unknown.
2. `expr.subs({1: 1.0})` on these expressions should succeed. The result should be the same as with non-real symbols, apart from the int → float replacement.
3. The failure depends on the cache. It happens on a fresh cache after `clear_cache()` and goes away on a repeated call. This suggests that some evaluation path, probably an assumptions query, raises during the first evaluation. Later calls reuse cached results.
4. The error comes from code that applies polynomial machinery to an expression containing `Piecewise`. The message "Piecewise generators do not make sense" points to the polys module. The exact call path is not confirmed from the issue alone.
5. A likely trigger is an assumption query on the hyperbolic function during reconstruction in `subs`. Examples are `is_real`, `is_zero`, `is_finite` or `is_extended_real` on `sinh`/`cosh`/`tanh`. Such a query may evaluate the argument's imaginary part modulo `pi` or something similar. This is a hypothesis and needs a traceback to confirm.
6. The fix should be general. Assumption queries and `subs` must not raise `PolynomialError` for `Piecewise` arguments. Special-casing only this one expression is not acceptable.
7. Any assumption query that cannot be decided should return `None` (unknown) rather than raise.

## Objective

Make `subs` work reliably on expressions such as `exp(sinh(Piecewise((x, y > x), (y, True)) / z))` when `x` and `y` are real. It should work regardless of cache state and must not raise `PolynomialError`.

**User:** SymPy users who rewrite expression trees in bulk, for example casting every integer atom to a float before `lambdify` with the TensorFlow backend.

**Reported reproduction (from the issue):**

```python
from sympy import *
from sympy.core.cache import clear_cache

x, y, z = symbols('x y z')
clear_cache()
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
expr.subs({1: 1.0})   # works

clear_cache()
x, y, z = symbols('x y z', real=True)
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
expr.subs({1: 1.0})   # PolynomialError: Piecewise generators do not make sense
expr.subs({1: 1.0})   # works on repeat (cache populated)
```

**Reported conditions:**

| Condition | Effect on the error |
|---|---|
| `sinh`, `cosh`, `tanh` as the hyperbolic function | Error occurs. The reporter's bullet list is ambiguous here; the MWE shows that `sinh` fails. |
| Remove the division by `z` | No error |
| Remove the outer `exp` | No error |
| Replace `exp` with another unary function such as `sin` or `log` | Error "stays for most" |
| `x` and `y` are real (`z` need not be) | Required for the error |
| Repeat the call without clearing the cache | No error |

## Tech Stack

- Python with SymPy `1.8.dev`. The exact commit, Python version and test runner version are unknown.
- Relevant areas, inferred from symptoms and not verified against the source:
  - `sympy.core` (`subs`, the assumptions system, cache)
  - `sympy.functions.elementary.hyperbolic` (`sinh`, `cosh`, `tanh` and their `_eval_is_*` methods)
  - `sympy.functions.elementary.piecewise`
  - `sympy.polys` (the source of `PolynomialError`)
  - possibly `sympy.core.mod` or the gcd helpers used during argument simplification

## Commands

Unknown. The repository is not visible.

- Build: unknown. SymPy is pure Python, so a build step is probably not needed.
- Test: unknown. Something like `bin/test` or `pytest` for the relevant test modules is likely, but the exact command is unconfirmed.
- Lint: unknown.

## Project Structure

Unknown beyond the module names listed under Tech Stack. The file paths of the hyperbolic, piecewise, polys and core assumption modules, and their tests, need confirming in the repository.

## Code Style

Unknown. Follow the conventions of the surrounding SymPy code. No snippet is available from the issue.

## Testing Strategy

- **Regression test** in the test module for the component where the fix lands (location unknown):
  - Call `clear_cache()` before building the expression, so the failure path runs on an empty cache.
  - Use `x, y` with `real=True` and `z` unrestricted, and the exact expression from the issue.
  - Assert that `expr.subs({1: 1.0})` does not raise.
- **Parametrized coverage:**
  - Hyperbolic functions: `sinh`, `cosh`, `tanh`.
  - Outer functions: `exp`, `sin`, `log`.
  - Include the variants the reporter says pass (no `/ z`, no outer function, non-real symbols) as controls.
- **Assumption-level test:** if the root cause is an assumption query, add a direct test. On a cleared cache, the relevant `is_*` property of the hyperbolic function of the Piecewise argument should return `True`, `False` or `None` without raising.
- **Existing suites:** the existing tests for hyperbolic functions, Piecewise, polys and core must still pass.

## Boundaries

- **Always:**
  - Reproduce on a cleared cache before and after the change.
  - Add regression tests.
  - Keep assumption queries non-raising: return `None` when the answer is unknown.
- **Ask first:**
  - Changing `PolynomialError` behaviour in `sympy.polys` globally.
  - Changing cache semantics.
  - Changing the documented behaviour of `subs` or of the assumptions system.
- **Never:**
  - Mask the error by catching broad exceptions in `subs` at the top level.
  - Special-case only the exact reported expression.
  - Remove or loosen existing tests to make the suite pass.

## Success Criteria

1. On a fresh cache with `x, y` real, `exp(sinh(Piecewise((x, y > x), (y, True)) / z)).subs({1: 1.0})` returns an expression and does not raise.
2. The same holds for `cosh` and `tanh`, and for outer functions `sin` and `log`.
3. The result is identical whether the cache is cold or warm.
4. The result is structurally equivalent to what the non-real-symbol case produces, apart from the int → float replacement.
5. Assumption queries such as `is_real` and `is_zero` on the affected subexpressions do not raise `PolynomialError`. They return a definite answer or `None`.
6. All new regression tests pass, and no existing tests regress.

## Open Questions

1. What is the full traceback? It would show which assumption handler or simplification step calls into polys with a `Piecewise` generator.
2. Which hyperbolic functions actually fail? The issue says "only happens with `cosh` or `tanh` in place of `sinh`", but the MWE fails with `sinh`.
3. What is the exact SymPy commit or version? Does the bug still reproduce on current master?
4. Where should the fix go?
   - (a) In the hyperbolic `_eval_is_*` methods, by guarding against non-polynomial arguments.
   - (b) In the helper that raises, such as `Mod` or gcd evaluation, by catching `PolynomialError` and leaving the expression unevaluated.
   - (c) Both.
5. Should `PolynomialError` raised from inside the assumptions system be treated as "unknown" in general, or only at specific call sites?
6. Are the trigonometric counterparts (`sin`, `cos` and `tan` of a Piecewise divided by a symbol) affected in the same way and in scope for this change?
7. Is the cache-dependence a separate bug to investigate, for example whether a partially computed assumption is cached? Or is it fully explained by the raising query?