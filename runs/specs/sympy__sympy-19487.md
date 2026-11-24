# Spec: `sign(x).rewrite(Abs)` in SymPy

## Assumptions
1. The target is SymPy's `sign` function, as named in the issue. Its module path is not given in the issue and is **unknown**.
2. The definition the issue cites is `sign(z) := z / Abs(z)` for non-zero complex `z`. The current behaviour is `sign(0) == 0`.
3. "Rewrite in terms of Abs" means calling `.rewrite(Abs)` through SymPy's standard rewrite mechanism. The issue does not say how a rewrite target is registered on a function, so that mechanism is **unknown** here.
4. The rewritten expression must be mathematically equivalent to the original `sign(x)` for every value of `x` that `x`'s assumptions allow, including zero. A rewrite that is wrong for some admissible inputs is not acceptable.
5. Changing `sign(0)` from `0` to `nan` is **out of scope** unless a maintainer explicitly approves it. That change would break existing behaviour, and the issue only raises it as a possibility ("Maybe").
6. `rewrite` should leave expressions that contain no `sign` unchanged, and it should rewrite each `sign` inside a larger expression.

## Objective
Let users express `sign(x)` in terms of `Abs`, so that this works:
```
>>> sign(x).rewrite(Abs)
 x
───
│x│
```
Today there is no such rewrite. The main difficulty is `x = 0`:
- `sign(0)` returns `0`.
- `0/Abs(0)` returns `nan`.

A plain `x/Abs(x)` is therefore only correct when `x` is known to be non-zero.

**Users:** SymPy users who simplify, integrate or otherwise manipulate expressions that contain `sign`, and who want an `Abs`-based form.

**Acceptance (user stories):**
- If `x` is known to be non-zero, `sign(x).rewrite(Abs)` returns `x/Abs(x)`.
- If `x` might be zero, the rewrite returns a form that is still correct at zero. The exact form is an open question (see below).
- Numeric arguments keep their current evaluation (`sign(0) == 0`). Rewriting already-evaluated numbers changes nothing.

## Tech Stack
- Python, SymPy. The versions and minimum supported Python version are **unknown** because they are not stated in the issue.
- No new dependencies are expected.

## Commands
None appear in the issue, so all are **unknown**. The likely shape is a pytest invocation on the test module for `sign`/`Abs`, but the exact paths and flags have not been confirmed.
- Build: unknown (pure Python, possibly none)
- Test: unknown
- Lint/code quality: unknown
- Doctests: unknown

## Project Structure
**Unknown.** These still need to be found:
- The module that defines `sign` and `Abs`
- The test module that covers them
- The location of the docs/docstring for `sign`

## Code Style
Follow the existing conventions in the module that defines `sign`. The issue shows no snippet beyond the REPL example above, so the conventions themselves are **unknown**. The docstring for `sign` should gain a `rewrite(Abs)` example in the same doctest style as the issue's example.

## Testing Strategy
- Framework: the project's existing test framework (**unknown**, probably pytest-compatible).
- Tests go in the existing test file for `sign`/`Abs` (path **unknown**).
- Test cases:
  - Non-zero symbol, e.g. `Symbol('x', nonzero=True)` or `positive=True`: `sign(x).rewrite(Abs) == x/Abs(x)`.
  - Generic symbol `x` with no assumptions: the result equals `sign(x)` when substituted at `x = 0` and at several non-zero real and complex values (e.g. `2`, `-3`, `I`, `1+I`).
  - Symbol known to be zero: the result is `0`, not `nan`.
  - Numeric arguments (`sign(0)`, `sign(-2)`, `sign(I)`): `.rewrite(Abs)` gives the same value as before.
  - Nested use: `(1 + sign(y)).rewrite(Abs)` rewrites the inner `sign`.
  - Regression: `sign(0)` still returns `0`.
- Docstring example passes as a doctest.

## Boundaries
- **Always:** Keep `rewrite(Abs)` exactly equivalent to `sign` on every admissible input. Add tests for the zero, non-zero and unknown-zero cases. Follow the existing rewrite conventions in the codebase.
- **Ask first:** Changing the value of `sign(0)`. Changing `Abs` or other functions' rewrite behaviour. Returning a `Piecewise` (or any other non-obvious form) for the unknown-zero case. Changing how `sign` simplifies or evaluates.
- **Never:** Return `x/Abs(x)` when `x` might be zero, because that silently produces `nan` where `sign` gives `0`. Remove or loosen existing tests for `sign` without approval.

## Success Criteria
1. `sign(x).rewrite(Abs)` returns `x/Abs(x)` when `x.is_zero is False`.
2. For any `x` with unknown zero-ness, the rewrite equals `sign(x)` after substitution at `0` and at non-zero values. The chosen form is the one agreed under Open Questions.
3. `sign(0)`, and every other existing evaluation of `sign`, is unchanged unless an explicit decision says otherwise.
4. The new tests pass, and the existing tests for `sign`, `Abs` and `rewrite` still pass.
5. The `sign` docstring documents the rewrite and its handling of zero.

## Open Questions
1. **Value of `sign(0)`:** Keep it `0` (assumed), or change it to `nan` to match `z/Abs(z)`? Changing it breaks backward compatibility and needs a maintainer decision.
2. **Unknown-zero arguments:** If `x` might be zero, what should the rewrite return?
   - (a) A `Piecewise`, such as `0` when `x == 0` and `x/Abs(x)` otherwise.
   - (b) `sign(x)` unchanged, meaning the rewrite only applies when `x` is known to be non-zero. The issue notes this would make the rewrite fail in most cases.
   - (c) Some other closed form.
3. Should rewrite targets other than `Abs` (for example `Piecewise`) be covered in the same change, or kept out of scope?
4. Do other functions defined in terms of `sign` need matching behaviour so that rewrites stay consistent?
5. What are the repository paths and test/lint commands? (Needed to fill in Commands and Project Structure.)