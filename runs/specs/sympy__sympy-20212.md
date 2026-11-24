# Spec: Make `0**-oo` evaluate to `zoo` as documented for `Pow`

## Objective

In SymPy 1.5.1, evaluating `0**-oo` returns `0`. The `Pow` class documentation says it should return `zoo` (`ComplexInfinity`):

| expr | value | reason |
| :-- | :-- | :-- |
| `0**-oo` | `zoo` | This is not strictly true, as 0**oo may be oscillating between positive and negative values or rotating in the complex plane. It is convenient, however, when the base is positive. |

**Goal:** Automatic evaluation of `Pow` with base zero and exponent negative infinity should return `zoo`. This would match:
- the documented behaviour, and
- the existing rule that zero raised to a negative number gives `zoo` (e.g. `0**-1 → zoo`).

**Users:** SymPy users who rely on the documented special-value table for `Pow`, and code that relies on consistent treatment of `0**(negative)`.

**Acceptance criteria (user-level):**
- `S.Zero**S.NegativeInfinity` returns `S.ComplexInfinity`.
- `Pow(S.Zero, S.NegativeInfinity)` returns `S.ComplexInfinity`.
- The other documented special values are unchanged, including `0**oo → 0`.
- The behaviour and the documentation agree. Any wording change to the doc row must be agreed first (see Open Questions).

## Assumptions

1. The documentation is correct and the code is wrong. The fix makes the code match the docs, not the other way around.
2. The bug is in automatic evaluation of `Pow` for a zero base and `S.NegativeInfinity` exponent. The likely location is `Pow.__new__` and/or a numeric `_eval_power` method. This is **unverified**: I have no repository access.
3. The fix targets the current SymPy development branch, not a 1.5.x backport.
4. `evaluate=False` must keep returning an unevaluated `Pow`.
5. The reason text in the doc row refers to `0**oo` while the row is about `0**-oo`. I assume this is a documentation typo and the intended meaning is unchanged.
6. Other places with their own zero/infinity power handling are out of scope unless the user-facing result for `0**-oo` depends on them. Examples: `Float` zero, `mpmath`, and `limit`.

## Tech Stack

- Python, SymPy (issue reported on 1.5.1). The supported Python versions for the target branch are **unknown**.
- Key classes named in the issue: `Pow`, `ComplexInfinity` (`zoo`), `oo` / `-oo`.

## Commands

**Unknown.** These are not given in the issue and I have no repository access.

- Build: unknown (likely not needed for a pure-Python change)
- Test: unknown. It should run the core power/numbers test modules and the docstring doctests for `Pow`.
- Lint / code-quality check: unknown
- Dev / REPL: unknown

## Project Structure

**Unknown.** I have no repository access.

- The source file defining `Pow` and its docstring table: unknown (presumed to be in SymPy's core package).
- The source files for numeric singletons (`Zero`, `NegativeInfinity`, `ComplexInfinity`): unknown.
- The test file(s) for `Pow` evaluation: unknown.

## Code Style

Follow the existing SymPy core conventions. No snippet is available from the issue. Expected properties:
- Compare against singletons via `S.Zero`, `S.NegativeInfinity`, `S.ComplexInfinity`.
- Special cases follow the existing pattern used for neighbouring cases in the documented table.

## Testing Strategy

- **Framework:** SymPy's existing test runner (exact command unknown).
- **Regression unit tests** in the existing `Pow` / numbers tests:
  - `S.Zero**S.NegativeInfinity == S.ComplexInfinity`
  - `Pow(S.Zero, S.NegativeInfinity) == S.ComplexInfinity`
  - `0**-oo` written with a Python int base, which sympifies to `S.Zero`, also gives `zoo`
  - Unchanged neighbours: `0**oo == 0`, `0**-1 == zoo`, `0**0 == 1`, `oo**-1 == 0`
  - `Pow(0, -oo, evaluate=False)` stays unevaluated
- **Doctests:** the `Pow` docstring table must still pass doctests, if it is doctested.
- **Full core test suite** must pass, so that no other result silently depended on `0**-oo == 0`.

## Boundaries

- **Always:**
  - Add a regression test for the reported case.
  - Run the core test suite and the `Pow` doctests before committing.
  - Keep the documented table and the behaviour in sync.
- **Ask first:**
  - Changing behaviour for `Float(0)**-oo` or for symbolic zero-valued bases.
  - Changing results from `limit`, `series`, or `mpmath`.
  - Rewording the documentation row beyond fixing the `0**oo` typo.
  - Backporting to 1.5.x.
- **Never:**
  - "Fix" the issue by changing the documentation to say `0`, without approval.
  - Remove or loosen existing tests that fail after the change. Investigate them instead.
  - Alter the semantics of other entries in the special-value table.

## Success Criteria

1. `S.Zero**S.NegativeInfinity`, `Pow(S.Zero, S.NegativeInfinity)` and `sympify("0**-oo")` all return `zoo`.
2. All other entries in the `Pow` special-value table still evaluate to their documented values.
3. New regression tests cover cases 1–2 and pass. The full existing core test suite and the `Pow` doctests pass.
4. The doc row for `0**-oo` is internally consistent: either the reason text refers to `0**-oo`, or the wording is confirmed intentional.

## Open Questions

1. Should `Float(0.0)**-oo` (and `0.0**-oo` after sympification) also return `zoo`, or something else, such as `zoo` or float infinity, to match the float semantics used elsewhere?
2. What about a symbol known to be zero (e.g. assumptions imply zero), or an expression that simplifies to zero? Are these in scope, or only the literal `S.Zero`?
3. Is the reason text "0**oo may be oscillating…" a typo for `0**-oo`? Should it be corrected in the same change?
4. Should `-oo` written as `Mul(-1, oo)` in unevaluated form be covered, or only `S.NegativeInfinity`?
5. What is the target branch or release? Is a backport to the 1.5.x line wanted?
6. Which test and lint commands, and which file locations, should be used? These are unknown without repository access.
7. Does any downstream code (e.g. `limit`, `series`, `nsimplify`) currently rely on `0**-oo == 0`? Should those results change if they do?