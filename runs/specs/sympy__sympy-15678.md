# Spec: `idiff` support for `Eq` equations and applied functions (`f(x)`) as the dependent variable

## Objective

`idiff(eq, y, x)` in `sympy/geometry/util.py` computes the implicit derivative `dy/dx` of an equation. It currently fails in two cases:

1. **`Eq` input.** When `eq` is an `Eq(lhs, rhs)` object instead of an expression assumed equal to zero, `idiff` raises `IndexError: list index out of range` at line 582 (`yp = solve(eq.diff(x), dydx)[0].subs(derivs)`).
2. **Applied function as dependent variable.** When `y` is an applied undefined function such as `f(x)` instead of a `Symbol`, `idiff` raises `ValueError: expecting x-dependent symbol(s) but got: f(x)` at line 574.

The expression form already works:

```
>>> idiff(y*exp(y) - x*exp(x), y, x)
(x + 1)*exp(x - y)/(y + 1)
```

**Users:** SymPy users who compute implicit derivatives and naturally write equations as `Eq(...)` or model the dependent variable as `f(x)`.

**Success:** Both failing calls return the mathematically correct derivative. Existing behaviour does not change.

### Acceptance criteria

- **AC1.** `idiff(Eq(y*exp(y), x*exp(x)), y, x)` returns a result equivalent to `idiff(y*exp(y) - x*exp(x), y, x)`, which is `(x + 1)*exp(x - y)/(y + 1)`.
- **AC2.** `idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)` returns a result equivalent to `(x + 1)*exp(x - f(x))/(f(x) + 1)`. This is the AC1 result with `y` replaced by `f(x)`.
- **AC3.** The combination `idiff(Eq(f(x)*exp(f(x)), x*exp(x)), f(x), x)` also works and gives the AC2 result. *(Assumed in scope. See Open Questions.)*
- **AC4.** All currently supported call forms keep returning their current results. This includes:
  - a single `Symbol` `y`;
  - a list of dependent symbols (e.g. `[y, a]`);
  - the higher-order argument `n`.
- **AC5.** Invalid `y` arguments (anything that is neither a `Symbol` nor an `x`-dependent applied function, or a list of these) still raise a `ValueError`.

## Tech Stack

- Python, SymPy (versions unknown).
- Relevant module: `sympy/geometry/util.py`, function `idiff`. This is the only path visible in the issue.
- Related SymPy constructs: `Eq`, `solve`, `Function` / applied undefined functions, `Derivative`.

## Commands

The repository is not visible, so the exact commands are unknown.

- Build: unknown (pure-Python package; likely none required).
- Test: unknown. Must be confirmed. This is presumably the project's standard test runner targeting the `idiff` tests.
- Lint: unknown.
- Reproduce: the Python REPL snippet from the issue (requires `x`, `y` symbols and `f` as an undefined `Function`).

## Project Structure

- `sympy/geometry/util.py` → contains `idiff`. Seen in the traceback.
- Test file location for `idiff`: unknown. It is presumably a `tests/` directory near `sympy/geometry/`. Must be confirmed.

## Code Style

Unknown beyond what the issue shows. Follow the existing style of `sympy/geometry/util.py`. The one visible snippet is:

```python
yp = solve(eq.diff(x), dydx)[0].subs(derivs)
raise ValueError("expecting x-dependent symbol(s) but got: %s" % y)
```

Error messages use `%`-formatting in that file. Keep consistency with the surrounding code.

## Testing Strategy

- **Unit tests** for `idiff` in the existing test module for `sympy/geometry/util.py` (location unknown):
  - one test each for AC1, AC2 and AC3;
  - compare results via symbolic equivalence (e.g. simplification of the difference to zero), not exact printed form, unless the existing tests use exact form.
- **Regression:** the existing `idiff` tests must pass unchanged (AC4).
- **Negative test:** an invalid `y` still raises `ValueError` (AC5).
- **Coverage expectations:** unknown. Follow the project norm.

## Boundaries

**Always:**
- Run the existing `idiff` tests and the new tests before committing.
- Keep the public signature `idiff(eq, y, x, n=1)` unchanged. *(Assumed signature. See Assumptions.)*
- Add regression tests reproducing both tracebacks from the issue.

**Ask first:**
- Changing the return form or simplification of existing results.
- Moving `idiff` out of `sympy/geometry/util.py`.
- Broadening support to other relational types (`Ne`, `Lt`, …).
- Supporting multivariate applied functions such as `f(x, z)`.

**Never:**
- Change the behaviour of currently working call forms.
- Silently accept invalid `y` arguments.
- Remove or weaken existing tests.

## Success Criteria

- The two failing REPL calls from the issue return correct derivatives instead of raising (AC1, AC2).
- The combined `Eq` + `f(x)` case works (AC3).
- `idiff(y*exp(y) - x*exp(x), y, x)` still returns `(x + 1)*exp(x - y)/(y + 1)`.
- All pre-existing `idiff` tests pass. New tests covering AC1–AC5 are added and pass.

## Assumptions

1. An `Eq(lhs, rhs)` argument should be treated as the expression `lhs - rhs` set equal to zero, matching the documented expression form.
2. When `y` is an applied function like `f(x)`, the result should be expressed in terms of `f(x)`, not a substituted dummy symbol.
3. Only applied functions whose arguments depend on `x` (e.g. `f(x)`) need to be supported. Single-argument `f(x)` is the required case.
4. The signature is `idiff(eq, y, x, n=1)` with optional higher-order `n` and list-valued `y`. This is inferred from SymPy conventions and the error message "symbol(s)", not seen in the issue.
5. Mixed lists such as `[f(x), a]` should be handled consistently with lists of symbols.
6. The issue author's expected outputs are the "equivalent of the expression form" results. The exact printed form may differ.

## Open Questions

1. Should the combined case (`Eq` with `f(x)` as `y`) be explicitly in scope? AC3 assumes yes.
2. For `f(x)` input, should the output be in terms of `f(x)`, or is a different representation acceptable?
3. Should multi-argument applied functions (e.g. `f(x, z)`) or derivative-valued `y` be supported or explicitly rejected?
4. Should other relationals (`Ne`, inequalities) be rejected with a clear error rather than mis-handled?
5. What is the exact test file and test command for `sympy/geometry/util.py`?
6. Are there supported SymPy/Python version constraints that affect the solution?