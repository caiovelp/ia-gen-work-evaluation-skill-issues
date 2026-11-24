# Spec: `lambdify` support for `MatrixSymbol` arguments with non-identifier names

## Assumptions
1. The project is SymPy, and the affected public API is `sympy.lambdify` (called as `sy.lambdify` in the issue).
2. `lambdify` generates Python source text from its arguments and expression, then compiles it. The `SyntaxError` comes from a `MatrixSymbol` name such as `{v}` being written into the generated source as a raw identifier.
3. **Hypothesis to verify, not a fact.** The step that replaces invalid names with dummies handles scalar `Symbol` arguments, which is why `{x}` works. It may not handle `MatrixSymbol` arguments, which is why `{v}` fails both with and without `dummify=True`.
4. Expected behavior for `{v}` matches the behavior for `{x}`. When an argument name is not a valid Python identifier, `lambdify` substitutes a safe name. The resulting function behaves exactly as if the user had chosen a valid name.
5. `dummify=True` should always yield valid generated code, whatever the argument names are.
6. Behavior for currently working cases must not change. This covers valid-name `MatrixSymbol`s, curly-brace scalar `Symbol`s and ordinary symbols.
7. The fix targets the default printer/module path. Other `modules=` backends (numpy, etc.) should behave the same where they already support `MatrixSymbol`.
8. The SymPy version and Python version from the report are unknown. The bug is assumed to still reproduce on the current development branch.

## Objective
`lambdify` must produce a working callable when an argument or expression involves a `MatrixSymbol` whose name is not a valid Python identifier (for example `"{v}"`). This must work both with and without `dummify=True`.

**User:** a SymPy user who builds symbols with LaTeX-style names (e.g. `{v}`, which is common for pretty printing) and wants numeric functions from expressions over matrices.

**Acceptance (user stories):**
- As a user, `sy.lambdify(curlyv, curlyv)` returns a callable without raising `SyntaxError`, where `curlyv = sy.MatrixSymbol("{v}", 2, 1)`.
- As a user, `sy.lambdify(curlyv, curlyv, dummify=True)` returns a callable without raising `SyntaxError`.
- As a user, calling either callable with a 2×1 matrix/array returns that same value, just as `sy.lambdify(v, v)` does for `v = sy.MatrixSymbol("v", 2, 1)`.

## Tech Stack
- Python, SymPy (version under test: unknown; assumed current development branch).
- Exact supported Python versions and optional numeric backends (e.g. NumPy): **unknown**, so use the project's existing CI matrix.

## Commands
Not visible in the issue; all **unknown**. To be filled in from the repository:
- Test: unknown (project's standard test runner, run against the lambdify test module)
- Lint / code quality: unknown
- Build: unknown / likely not applicable (pure Python)

Reproduction snippet (from the issue):
```python
import sympy as sy
curlyx = sy.symbols("{x}")
v = sy.MatrixSymbol("v", 2, 1)
curlyv = sy.MatrixSymbol("{v}", 2, 1)

sy.lambdify(curlyx, curlyx)                      # works
sy.lambdify(v, v)                                # works
sy.lambdify(curlyv, curlyv)                      # SyntaxError
sy.lambdify(curlyv, curlyv, dummify=True)        # SyntaxError
```

## Project Structure
Not visible in the issue; **unknown**.
- Location of the `lambdify` implementation: unknown (to be located in the repository).
- Location of existing `lambdify` tests: unknown (new regression tests go alongside them).

## Code Style
- Follow the existing conventions of the `lambdify` module and its tests. No snippet can be given because the source is not visible.
- Regression tests should mirror the issue's reproduction (same symbol names and shapes) so they trace back to it.

## Testing Strategy
- **Framework:** the project's existing test framework (name unknown from the issue).
- **Location:** next to the existing `lambdify` tests (path unknown).
- **Required regression tests:**
  1. `lambdify(MatrixSymbol("{v}", 2, 1), same)` succeeds, and the callable returns its input for a 2×1 value.
  2. The same call with `dummify=True` succeeds and behaves identically.
  3. A `MatrixSymbol` with a non-identifier name used inside a larger expression (e.g. matrix product or sum) evaluates correctly. This covers the expression body as well as the argument list.
  4. Mixed arguments: a curly-brace scalar `Symbol` together with a curly-brace `MatrixSymbol` in one call.
  5. Arguments given in a nested structure (e.g. list/tuple containing the `MatrixSymbol`), if `lambdify` supports nested args for scalars.
- **Non-regression tests:** existing tests for valid-name `MatrixSymbol`, curly-brace `Symbol` and the `dummify` behavior must keep passing unchanged.
- **Coverage:** no numeric target is known. Every new branch in the name-sanitization logic must be exercised by at least one test.

## Boundaries
- **Always:**
  - Reproduce the failure with a test before changing behavior.
  - Keep the public `lambdify` signature and documented `dummify` semantics unchanged.
  - Run the full `lambdify` test suite before committing.
- **Ask first:**
  - Changing which arguments get dummified when `dummify=False`, for example dummifying valid-name `MatrixSymbol`s, which may alter generated source or `inspect` output.
  - Changing printer behavior that affects code generation outside `lambdify`.
  - Adding dependencies.
- **Never:**
  - Silently rename the user's symbols in the returned expression or alter the user's objects.
  - Disable or weaken existing tests to make new ones pass.
  - Rely on `eval`/`exec` workarounds that bypass code validation.

## Success Criteria
- [ ] `sy.lambdify(curlyv, curlyv)` returns a callable, with no `SyntaxError`.
- [ ] `sy.lambdify(curlyv, curlyv, dummify=True)` returns a callable, with no `SyntaxError`.
- [ ] Both callables return a value equal to their 2×1 input, matching `sy.lambdify(v, v)` on the same input.
- [ ] A non-identifier `MatrixSymbol` name works when it appears in the expression body as well as in the argument list.
- [ ] `sy.lambdify(curlyx, curlyx)` and `sy.lambdify(v, v)` behave exactly as before.
- [ ] New regression tests fail before the change and pass after it.
- [ ] The full existing `lambdify` test suite passes.

## Open Questions
1. Which SymPy and Python versions did the reporter use, and does the bug still reproduce on the current development branch?
2. Which `modules=` backends must be covered: the default only, or also `numpy`, `math`, `mpmath`, etc.? For `MatrixSymbol`, which backends are officially supported today?
3. When `dummify=False`, should a non-identifier `MatrixSymbol` name be auto-replaced (matching the current scalar `Symbol` behavior), or should it raise a clear, non-`SyntaxError` error?
4. Should other non-`Symbol` argument types with invalid names be handled in the same change? Examples: other matrix expressions, `Indexed`/`IndexedBase`, and applied functions with odd names. Or is this scoped strictly to `MatrixSymbol`?
5. Is it acceptable for the generated source (visible via `inspect.getsource`) to change for affected cases?
6. What are the repository's test command, lint command and the paths of the `lambdify` implementation and its tests? None of these are visible in the issue.