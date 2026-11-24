# Spec: `cse()` must not extract bare `MatrixSymbol`s as common subexpressions when only their elements are used

## Objective

When an expression contains several element references to the same `MatrixSymbol` (e.g. `a[0, 0]`, `a[0, 1]`, …, which are `MatrixElement` objects), `sympy.cse()` currently treats the parent `MatrixSymbol` (`a`) as a repeated subexpression. It then emits a replacement such as `(x0, a)` and rewrites every element reference as `x0[i, j]`.

This is not a real common-subexpression saving:

- `x0` is only an alias (a copy) of the input matrix `a`.
- Downstream code generation (e.g. `ccode`) turns `x0 = a` into a 16-element element-wise copy (`x0[0] = a[0]; …`) and declares an extra array temporary.
- The generated code is longer and slower than the original, and the temporary `x0` has no declared shape at codegen time.

**Users:** people who substitute `MatrixSymbol` elements into scalar expressions so that codegen gets array inputs, then run `cse()` before `ccode`/codegen.

**Desired behaviour:** a `MatrixSymbol` that appears only as the parent of `MatrixElement` indexing must not be emitted as a CSE replacement on its own. Element references must stay rooted at the original symbol, for example `(x1, a[0, 0])` or `a[0, 0]` used directly. They must not be rooted at an alias, as in `x0[0, 0]`.

### Acceptance criteria (user-level)

1. For the issue's example (`e2 = (A*B)` built from `MatrixSymbol("a",4,4)` and `MatrixSymbol("b",4,4)` elements), `cse(e2)` returns no replacement whose right-hand side is a bare `MatrixSymbol` (`a` or `b`).
2. In the replacements and the reduced expressions, every `MatrixElement` has the original `MatrixSymbol` (`a` or `b`) as its parent, not a CSE symbol.
3. Substituting the replacements back into the reduced expressions reproduces the original expression (`cse` round-trip correctness is preserved).
4. Running `ccode` over the replacements, as in the issue, produces no whole-matrix copy statements (`x0[k] = a[k]`).

## Assumptions

1. The bug lies in `sympy.simplify.cse_main` (the function that finds repeated subexpressions treats the `MatrixSymbol` argument of each `MatrixElement` as a countable repeated subexpression). This is unverified because the repository is not available.
2. Plain `Symbol`s are already excluded from being CSE'd. A `MatrixSymbol` used purely as a parent of indexing should be treated in the same way, as an atom.
3. Matrix-level expressions that really repeat (e.g. `(A*B)` occurring twice in a matrix expression) remain valid CSE candidates. Only the bare `MatrixSymbol` leaf is excluded.
4. Whether individual elements (`a[0,0]`) should still get their own `xN` aliases when repeated is acceptable either way. The issue does not object to `x1 = a[0,0]`, only to `x0 = a`.
5. The issue's reproduction is Python 2 (`print` statements, an old `ccode` return signature with `human=False`). The fix targets the current supported SymPy/Python version, and tests should use current APIs.
6. No public API signature of `cse()` changes.

## Tech Stack

- Python, SymPy. The exact supported versions are unknown, and the repository is not visible.
- Components involved: `sympy.cse`, `MatrixSymbol`, `MatrixElement`, `sympy.printing.ccode`.

## Commands

- Build: unknown (none expected for pure Python).
- Test: unknown. The project's test runner command and the path of the relevant test file are not visible in the issue.
- Lint: unknown.
- Reproduce: run the snippet from the issue (ported to Python 3 / the current `ccode` API).

## Project Structure

Unknown; the repository is not visible. The likely locations are assumptions only:

- the CSE implementation module (assumed `sympy/simplify/cse_main.py`)
- its test module (assumed a `tests/` directory next to it)

Both need confirmation.

## Code Style

Unknown. Follow existing conventions in the CSE module and its tests. No snippet is available from the issue.

## Testing Strategy

- **Regression test (unit):** build the issue's 4×4 example (or a smaller 2×2 one) with `MatrixSymbol` elements, call `cse()`, and assert:
  - no replacement right-hand side is a `MatrixSymbol`;
  - all `MatrixElement`s in the output have the original `MatrixSymbol` as parent;
  - back-substitution equals the input.
- **Non-regression:** run the existing CSE test suite unchanged. Existing tests with matrix expressions, including any that intentionally CSE `MatrixExpr`s, must still pass.
- **Optional integration check:** `ccode` over the CSE output contains no element-wise copy of a whole input matrix.
- Coverage expectations: unknown and project-defined.

## Boundaries

- **Always:**
  - Keep `cse()` results mathematically equivalent to the input.
  - Add a regression test reproducing the issue.
  - Run the existing CSE tests.
- **Ask first:**
  - Changing the public signature or default options of `cse()`.
  - Changing how genuine repeated matrix expressions (non-leaf `MatrixExpr`) are CSE'd.
  - Changing `ccode`/codegen behaviour to work around the issue instead of fixing `cse`.
- **Never:**
  - Remove or weaken existing CSE tests to make the change pass.
  - Special-case the issue's specific names (`a`, `b`) or shapes.

## Success Criteria

- [ ] The issue's example yields no `(xN, a)` / `(xN, b)` replacements.
- [ ] No `MatrixElement` in the `cse()` output is indexed off a CSE-introduced symbol that merely aliases an input `MatrixSymbol`.
- [ ] Round-trip: `reduced` with the replacements substituted back equals `e2`.
- [ ] `ccode` of the CSE output for the example contains no whole-matrix copy loops.
- [ ] All pre-existing CSE tests pass.

## Open Questions

1. Should repeated individual elements (`a[0,0]` used several times) still be aliased to scalar temporaries (`x1 = a[0,0]`), or should `MatrixElement`s of `MatrixSymbol`s also be treated as atoms and never CSE'd?
2. If a bare `MatrixSymbol` appears both as an element parent and as a standalone operand in a matrix expression (e.g. `A*B + A[0,0]`), should it ever be CSE'd? The current proposal is never, since aliasing a leaf saves nothing.
3. Should the same rule apply to other indexable leaf objects (e.g. `IndexedBase`/`Indexed`)? Is there existing behaviour there to stay consistent with?
4. Which SymPy versions should the fix target or be backported to? The issue uses Python 2 and an older `ccode` API.
5. What are the exact test command and test file locations in the repository? They are unknown from the issue.