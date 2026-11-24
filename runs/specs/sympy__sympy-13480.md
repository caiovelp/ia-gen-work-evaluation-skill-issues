# Spec: Fix `NameError` in `coth.eval` when substituting integers into `coth(log(tan(x)))`

## Objective

`coth(log(tan(x))).subs(x, n)` raises an exception for some integer values of `n`. It should return a valid SymPy expression instead.

**Reported reproduction:**

```python
>>> from sympy import *
>>> x = Symbol('x')
>>> e = coth(log(tan(x)))
>>> print(e.subs(x, 2))
...
File ".../sympy/functions/elementary/hyperbolic.py", line 590, in eval
    if cotm is S.ComplexInfinity:
NameError: name 'cotm' is not defined
```

**Reported failing values:** 2, 3, 5, 6, 8, 9, 11, 12, 13, 15, 18, and others.

**User:** any SymPy user who evaluates or substitutes into expressions that contain `coth`. Today, a branch inside `coth.eval` crashes with a `NameError` when it should simplify or leave the expression unevaluated.

**Success means:**
- `coth.eval` never raises `NameError` (or any other unintended exception) on this code path.
- The returned value is mathematically correct.

## Assumptions

1. The traceback points to a bug inside `coth.eval` in `sympy/functions/elementary/hyperbolic.py`. The name `cotm` is referenced but never bound on that branch. It is most likely a misnamed local variable, but this is not verified because the source was not visible.
2. The branch is reached when the argument of `coth` takes a particular form. For `n = 2`, `tan(2) < 0`, so `log(tan(2))` can carry an imaginary `I*pi` component, which suggests an `Add` argument with a multiple of `I*pi` peeled off. This is an inference only. Some listed values (for example 13) do not obviously have `tan(n) < 0`, so the exact trigger condition is unconfirmed.
3. The correct behaviour relies on `coth` being periodic with period `I*pi`. So `coth(a + k*I*pi) == coth(a)` for integer `k`, and the result must agree numerically with the original expression.
4. The fix is limited to `coth.eval`. Sibling functions (`tanh`, `sinh`, `cosh`, `csch`, `sech`, etc.) are not in scope unless they show the same defect (see Open Questions).
5. The return value may be an unevaluated or partially simplified expression. The issue only requires correctness and no exception, not a particular canonical form.

## Tech Stack

- Python, SymPy (version or commit unknown; the reporter used a `sympy-master` checkout).
- Affected module: `sympy/functions/elementary/hyperbolic.py`. This path comes from the traceback. Line numbers may differ on current master.

## Commands

Unknown. They are not given in the issue. The SymPy test runner is presumably used, but the exact invocation is not confirmed.

```
Build: UNKNOWN (pure Python, likely none)
Test:  UNKNOWN (e.g. a test runner targeting the hyperbolic functions test module, to be confirmed)
Lint:  UNKNOWN
```

## Project Structure

Only the following is known from the issue:

```
sympy/functions/elementary/hyperbolic.py   → contains coth.eval (site of the error)
```

The location of the corresponding tests is unknown. It is presumably a `tests/` directory alongside `elementary/`, to be confirmed.

## Code Style

Unknown beyond the following:
- Follow the existing conventions in `hyperbolic.py`.
- Keep the change minimal and local to the faulty branch.
- Do not restructure `eval`.

## Testing Strategy

- **Regression unit tests** for `coth` covering the reported case: `coth(log(tan(x))).subs(x, n)` for `n` in {2, 3, 5, 6, 8, 9, 11, 12, 13, 15, 18}. Each case must not raise.
- **Numerical correctness:** for each such `n`, the substituted result evaluated with `.evalf()` must match the original expression evaluated numerically, for example via `e.evalf(subs={x: n})` or mpmath, within a tolerance.
- **Direct eval-path test:** call `coth` with an argument of the form `a + k*I*pi`, where `a` is non-trivial and `k` is an integer. This exercises the faulty branch without depending on `tan`/`log` simplification.
- **Non-regression:** existing `coth` and hyperbolic-function tests continue to pass.
- **Coverage:** the previously crashing branch in `coth.eval` is executed by at least one test.

## Boundaries

- **Always:**
  - Add regression tests for the reported inputs.
  - Verify results numerically, not only that no exception is raised.
  - Run the existing hyperbolic test suite.
- **Ask first:**
  - Changing the canonical output form of `coth` for previously working inputs.
  - Applying analogous changes to other hyperbolic or trigonometric functions.
  - Refactoring `eval` beyond the faulty branch.
- **Never:**
  - Suppress the error with a broad `try/except`.
  - Delete or weaken existing tests.
  - Change public API signatures.

## Success Criteria

- [ ] `coth(log(tan(x))).subs(x, n)` returns without exception for every `n` in {2, 3, 5, 6, 8, 9, 11, 12, 13, 15, 18}.
- [ ] It also returns without exception for all integers `n` in some tested range, for example 1–100.
- [ ] For each of those `n`, `abs(N(result) - N(coth(log(tan(n))))) < 1e-10`, where the reference is computed numerically, independently of the symbolic branch.
- [ ] `coth(a + k*I*pi)` for symbolic or numeric `a` and integer `k` returns a value equal to `coth(a)`, either symbolically or numerically.
- [ ] No `NameError` can occur in `coth.eval`. The undefined name is either bound or replaced by the correct variable.
- [ ] All pre-existing hyperbolic-function tests pass.

## Open Questions

1. **Trigger condition:** What exactly triggers the faulty branch? Some listed values (for example 13) do not have `tan(n) < 0`, so the "negative tan → `I*pi` term" explanation may be incomplete. The trigger should be confirmed by inspecting `coth.eval`.
2. **Sibling functions:** Do other functions in `hyperbolic.py` (or `trigonometric.py`) contain the same misnamed-variable pattern? Should they be fixed in the same change?
3. **Result form:** Is there a preferred canonical form for the result? For example, should `coth(log(tan(2)))` become `coth(log(-tan(2)))` or remain unevaluated?
4. **Target revision:** Which SymPy version or commit is targeted? Line 590 may not match current master.
5. **Test command:** What is the exact test command and test file location for hyperbolic functions?