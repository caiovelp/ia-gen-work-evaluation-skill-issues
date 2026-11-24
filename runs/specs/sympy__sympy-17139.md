# Spec: Fix `TypeError` in `simplify(cos(x)**I)` from complex exponent comparison in `fu.py`

## Objective

`simplify()` crashes with `TypeError: Invalid comparison of complex I` when the expression contains a trig function raised to a non-real exponent, such as `cos(x)**I`.

**Reproduction (from the issue):**
```python
>>> from sympy import *
>>> x = Symbol('x')
>>> print(simplify(cos(x)**I))
TypeError: Invalid comparison of complex I
```

**Root cause (from the traceback):**

1. `simplify` → `trigsimp(deep=True)` → `futrig` → `_futrig` → `greedy(tree, objective=Lops)`.
2. That chain reaches `TR6` → `_TR56` → the inner rewrite function `_f` in `sympy/simplify/fu.py`.
3. At line 504, `_f` evaluates `if (rv.exp < 0) == True:`.
4. When `rv.exp` is `I`, the `<` operator itself raises `TypeError` (`sympy/core/expr.py`, `__lt__`). It does not return an unevaluated or false relational.
5. So the `== True` guard never gets a chance to run.

**Goal:** The `TR5`/`TR6` power rewrites in `fu.py` must not raise on powers whose exponent is non-real (complex, purely imaginary, or of unknown realness). They should leave such powers unchanged. `simplify`/`trigsimp` should then return a valid result instead of crashing.

**User:** SymPy users calling `simplify`, `trigsimp`, or the `fu` transforms directly on expressions with complex exponents.

**Acceptance criteria:**
- `simplify(cos(x)**I)` returns without raising. The result is mathematically equivalent to `cos(x)**I`, most likely `cos(x)**I` itself.
- `TR6(cos(x)**I)` and `TR5(sin(x)**I)` return their input unchanged and do not raise.
- Existing behaviour for real numeric exponents (positive, negative, even, odd, above or below `max`) is unchanged. All existing tests for `fu.py`, `trigsimp.py`, and `simplify.py` still pass.

## Assumptions

1. The fix belongs in `sympy/simplify/fu.py`, in `_TR56`'s inner function `_f`. It does not belong in `Expr.__lt__`, whose raising on complex comparisons is intentional.
2. Correct behaviour for a non-real exponent is "do not transform": return `rv` unchanged. Rewriting `cos(x)**2 → 1 - sin(x)**2` only makes sense for real (specifically integer) exponents.
3. Other comparisons in `_f` on `rv.exp` (for example against `max`, or parity and power checks) may raise the same way. The guard should cover all of them, not only line 504.
4. Other `fu.py` transforms may contain the same `(expr < 0) == True` pattern on exponents. They are in scope only if the same input (`cos(x)**I`, `sin(x)**I`) reaches them through `simplify`. A wider audit is listed as an open question.
5. The fix needs no public API change, no new dependency, and no change to `simplify`/`trigsimp` signatures.
6. Python and SymPy versions are not stated in the issue. The line numbers in the traceback refer to a specific, unknown revision.

## Tech Stack

- Python, SymPy. The exact versions are **unknown**.
- Modules involved (from the traceback): `sympy/simplify/fu.py`, `sympy/simplify/trigsimp.py`, `sympy/simplify/simplify.py`, `sympy/strategies/core.py`, `sympy/core/expr.py`.

## Commands

- Build: **unknown.** A pure-Python package is likely, but the issue does not say.
- Test: **unknown.** The issue does not show the project's test runner invocation.
- Lint: **unknown.**
- Repro: run the Python snippet in the Objective section in an interpreter with this SymPy checkout importable.

## Project Structure

Only what the traceback shows:
```
sympy/simplify/fu.py         → TR5/TR6/_TR56 trig power rewrites (site of the bug)
sympy/simplify/trigsimp.py   → trigsimp / futrig / _futrig (caller)
sympy/simplify/simplify.py   → simplify, bottom_up (entry point / traversal)
sympy/strategies/core.py     → greedy / minrule / chain_rl strategy combinators
sympy/core/expr.py           → Expr.__lt__ (raises on complex comparison)
```
Test file locations are **unknown**. They are presumably test modules alongside `sympy/simplify/`, but this is unconfirmed.

## Code Style

The repository is not visible, so no style snippet is available. Follow the conventions of the surrounding code in `fu.py`:
- Rewrite functions return `rv` unchanged when a transform does not apply.
- Relational checks are written as `(cond) == True` so that unevaluated relationals count as "not applicable". Note that this idiom does not protect against comparisons that raise, which is exactly this bug.

## Testing Strategy

- **Framework:** **unknown.** Use whatever the existing SymPy test suite uses.
- **Regression tests to add, placed next to the existing tests for `fu.py`, `trigsimp.py`, and `simplify.py`:**
  - `simplify(cos(x)**I)` does not raise and is equivalent to `cos(x)**I`.
  - `TR6(cos(x)**I) == cos(x)**I` and `TR5(sin(x)**I) == sin(x)**I`.
  - Possibly also other non-real exponents, such as `cos(x)**(2 + 3*I)` and `cos(x)**(I*y)`, plus a symbolic exponent of unknown realness, such as `cos(x)**y`, to confirm that one still does not raise.
- **Existing tests:** run the full `fu`, `trigsimp`, and `simplify` test modules to confirm there are no regressions in the real-exponent rewrites.
- **Level:** unit tests only. No integration-level changes are needed.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue before fixing it.
  - Keep real-exponent behaviour of `TR5`/`TR6` identical.
  - Run the existing simplify and trig test suites.
- **Ask first:**
  - Changing `Expr.__lt__` or other core comparison semantics.
  - Changing the public signatures of `TR5`/`TR6`/`_TR56`, `trigsimp`, or `simplify`.
  - Broadening the fix to other `fu.py` transforms not on the failing path.
- **Never:**
  - Swallow the error with a broad `try/except Exception` that could hide other bugs.
  - Remove or weaken existing tests.
  - Make `Expr.__lt__` silently return `False` for complex values.

## Success Criteria

1. `simplify(cos(x)**I)` completes without exception and returns an expression equivalent to `cos(x)**I`.
2. `TR6(cos(x)**I)` and `TR5(sin(x)**I)` return their input unchanged.
3. Non-real exponents such as `2 + 3*I` also do not raise in `TR5`/`TR6`.
4. All pre-existing tests in the `fu`, `trigsimp`, and `simplify` test modules pass unchanged.
5. New regression tests covering criteria 1–3 are committed and pass.

## Open Questions

1. **Exponent filter.** Should `_TR56` bail out for any exponent that is not a real number (`exp.is_real` is not `True`)? Or should it be stricter and only act on integer exponents (`exp.is_integer`)? The latter matches what the `pow`/`max` logic seems to assume.
2. **Expected output.** Is `cos(x)**I` unchanged the expected output of `simplify(cos(x)**I)`, or is some other canonical form preferred?
3. **Audit scope.** Should this fix include an audit of other `fu.py` transforms (and `trigsimp.py`) for the same `(expr < 0) == True` pattern on possibly-complex values, or should those be filed separately?
4. **Versions.** Which SymPy and Python versions must this fix target or be backported to?
5. **Commands.** What are the exact test and lint commands for this repository?