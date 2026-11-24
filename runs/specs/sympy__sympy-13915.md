# Spec: `subs` must not return a finite value when substitution makes a subexpression undefined

## Objective

**Problem.** In SymPy 1.1.1, substituting a value that makes a subexpression undefined can still give a finite, defined result. This result is mathematically wrong.

Reproduction from the issue:

```python
from sympy import *
a, b = symbols('a,b')
r = (1/(a+b) + 1/(a-b))/(1/(a+b) - 1/(a-b))
r.subs(b, a)    # returns 1, expected an undefined result
r.limit(b, a)   # returns -1, which is correct and must stay that way
```

When `b` is replaced by `a`, the term `1/(a-b)` becomes `1/0`, which SymPy evaluates to `zoo`. That makes the numerator and the denominator undefined or infinite. The reporter's rule is: *if any subexpression is undefined, the whole expression is undefined.* Returning `1` hides the problem from the user.

**Likely mechanism (a hypothesis, not yet verified against the source):**

- After substitution, the numerator becomes `1/(2*a) + zoo`.
- The denominator becomes `1/(2*a) - zoo`, which canonicalises to the same form, because `-zoo == zoo`.
- `1/(2*a)` is not known to be finite (`a` could be 0), so the `Add` may keep both terms, for example as `zoo + 1/(2*a)`.
- The quotient then has the form `X * X**-1`.
- Automatic `Mul`/`Pow` flattening combines equal bases (`X**1 * X**-1 → X**0 → 1`) without checking that `X` is infinite or undefined.

The fix belongs in the evaluation layer, not in `subs` itself. That layer still needs to be confirmed.

**Users.** SymPy users who substitute values into rational expressions. They need a result that signals "undefined" instead of a misleading finite number.

**Acceptance criteria**

1. `r.subs(b, a)` for the expression above does not return `1` or any other finite number.
   - It should return `nan`; see Open Questions.
2. `r.limit(b, a)` still returns `-1`.
3. Ordinary cancellation of finite or symbolic bases is unchanged:
   - `x/x → 1`
   - `x**2/x → x`
   - `(a+b)/(a+b) → 1`
4. An expression that contains `zoo` or `nan` and is divided by itself does not simplify to `1`. For example, `(zoo + x)/(zoo + x)` must not give `1`.

## Tech Stack

- Python and SymPy.
- The issue was reported on SymPy 1.1.1 with Python 3.6.4.
- The target branch and version are unknown.
- Relevant core modules are presumably `sympy/core/mul.py`, `sympy/core/add.py`, `sympy/core/power.py` and `sympy/core/basic.py` (`subs`). This needs confirmation in the repository.

## Commands

The exact commands are unknown because there is no repository access. They will likely use pytest or SymPy's own test runner, for example `bin/test sympy/core`, but this is not confirmed.

| Purpose | Command |
|---|---|
| Build | Unknown (pure Python; likely none) |
| Test | Unknown |
| Lint / code quality | Unknown |
| Reproduce | The snippet in the Objective section |

## Project Structure

Unknown, beyond SymPy's conventional layout:

- Core source is assumed to be under `sympy/core/`.
- Tests are assumed to be in `sympy/core/tests/`, for example `test_subs.py` and `test_arit.py`.

Both need confirmation.

## Code Style

- Follow the existing SymPy conventions in the files being touched.
- The style is unknown in detail; no repository code is visible.

## Testing Strategy

**Regression test for the reported case.** Assert that `r.subs(b, a)` is not `1` and equals the agreed undefined value, probably `S.NaN`.

**Unit tests for the core evaluation rule:**

- An infinite or undefined base must not cancel against its reciprocal.
- Finite and symbolic cancellation must stay unchanged; see criterion 3.

**Guard test.** `r.limit(b, a) == -1`.

**Wider check.** Run the full core test suite, and ideally the whole suite. Changing `Mul`/`Add` canonicalisation affects most of SymPy, so performance and behaviour regressions are a real risk.

## Boundaries

**Always**
- Add regression tests for the reported expression.
- Run the core test suite before proposing changes.
- Keep the automatic simplification of finite and symbolic expressions unchanged.

**Ask first**
- Changing the semantics of `subs`, for example making it evaluate limits or check denominators.
- Changing how `zoo + finite-or-unknown` terms are combined in `Add`.
- Any change with a measurable performance cost to `Mul`/`Add` flattening.
- Changing existing tests that currently expect the old behaviour.

**Never**
- Make `subs` silently return the limit value (`-1`). Substitution is not taking a limit.
- Remove or weaken existing tests without approval.
- Special-case this one expression instead of fixing the general rule.

## Success Criteria

- The reproduction snippet returns an undefined value (`nan`, unless decided otherwise), not `1`.
- `r.limit(b, a)` still returns `-1`.
- Criteria 3 and 4 above are covered by tests, and those tests pass.
- The existing SymPy test suite passes with no new failures.

## Assumptions

1. The expected result for `r.subs(b, a)` is `nan`. Both numerator and denominator are infinite or undefined, and `zoo/zoo` is `nan`.
2. The root cause is equal-base cancellation in `Mul`/`Pow` (`X * X**-1 → 1`) applied to a base containing `zoo`. It is not caused by `subs` itself.
3. `subs` should keep its current semantics: substitute and auto-evaluate, with no limit-taking and no global "is any denominator zero" scan.
4. The fix targets the current development branch, not 1.1.1.
5. Returning `nan` in more edge cases that previously gave finite values is acceptable when those finite values were mathematically wrong.

## Open Questions

1. Should the result be `nan`, or is `zoo` (or an unevaluated expression) acceptable or preferred?
2. Should the fix also ensure that `1/(2*a) + zoo` collapses to `zoo` even though `a` might be zero? Or should it only stop the faulty cancellation?
3. Should `subs` offer an option, or should the docs point users to `limit` when a substitution hits a singularity?
4. What is the acceptable performance cost for adding finiteness checks in `Mul` flattening?
5. Are there existing tests or downstream code that rely on the current cancellation behaviour with `zoo`-containing terms?
6. What are the target branch, version, and exact test commands?