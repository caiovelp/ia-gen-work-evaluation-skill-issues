# Spec: Fix incorrect result from `apart` with a symbolic (non-decomposition) parameter

## Objective

`apart(expr, t)` returns a wrong result when the rational function contains a symbol other than the decomposition variable `t`.

Reproduction from the issue (SymPy 1.0, Python 3.6.0):

```python
from sympy import symbols
a = symbols('a', real=True)
t = symbols('t', real=True, negative=False)
bug = a * (-t + (-t + 1) * (2 * t - 1)) / (2 * t - 1)

bug.subs(a, 1).apart()    # -t + 1/2 - 1/(2*(2*t - 1))   (correct)
bug.subs(a, 1).apart(t)   # -t + 1/2 - 1/(2*(2*t - 1))   (correct)
bug.apart(t)              # -a*t                          (WRONG)
```

Working the math by hand:

- The numerator expands as `-t + (1 - t)(2t - 1) = -2t² + 2t - 1`.
- Dividing by `(2t - 1)` gives `-t + 1/2 - 1/(2(2t - 1))`.
- The correct result of `bug.apart(t)` is therefore `a*(-t + 1/2 - 1/(2*(2*t - 1)))`, or an equivalent expanded form such as `-a*t + a/2 - a/(2*(2*t - 1))`.

The current output `-a*t` drops both the constant part of the polynomial quotient and the entire proper-fraction part. It is mathematically wrong and not just a different form of the right answer.

**Who is affected:** anyone who calls `apart` (function or method) on a rational function whose coefficients involve other symbols. Results are silently wrong, with no error raised.

**What success means:** `apart(expr, x)` always returns an expression mathematically equal to `expr`, including when the coefficients contain free symbols other than `x`.

## Assumptions

1. The bug is in SymPy's `apart` (exposed as `sympy.apart` and `Expr.apart`). The exact module and file have not been verified because there is no repository access.
2. The bug still exists on the current development branch. This has only been confirmed for SymPy 1.0, as reported.
3. The assumptions on the symbols (`real=True`, `negative=False`) do not cause the bug. They are incidental and need to be confirmed.
4. **Working hypothesis, not verified:** when coefficients contain `a`, the polynomial domain becomes an integer-coefficient ring over `a` (e.g. `ZZ[a]`) rather than a field. Polynomial division or the gcd/cancel step in that ring may then discard non-integer quotient terms such as `1/2`, along with the remainder. With `a = 1`, the domain becomes `QQ` and the result is correct. Root-cause analysis must confirm or reject this hypothesis.
5. Any form that is mathematically equivalent is acceptable. A fully expanded or `a`-factored form is fine.
6. The fix should not change the public signature or the documented behavior of `apart`, apart from correcting wrong results.

## Tech Stack

- Python library: SymPy. The issue reports SymPy 1.0 on Python 3.6.0.
- The target branch and the supported Python versions are unknown.
- Key areas are inferred from the symptom only: the partial fraction code (`apart`), polynomial division, and polynomial domains. Their exact paths are unknown.

## Commands

The project's commands could not be seen. All of the following are **unknown** and must be taken from the repository's contributing docs or CI config:

- Build: unknown
- Test (full suite): unknown
- Test (targeted, partial-fraction tests): unknown
- Lint / code-quality check: unknown

The only verifiable action from the issue is running the reproduction snippet above in a Python session with SymPy importable.

## Project Structure

Unknown, because there is no repository access. The following must be located:

- The source module that implements `apart`.
- The test module that covers `apart`.
- The polynomial division and domain modules, if the root cause is there.

## Code Style

Unknown. Follow the existing conventions of the SymPy codebase as found in the module being changed. No snippet is available from the issue.

## Testing Strategy

- **Regression test (required):** add the exact expression from the issue and assert that `bug.apart(t)` equals the correct result. Check equality robustly, for example by asserting that `(result - expected)` simplifies to `0`, or that `result.subs(a, 1)` matches the known correct output. Do not depend on one particular printed form.
- **Invariant check:** for the regression case, and ideally for a few variants, assert that `together(result) - expr` or `cancel(result - expr)` reduces to `0`.
- **Variants to cover:**
  - The same expression with the symbol assumptions removed. This confirms or rules out assumption 3.
  - A symbolic coefficient on a denominator that is not monic, like `2t - 1` here. A leading coefficient other than 1 is the likely trigger.
  - A case where the polynomial quotient has rational, non-integer coefficients.
  - `apart` called without an explicit variable, if that path is valid for multivariate input. It may raise an error by design; this needs to be confirmed.
- **No regressions:** the existing `apart` tests and polynomial tests must keep passing.
- The test framework and file locations are unknown, beyond following the existing test module for `apart`.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Check results for mathematical equivalence, not exact printed form.
  - Run the existing `apart` and polynomial test suites.
- **Ask first:**
  - Changing behavior in shared polynomial division or domain code beyond what `apart` needs, since it may affect many other functions.
  - Changing the canonical output form of `apart` for inputs that already return correct results.
  - Changing the signature of `apart`.
- **Never:**
  - Special-case this specific expression.
  - Weaken or delete existing tests to make the suite pass.
  - Accept a fix that is checked only by visual inspection of the printed output.

## Success Criteria

1. `bug.apart(t)` (and `apart(bug, t)`) returns an expression equal to `a*(-t + 1/2 - 1/(2*(2*t - 1)))`. Concretely, `simplify(result - bug) == 0`, and the result has the partial-fraction structure: a polynomial part in `t` plus proper fractions in `t`.
2. `bug.apart(t).subs(a, 1)` equals `bug.subs(a, 1).apart(t)`, up to mathematical equivalence.
3. The variant tests listed under Testing Strategy pass.
4. A regression test reproducing the issue is committed and passes.
5. All existing tests for `apart` and the related polynomial code still pass.
6. The root cause is identified and documented in the PR, confirming or rejecting assumption 4. The fix addresses that root cause rather than the symptom.

## Open Questions

1. Does the bug reproduce on the current development branch, or was it already fixed after 1.0?
2. What is the exact root cause? Is it the coefficient domain (integer polynomial ring vs. field) in polynomial division, the cancel/gcd step, or something else in `apart`?
3. If the root cause is in shared polynomial division code, should it be fixed there, which affects other callers, or worked around locally inside `apart`?
4. Is there a preferred canonical output form for multivariate `apart` results: factored by `a`, or fully expanded per term?
5. What should `bug.apart()` do with no variable given on this multivariate input? Should it work, or raise an error asking for a variable?
6. Do the symbol assumptions (`real=True`, `negative=False`) play any role, or can they be dropped from the regression test?
7. Should `apart_list` and the `full=True` path of `apart` be checked for the same defect?
8. What are the project's test and lint commands, and which file paths should hold the regression test?