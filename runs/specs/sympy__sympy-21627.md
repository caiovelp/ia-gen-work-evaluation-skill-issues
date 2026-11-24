# Spec: Fix `RecursionError` in `is_zero` for nested `cosh`/`acos`/`acosh` expression

## Objective

Querying `expr.is_zero` on the expression below raises `RecursionError: maximum recursion depth exceeded while calling a Python object`:

```python
expr = sympify("cosh(acos(-i + acosh(-g + i)))")
expr.is_zero
```

An assumption query must never crash. It should return `True`, `False`, or `None` (unknown).

**User:** Anyone using SymPy who queries assumptions such as `is_zero` on expressions that nest hyperbolic and inverse trigonometric or inverse hyperbolic functions. This includes internal SymPy code that runs these queries implicitly, for example during simplification, comparison or `Mul`/`Add` construction.

**Acceptance criteria:**
- `sympify("cosh(acos(-i + acosh(-g + i)))").is_zero` returns without raising.
- The returned value is mathematically correct. `None` is acceptable when the truth cannot be determined. The query must not return a definite `True`/`False` that is wrong.
- The root cause is fixed: the specific cycle of mutual assumption queries is identified and broken. Raising the recursion limit or catching `RecursionError` does not count as a fix.
- Existing assumption behavior of `cosh`, `acos` and `acosh` on previously working inputs does not change, unless a change is required to fix a demonstrably wrong result.

## Assumptions

1. The project is SymPy. `sympify` and `.is_zero` are SymPy APIs.
2. In the string, `i` and `g` are parsed as plain `Symbol`s with no assumptions. `i` is not the imaginary unit `I`, because `sympify("i")` gives `Symbol('i')`.
3. The recursion comes from the old-style assumptions system (`_eval_is_*` handlers and their inference rules). One handler, such as `cosh._eval_is_zero`, `_eval_is_real`, `_eval_is_positive`, or an `acos`/`acosh` handler, queries a property of its argument, and that query eventually re-enters the original query in a cycle.
4. The bug reproduces on the current development branch. The SymPy version and Python version were not given in the issue.
5. The fix belongs in the relevant function classes' assumption handlers. No change to the core assumptions engine is expected, though this is not confirmed.
6. Other assumption queries on the same expression may also recurse, for example `is_real`, `is_positive` and `is_finite`. They should be checked too.

## Tech Stack

- Python, SymPy. Versions unknown (not stated in the issue).
- Relevant components (inferred): the `cosh` class, the `acos` class, the `acosh` class, and the old-style assumptions machinery. Exact file locations are unknown.

## Commands

Unknown. The issue does not state them. Placeholders to confirm:
- Reproduce: `python -c "from sympy import sympify; print(sympify('cosh(acos(-i + acosh(-g + i)))').is_zero)"`. This is derived directly from the issue.
- Test: unknown (SymPy's test runner and the relevant test file paths are not visible).
- Lint/style check: unknown.

## Project Structure

Unknown. No paths are visible in the issue. Expected locations, to be confirmed:
- The source module(s) defining `cosh`, `acos` and `acosh`.
- The corresponding test module(s) for hyperbolic and trigonometric functions.

## Code Style

No code is visible in the issue. Follow the existing conventions in the modules being changed. Assumption handlers should:
- Return `True`, `False` or `None`, and never raise for undecidable cases.
- Avoid querying a property of the argument that can, through inference, re-query the property being computed on the same object.

## Testing Strategy

- **Regression test:** add a test asserting that `sympify("cosh(acos(-i + acosh(-g + i)))").is_zero` completes. If the correct value is determinable, assert it. Otherwise assert `is None`. Place it in the existing test module for hyperbolic functions (path unknown).
- **Related queries:** in the same test, check that other common assumption queries on this expression complete without error (`is_real`, `is_positive`, `is_finite`, `is_extended_real`, etc.).
- **Sub-expression coverage:** add assertions for the minimal sub-expression that triggers the cycle, once it is identified. For example, it may be `acos(x + acosh(y))` or `cosh(acos(z))` with generic symbols.
- **Regression safety:** run the full existing test suites for the hyperbolic, trigonometric and assumptions areas. All must pass.

## Boundaries

- **Always:** reproduce the error before changing code. Identify the exact recursion cycle and record which handlers are involved. Add a regression test that fails before the fix and passes after. Keep assumption results conservative (`None` rather than a guess).
- **Ask first:** changing the core assumptions engine or inference rules. Changing documented assumption results of existing functions. Broad refactors of the `cosh`, `acos` or `acosh` handlers beyond what breaks the cycle.
- **Never:** raise `sys.setrecursionlimit` or catch `RecursionError` as the fix. Return a definite `True`/`False` without mathematical justification. Remove or weaken existing tests to make the suite pass.

## Success Criteria

1. The reproduction snippet from the issue runs and prints `True`, `False` or `None` with no exception.
2. The returned value is mathematically correct, or `None`.
3. A new regression test covering the issue's expression exists and passes. It failed before the fix.
4. The existing hyperbolic, trigonometric and assumptions test suites pass unchanged.
5. The PR description names the recursion cycle (which `_eval_is_*` handlers call each other) and explains how the fix breaks it.

## Open Questions

1. Which SymPy and Python versions were used? Does the bug reproduce on the current development branch?
2. Was `i` intended as a generic symbol, or as the imaginary unit `I`? Should the fix also be verified with `I` substituted?
3. What is the expected value of `is_zero` here: `False`, or `None` (unknown)? Is `None` acceptable to the reporter?
4. Is the cycle confined to `cosh` handlers, or does it involve `acos`/`acosh` handlers, or general inference in the assumptions engine? This determines where the fix belongs.
5. Should the same audit apply to sibling functions with similar handlers, such as `sinh`, `cos` and `asin`, or should this fix stay narrowly scoped?
6. What are the exact test and lint commands, and which test file paths are relevant? None are visible in the issue.