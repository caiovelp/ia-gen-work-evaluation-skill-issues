# Spec: Fix explicit conversion of single-block `BlockDiagMatrix` to `Matrix`

## Objective

Converting a `BlockDiagMatrix` with exactly one block into an explicit matrix raises `TypeError: 'One' object is not subscriptable`. With two or more blocks the same conversion works. The reporter says this is a regression: it works in SymPy 1.4 and fails in 1.5.1.

**User:** Anyone who builds block-diagonal matrices programmatically, where the number of blocks may be 1, and later needs an explicit `Matrix`.

**Reproduction (from issue):**
```python
M = sympy.Matrix([[1, 2], [3, 4]])
D = sympy.BlockDiagMatrix(M)
B = sympy.Matrix(D)   # TypeError: 'One' object is not subscriptable
```

**Expected:** `sympy.Matrix(D)` returns `Matrix([[1, 2], [3, 4]])`, the same as `M`.

**Failure path (from the traceback):**
1. `dense.py` `__new__` / `_new`
2. `matrices.py` `_handle_creation_inputs`, which calls `as_explicit()`
3. `matexpr.py` `as_explicit` and `__getitem__`
4. `blockmatrix.py` `_entry`, at `self.blocks[row_block, col_block][i, j]`

At that point `self.blocks[0, 0]` is the scalar `1`, not the block `M`. This means the `blocks` matrix of a single-block `BlockDiagMatrix` holds the block's *elements* instead of a 1×1 grid containing the block.

**User stories / acceptance:**
- As a user, `Matrix(BlockDiagMatrix(M))` gives a matrix equal to `M`.
- As a user, element access on a single-block `BlockDiagMatrix` (`D[i, j]`) returns the same values as `M[i, j]`.
- As a user, the multi-block behaviour stays unchanged. For example, `Matrix(BlockDiagMatrix(M, M))` still gives the 4×4 result shown in the issue.

## Tech Stack

- Python and SymPy. The issue's traceback runs on Python 3.7.
- Affected version: SymPy 1.5.1. Last known-good version: 1.4.
- Supported Python versions for the fix: **unknown**.

## Commands

- Build: **unknown** (SymPy is pure Python, but the repo's install or dev command is not visible).
- Test: **unknown**. The repo's test runner and invocation are not visible in the issue.
- Lint: **unknown**.
- Reproduce: run the Python snippet above in an environment with the fixed SymPy.

## Project Structure

Only the files named in the traceback are known:
```
sympy/matrices/expressions/blockmatrix.py  → BlockMatrix / BlockDiagMatrix (_entry, blocks); likely site of the bug
sympy/matrices/expressions/matexpr.py      → MatrixExpr.as_explicit, __getitem__
sympy/matrices/matrices.py                 → _handle_creation_inputs
sympy/matrices/dense.py                    → Matrix.__new__ / _new
```
Test file locations for `blockmatrix` are **unknown**. The assumption is a `tests/` directory next to the module, following SymPy convention, but this has not been verified.

## Code Style

The conventions are not visible from the issue. Follow the existing style of `blockmatrix.py`. Keep the fix minimal and local to the block-diagonal construction or access logic. Do not add special cases in the generic `Matrix` constructor.

## Testing Strategy

- Add regression tests in the existing test module for block matrices. The exact path is unknown.
- Test cases:
  1. `Matrix(BlockDiagMatrix(M)) == M` for an explicit 2×2 `M`.
  2. `BlockDiagMatrix(M).as_explicit() == M`.
  3. Entry access: `BlockDiagMatrix(M)[i, j] == M[i, j]` for all `i, j`.
  4. Shape: `BlockDiagMatrix(M).shape == M.shape`, and `blockshape == (1, 1)`.
  5. A single non-square block (e.g. 2×3), so the fix is not specific to square blocks.
  6. A single 1×1 block, as an edge case.
  7. Non-regression: `Matrix(BlockDiagMatrix(M, M))` equals the 4×4 result in the issue.
  8. Consider whether a single-block `BlockMatrix([[M]])` shows the same defect. See Open Questions.
- The existing block-matrix test suite must keep passing.

## Boundaries

- **Always:**
  - Add the regression test that reproduces the issue.
  - Run the existing matrix and block-matrix tests.
  - Keep the public API unchanged.
- **Ask first:**
  - Changing how `ImmutableMatrix` or `Matrix` constructors interpret nested matrix inputs. This is a broader behavioural change with wide blast radius.
  - Changing the return type of `BlockDiagMatrix.blocks`.
- **Never:**
  - Fix the bug by special-casing `BlockDiagMatrix` inside `Matrix._handle_creation_inputs`.
  - Remove or weaken existing tests.
  - Change multi-block output.

## Success Criteria

- [ ] The issue's reproduction snippet runs without error, and `B == Matrix([[1, 2], [3, 4]])`.
- [ ] For a single block, `BlockDiagMatrix(M).blocks` is a 1×1 grid whose `[0, 0]` entry is `M`, not a scalar.
- [ ] All new regression tests (cases 1–7) pass.
- [ ] The existing block-matrix and matrix test suites pass with no changes to existing assertions.
- [ ] The two-block example from the issue produces exactly the 4×4 matrix shown.

## Assumptions

1. **Root-cause hypothesis.** When `BlockDiagMatrix.blocks` has a single block, it builds an immutable matrix from `[[M]]`. The matrix constructor flattens the nested matrix into `M`'s own elements, so `blocks[0, 0]` becomes the scalar `1` (`One`). With several blocks, the mixed `M` and `ZeroMatrix` entries are kept as blocks, so no flattening occurs. This is inferred from the traceback and the 1.4 → 1.5.1 regression, and has not been verified against source.
2. The fix belongs in `blockmatrix.py`, in the construction of `blocks` or the `_entry` path, rather than in generic matrix construction.
3. The expected result of the conversion is exactly `M`, with the same values and shape.
4. The fix targets the current development branch, not a 1.5.x backport. This needs confirmation.

## Open Questions

1. Does `BlockMatrix([[M]])`, a single-block general block matrix, have the same bug? If so, is it in scope for this fix?
2. Which change between 1.4 and 1.5.1 introduced the regression? Should the fix restore the 1.4 mechanism, or address it differently?
3. Should a single-block `BlockDiagMatrix` simplify to its block, so that `BlockDiagMatrix(M)` evaluates to `M`? Or must it remain a `BlockDiagMatrix` instance? This spec assumes it remains one.
4. Are other operations on single-block `BlockDiagMatrix` affected and in scope? Candidates include `_blockmul`, `_blockadd`, inverse, transpose, and `block_collapse`.
5. Is a backport to the 1.5.x / 1.6 maintenance line required?
6. What are the repo's test command and the location of the block-matrix test file? Both are unknown.