# Spec: Correct C signatures for unused array arguments in `autowrap` (cython backend)

## Objective

`autowrap` with `backend='cython'` generates a wrong C function signature when an array argument (e.g. a `MatrixSymbol`) passed through `args=` does not appear in the wrapped expression. The argument is declared as a scalar (`double x`) instead of a pointer (`double *x`). Calling the wrapped function with a NumPy array then fails with:

```
TypeError: only size-1 arrays can be converted to Python scalars
```

**Why it matters:** callers often need a fixed function signature to interface with external libraries such as numerical integrators. Some arguments in that signature may not contribute to the output.

**Users:** SymPy users who generate compiled numerical functions with `autowrap` and need control over the argument list.

**Expected behavior:** an argument's type and shape in the generated code depend on the argument itself (e.g. `MatrixSymbol('x', 2, 1)` is always an array). They do not depend on whether the argument appears in the expression.

**Reproduction (from the issue):**

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

x = MatrixSymbol('x', 2, 1)
expr = 1.0
f = autowrap(expr, args=(x,), backend='cython')

f(np.array([[1.0, 2.0]]))   # expected: 1.0; actual: TypeError
```

Currently generated C:

```c
double autofunc(double x) {
   double autofunc_result;
   autofunc_result = 1.0;
   return autofunc_result;
}
```

Expected: `x` is declared as `double *x`.

**Control case (works today):** with `expr = x[0,0]` the call returns `1.0` as expected.

**Suspected location:** the reporter believes the defect is in `codegen`. The exact module and function are unconfirmed. The likely cause is that array metadata (dimensions) is only inferred for symbols found in the expression.

## Assumptions

1. The root cause is in the code-generation layer (`codegen`) that builds routine arguments. It is not in the Cython wrapper template itself. This follows the reporter's diagnosis and has not been verified.
2. The fix should keep dimension and array information for any argument given explicitly in `args`, whether or not it appears in `expr`.
3. Other backends and languages that share `codegen` (e.g. f2py/Fortran) may have the same defect. A fix in shared `codegen` code may change their output too, and that change is desired.
4. The behavior for expressions that do use all their array arguments must stay unchanged.
5. A scalar `Symbol` that is unused but listed in `args` should stay a scalar argument. Only array-like arguments (`MatrixSymbol`, possibly `IndexedBase`) are affected.
6. The reporter intends to submit a PR. This spec describes what that PR, or any equivalent fix, must satisfy.

## Tech Stack

- Python, SymPy (version unknown; whichever version contains the defect)
- `sympy.utilities.autowrap` with the Cython backend
- NumPy (used at call time)
- Cython and a C compiler (needed to build the wrapper at runtime)
- Code-generation module referred to as `codegen` in the issue (exact path not confirmed)

## Commands

Unknown. They are not given in the issue and the repository is not available.

- Build: unknown (SymPy is pure Python; autowrap compiles at runtime)
- Test: unknown (the test runner and the exact test file paths for `codegen` and `autowrap` are not visible)
- Lint: unknown
- Dev: unknown

## Project Structure

Only what the issue implies:

- `sympy.utilities.autowrap`: public `autowrap` entry point and backends (module path from the import in the issue)
- `codegen`: code-generation layer where the reporter believes the bug lives (file path not confirmed)
- Test locations for `codegen` and `autowrap`: unknown

## Code Style

Unknown. Follow existing SymPy conventions in the touched module. No snippet of the relevant source is available.

## Testing Strategy

The framework and test file locations are unknown. The required coverage is:

- **Codegen-level test (no compiler needed):** generate C code for a routine with an array argument absent from the expression. Assert that the argument is declared as a pointer, e.g. `double *x`. This is the primary regression test because it runs without Cython or a C compiler.
- **Codegen-level control test:** confirm that an array argument used in the expression still produces the same signature as before.
- **Mixed case:** a routine with several arguments, some used and some unused, some scalar and some array. Assert that each argument has the correct declaration and that argument order matches `args`.
- **Autowrap integration test (cython backend):** run the reproduction from the issue and assert that it returns `1.0`. It should be skipped when Cython, NumPy, or a compiler is unavailable, following whatever skip mechanism existing autowrap tests use (unknown).
- **Other backends/languages (if affected):** if the fix is in shared `codegen` code, add equivalent signature assertions for other code generators that consume the same argument metadata (e.g. Fortran). Scope is subject to an Open Question.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep generated output unchanged for expressions that use all their arguments.
  - Respect the argument order given in `args`.
- **Ask first:**
  - Changing public signatures of `codegen` or `autowrap` APIs.
  - Changing generated output for languages or backends beyond C/Cython.
  - Changing how `IndexedBase` or other non-`MatrixSymbol` array types are handled, if that goes beyond the minimal fix.
- **Never:**
  - Work around the problem in the Cython wrapper only, for example by special-casing NumPy input, while leaving the wrong C signature in place.
  - Require users to reference unused arguments in `expr` as a workaround.
  - Remove or weaken existing tests.

## Success Criteria

1. With `x = MatrixSymbol('x', 2, 1)`, `autowrap(1.0, args=(x,), backend='cython')` returns a callable, and `f(np.array([[1.0, 2.0]]))` returns `1.0` without error.
2. The generated C function for that case declares `x` as `double *x`, not `double x`.
3. The generated C for `expr = x[0,0]` with `args=(x,)` is unchanged from current behavior.
4. With mixed used and unused scalar and array arguments, every argument appears in the generated signature in `args` order. Each array argument is a pointer and each scalar is a scalar.
5. New regression tests cover criteria 2–4 at the codegen level, plus an integration test for criterion 1. All existing codegen and autowrap tests still pass.

## Open Questions

1. Where exactly in `codegen` is argument metadata (dimensions) derived? Is the fix best made there, for example when an explicit argument list is given, or in each language-specific generator?
2. Do other backends and languages that share `codegen` (f2py/Fortran, Octave, Rust, Julia, etc.) show the same defect for unused array arguments? Should this fix cover them or be limited to C/Cython?
3. Should unused `IndexedBase` arguments, not just `MatrixSymbol`, be handled too? Is there a reproduction for that case?
4. Should an unused array argument that has no known shape be supported? If so, how should its dimensions be passed or declared?
5. Should the generated code avoid compiler warnings about unused parameters, or are such warnings acceptable?
6. Which SymPy version is affected, and which test files and commands should host the regression tests?
7. The reporter plans to open a PR. Should this work build on that PR or proceed independently?