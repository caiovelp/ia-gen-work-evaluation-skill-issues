# Spec: Stop `Expr.__eq__` from eval-ing reprs of unknown objects

## Assumptions

1. The affected code paths are the ones in the issue's traceback: `sympy/core/expr.py` (`__eq__`, line ~124), which calls `sympify(other)` in `sympy/core/sympify.py` (line ~385). That call falls back to `parse_expr` in `sympy/parsing/sympy_parser.py`, which runs `eval_expr` and then `eval(...)` (lines ~906–1011). Line numbers come from the issue and may have drifted.
2. The root cause is that `sympify` turns objects it doesn't recognize into a string (their `repr`/`str`) and parses that string as SymPy code. Equality comparison must not take this path.
3. **The scope is equality comparison (`==` / `!=`) only.** Changing the general-purpose `sympify()` string fallback for other callers (for example, `sympify("x + 1")`) is out of scope unless a maintainer decides otherwise. See the Open Questions.
4. Objects that SymPy legitimately knows how to convert must still compare correctly. This includes:
   - Python numeric types
   - objects with `_sympy_` hooks
   - types registered in the sympify converter table
5. Plain Python `str` operands in `==` should also not be parsed. For example, `Symbol('x') == 'x'` should be `False`. This must be confirmed (Open Question).
6. The issue appears to use pytest (the traceback has `FAILED [100%]`), but how the project's tests are invoked is not visible in the issue.

## Objective

Comparing a SymPy expression with an arbitrary object must never execute code derived from that object's string representation. Today `Symbol('x') == C()` can:

- **Raise unexpected exceptions.** For example, `AttributeError` when `repr` is `'x.y'`.
- **Run arbitrary code.** `eval` runs on an attacker- or user-controlled string, which is a security issue.
- **Return wrong results.** An object whose `repr` is `'x'` compares equal to `Symbol('x')`.

**Users affected:** any code that compares SymPy objects with non-SymPy objects. This includes containers holding mixed types, dict/set lookups, test assertions, and libraries that interoperate with SymPy.

**User stories:**
- As a library user, I can write `sym == obj` for any `obj` without side effects or exceptions coming from `obj.__repr__`.
- As a security-conscious user, I know that equality checks never pass untrusted strings to `eval`.
- As a user, an unrelated object is never reported as equal to a SymPy expression just because their string forms match.

## Tech Stack

- Python, SymPy (versions not given in the issue: **unknown**).
- Relevant modules (from the traceback): `sympy.core.expr`, `sympy.core.sympify`, `sympy.parsing.sympy_parser`.

## Commands

- Build: **unknown** (not specified in the issue)
- Test: **unknown**. The issue output suggests pytest, but the exact command and flags are not given.
- Lint: **unknown**
- Dev: **unknown**

## Project Structure

Known from the issue:
```
sympy/core/expr.py               → Expr.__eq__ (calls sympify on `other`)
sympy/core/sympify.py            → sympify(); string fallback into parse_expr
sympy/parsing/sympy_parser.py    → parse_expr / eval_expr (calls eval)
```
Test file locations: **unknown**. The existing test layout for `sympy/core` is not visible in the issue.

## Code Style

**Unknown.** No project code style is visible beyond the traceback. Follow existing conventions in the touched modules.

The reproduction cases below define the expected behavior and should become regression tests:

```python
import sympy

class C:
    def __repr__(self):
        return 'x.y'
_ = sympy.Symbol('x') == C()        # must not raise; result is False

class C:
    def __repr__(self):
        return 'x'
assert sympy.Symbol('x') != C()     # must pass
```

## Testing Strategy

- **Framework:** **unknown**. The issue output suggests pytest.
- **Regression tests to add:**
  - Comparing with an object whose `repr` is `'x.y'` does not raise and returns `False`.
  - Comparing with an object whose `repr` is `'x'` returns `False`, and `!=` returns `True`.
  - An object whose `repr` would have side effects (for example, a `repr` string that triggers a function call when evaluated) produces no side effect when compared. Assert this with a sentinel.
  - Both operand orders, `Symbol('x') == C()` and `C() == Symbol('x')`, behave consistently.
  - Non-`Symbol` expressions (for example, `x + 1`, `Integer(1)`) are covered, since the bug sits in `Expr.__eq__`.
- **Non-regression tests (must still pass):**
  - `Integer(1) == 1`, `Float(0.5) == 0.5`, and `Rational(1, 2) == Rational(1, 2)` stay `True`.
  - Objects defining `_sympy_` still compare via their SymPy conversion.
  - The existing `sympify("...")` string-parsing behavior is unchanged for direct callers (per Assumption 3).
- **Coverage expectations:** **unknown**. At minimum, all cases above are covered.

## Boundaries

- **Always:**
  - Add the repro cases from the issue as regression tests.
  - Keep `==` side-effect free and non-raising for arbitrary objects.
  - Run the existing core test suite before committing.
- **Ask first:**
  - Changing the public behavior of `sympify()` for general callers.
  - Changing behavior for `str` operands in `==`.
  - Changing `__eq__` semantics on classes other than `Expr` (for example, `Basic`).
  - Choosing between returning `False` and returning `NotImplemented` for unconvertible operands.
- **Never:**
  - Pass the `repr`/`str` of an arbitrary object to `eval` or `parse_expr` from an equality check.
  - Silence the problem by catching exceptions around `eval` while still evaluating.
  - Remove or weaken existing tests without approval.

## Success Criteria

1. `sympy.Symbol('x') == C()` with `repr` `'x.y'` returns `False` and raises nothing.
2. `sympy.Symbol('x') != C()` with `repr` `'x'` evaluates to `True`.
3. No code path reachable from `Expr.__eq__` (or `__ne__`) calls `eval`/`parse_expr` on a string derived from a non-string, non-SymPy object. This is verifiable by a sentinel-side-effect test.
4. Comparisons against Python numbers, SymPy objects, and objects implementing `_sympy_` give the same results as before the change.
5. The existing test suite passes.

## Open Questions

1. **Should `Expr == str` stay parsed?** For example, should `Symbol('x') == 'x'` keep its current behavior or become `False`? Changing it is a visible behavior change.
2. **Should the fix stop at `__eq__`?** Is the fix limited to `__eq__`/`__ne__`, or should other operators and comparisons that call `sympify` on operands also stop parsing reprs? Candidates include `__lt__`, `__add__`, and `__mul__`.
3. **Should general `sympify()` also change?** Should it deprecate or remove its fallback of stringifying unknown objects and parsing them, given the same security concern? If so, is that a separate issue?
4. **What should `__eq__` return for unconvertible operands?** Options are `False` or `NotImplemented`, the latter letting Python try the reflected `other.__eq__`.
5. **Does `Basic.__eq__` need the same fix?** It may have a similar `sympify` call, alongside `Expr.__eq__`.
6. **What compatibility policy applies?** Is a deprecation period needed for any user-visible change, or is it acceptable to change it immediately given the security nature ("fix ASAP")?
7. **What are the project's commands and test locations?** The build, test, and lint commands and the test file locations are needed for the Commands and Testing sections.