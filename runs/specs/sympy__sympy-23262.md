# Spec: Preserve single-element tuples in `lambdify` generated Python code

## Objective

In SymPy 1.10, `lambdify` drops the trailing comma when the expression is a one-element Python tuple. The generated function returns a scalar where it should return a tuple.

**Reproduction (from the issue):**

```python
import inspect
from sympy import lambdify

inspect.getsource(lambdify([], tuple([1])))
```

| Version | Generated source | Return type |
|---|---|---|
| SymPy ≤ 1.9 | `'def _lambdifygenerated():\n    return (1,)\n'` | `tuple` ✅ |
| SymPy 1.10 | `'def _lambdifygenerated():\n    return (1)\n'` | `int` ❌ |

Tuples with two or more elements generate correctly, for example `return (1, 2)`.

**Who is affected:** users whose code depends on `lambdify` returning a tuple when the input expression is a tuple. The reporter's program assumes the return type is always a tuple.

**What success looks like:** for any tuple input, including length 1, the generated code returns a Python `tuple` of the same length. The behaviour matches SymPy 1.9 for the cases shown.

**Classification:** this appears to be a regression between 1.9 and 1.10. The reporter is unsure, but the before/after outputs show behaviour that previously worked has changed.

## Assumptions

1. The bug is in how `lambdify` turns a Python `tuple` expression into source text, not in the runtime evaluation. The emitted source text itself is wrong (`(1)` instead of `(1,)`).
2. The same defect can appear wherever a one-element tuple is serialized:
   - nested inside other containers, e.g. `[(1,)]` or `((1,), 2)`
   - containing symbolic elements, e.g. `lambdify([x], (x,))`
   - under printer modules other than the default (e.g. `math`, `numpy`, `mpmath`)

   This has not been verified.
3. The empty tuple `()` must still produce valid code that returns `()`.
4. SymPy `Tuple` objects (as opposed to Python built-in `tuple`) might take a different printing path. Whether they are affected is unknown.
5. The fix should not change generated code for tuples of length ≥ 2, nor for lists or other containers, beyond what correctness requires.
6. The exact source location of the regression is not visible from the issue. It is unknown which file or function changed between 1.9 and 1.10.

## Tech Stack

- Python (supported versions for the target SymPy release: **unknown**)
- SymPy, affected version 1.10; last known good version 1.9
- Component: `sympy.lambdify` and the Python code printer it uses (exact module path: **unknown**)

## Commands

All of the following are unknown, because the repository is not visible:

```
Build: unknown (pure-Python package; build command not given)
Test:  unknown (test runner and invocation not given in the issue)
Lint:  unknown
Dev:   unknown
```

The only command shown in the issue is the reproduction snippet above, run in a Python interpreter.

## Project Structure

Unknown. The issue gives no file paths. The locations of the following still need to be confirmed:

- the `lambdify` implementation
- the code-printer module(s) used by `lambdify`
- the corresponding test files

## Code Style

Unknown. No project code appears in the issue. Follow the existing conventions of the surrounding SymPy code once located.

## Testing Strategy

- **Framework:** unknown. Use the project's existing test framework.
- **Regression tests (required).** Each case asserts both the generated source and the runtime return value:
  - `lambdify([], tuple([1]))()` returns `(1,)` and `type(...) is tuple`
  - `inspect.getsource(lambdify([], tuple([1])))` contains `(1,)`
  - `lambdify([], tuple([1, 2]))()` returns `(1, 2)` (unchanged behaviour)
- **Edge-case tests (recommended).** Exact expected outputs are subject to Open Questions:
  - Empty tuple: `lambdify([], ())()` returns `()`
  - Symbolic single element: `lambdify([x], (x,))(3)` returns `(3,)`
  - Nested: `lambdify([], ((1,), 2))()` returns `((1,), 2)`
  - Inside a list: `lambdify([], [(1,)])()` returns `[(1,)]`
  - The same checks under each supported printer module
- **Test location:** unknown. Place tests next to the existing `lambdify` tests.
- **Coverage expectation:** every container-serialization branch touched by the fix is exercised by at least one test.

## Boundaries

- **Always:**
  - Add a regression test that fails on current 1.10 behaviour before the fix.
  - Run the existing `lambdify` and printer test suites.
  - Keep output for tuples of length ≥ 2 unchanged.
- **Ask first:**
  - Changing the public `lambdify` signature or adding new options.
  - Altering generated code for non-tuple containers.
  - Changing how SymPy `Tuple` (as opposed to built-in `tuple`) is printed.
  - Backporting to a 1.10.x release.
- **Never:**
  - Remove or weaken existing tests.
  - "Fix" this by post-processing the user's return value (e.g. wrapping in `tuple()` at call time) instead of emitting correct source.
  - Change the generated function name or the overall source layout without approval.

## Success Criteria

1. `inspect.getsource(lambdify([], tuple([1])))` produces source that returns `(1,)`, e.g. `'def _lambdifygenerated():\n    return (1,)\n'`.
2. `type(lambdify([], tuple([1]))()) is tuple` and the value equals `(1,)`.
3. `lambdify([], tuple([1, 2]))` still generates `return (1, 2)` and returns `(1, 2)`.
4. Single-element tuples nested inside tuples or lists also produce tuples at runtime.
5. The empty tuple still produces valid code returning `()`.
6. All pre-existing `lambdify` and printer tests pass.
7. New regression tests covering criteria 1–5 are added and pass.

## Open Questions

1. Which change between 1.9 and 1.10 introduced the regression? Identifying it would confirm the root cause and show whether other container types were affected too.
2. Is a SymPy `Tuple` with one element affected in the same way as a built-in `tuple`, and should the fix cover both?
3. Which printer modules (`math`, `numpy`, `mpmath`, `scipy`, `tensorflow`, etc.) must be verified? Does any of them intentionally print tuples differently?
4. Is a specific source formatting required, e.g. `(1,)` vs `(1, )`, or is any syntactically correct one-element tuple acceptable?
5. Should the fix be backported to a 1.10.x patch release?
6. The reporter asks for a workaround on the user side until a fix ships. Should the issue response suggest one, such as wrapping the result in `tuple(...)` or passing a list? This is outside the code fix and needs maintainer judgment.
7. The test command, test file locations, and supported Python versions are unknown and must be confirmed from the repository.