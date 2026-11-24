# Spec: Preserve `ZeroMatrix` blocks in `BlockMatrix` block multiplication

## Objective

Multiplying `BlockMatrix` objects that contain `ZeroMatrix` blocks should work for any number of factors. Today the result of one block multiplication can contain scalar `Zero` (`sympy.core.numbers.Zero`) blocks in place of `ZeroMatrix` blocks. The next block multiplication then fails with an `AttributeError`.

**Users:** SymPy users working with block matrix expressions through `block_collapse`, `BlockMatrix._blockmul`, or matrix products of `BlockMatrix` objects.

**Reproduction (from the issue):**

```python
from sympy import *
a = MatrixSymbol("a", 2, 2)
z = ZeroMatrix(2, 2)
b = BlockMatrix([[a, z], [z, z]])

block_collapse(b * b)        # works: Matrix([[a**2, 0], [0, 0]])
b._blockmul(b)               # works
block_collapse(b * b * b)    # AttributeError: 'Zero' object has no attribute 'cols'
b._blockmul(b)._blockmul(b)  # same AttributeError
type(b._blockmul(b).blocks[0, 1])  # <class 'sympy.core.numbers.Zero'>, expected ZeroMatrix
```

**Failure location (from the traceback):**
- `sympy/matrices/expressions/blockmatrix.py`
  - `colblocksizes` (line ~80) reads `self.blocks[0, i].cols`. A scalar `Zero` block has no `.cols`.
  - `_blockmul` (line ~91) compares `self.colblocksizes == other.rowblocksizes`.
  - `bc_matmul` (line ~361) calls `A._blockmul(B)`.
  - `block_collapse` (line ~297) drives the rules.

**Observed root-cause symptom:** The blocks of the `_blockmul` result are not all matrix expressions. Zero blocks are demoted from `ZeroMatrix` to scalar `Zero`. The exact mechanism is unconfirmed. It most likely occurs while forming the product of the block arrays and placing the products into the resulting block container, where a sum or product of zero matrices collapses to scalar `0`. The fix must be scoped after the mechanism is confirmed.

**Acceptance criteria:**
1. `b._blockmul(b)._blockmul(b)` returns a `BlockMatrix` without raising.
2. `block_collapse(b * b * b)` returns a result without raising, and it is mathematically equal to `[[a**3, 0], [0, 0]]`.
3. Every block of `b._blockmul(b)` is a matrix expression with correct shape. In particular, `b._blockmul(b).blocks[0, 1]` is a `ZeroMatrix(2, 2)` and not a scalar `Zero`.
4. `rowblocksizes`, `colblocksizes`, and `shape` of any `_blockmul` result are well defined and consistent with its operands.
5. Existing behaviour for products without zero blocks is unchanged.

## Assumptions

1. The bug reproduces on the current development branch, not only in SymPy 1.4 as reported. This needs verification.
2. The intended invariant is that every block in a `BlockMatrix` is a matrix-like object with `.rows`/`.cols`. Scalar `Zero` blocks are a bug, not a supported state.
3. The defect is in how `_blockmul` builds its result blocks (zero-matrix products and sums collapsing to scalar `0`). It is not primarily in `colblocksizes`. Making `colblocksizes` tolerate scalars would only mask the problem, so it is not the target fix.
4. Non-square blocks and mixed block sizes must also keep correctly shaped `ZeroMatrix(m, n)` results. For example, a zero block in the product of an `m×k` block and a `k×n` block should be `ZeroMatrix(m, n)`.
5. The fix should not change the public API of `BlockMatrix`, `block_collapse`, or `ZeroMatrix`.
6. A regression test belongs in the test module for `blockmatrix.py`. The exact path is not visible in the issue.

## Tech Stack

- Python (issue reporter: 3.7.4; supported versions for the target branch: **unknown**)
- SymPy (issue reporter: 1.4; target branch/version: **unknown**)
- Relevant module: `sympy/matrices/expressions/blockmatrix.py`. It interacts with `ZeroMatrix`, `MatrixSymbol`, and `sympy.strategies.core` (`exhaustive_rl`, `chain_rl`, `conditioned_rl`, `switch_rl`).

## Commands

- Build: **unknown** (not shown in issue)
- Test: **unknown** (project test runner and invocation not shown in issue)
- Lint: **unknown**
- Reproduce: run the Python snippet in the Objective section in an interpreter with the checked-out SymPy on the path.

## Project Structure

Known from the issue:
```
sympy/matrices/expressions/blockmatrix.py   → BlockMatrix, _blockmul, colblocksizes, bc_matmul, block_collapse
sympy/strategies/core.py                    → rule combinators used by block_collapse
```
Unknown:
- Location of `blockmatrix.py` tests
- Location of the `ZeroMatrix` definition and its multiplication/addition logic

## Code Style

**Unknown.** No project code is visible beyond the traceback. Follow existing conventions in `blockmatrix.py`. A regression test should mirror the reproduction above, for example by asserting that the block types and the collapsed result match the expected values. The exact test style and helpers are unknown.

## Testing Strategy

- **Framework:** unknown. The existing SymPy test-suite conventions apply.
- **Regression tests (unit level), in the existing `blockmatrix` test module:**
  - `b._blockmul(b)` produces `ZeroMatrix` blocks with correct shapes, not scalar `Zero`.
  - `b._blockmul(b)._blockmul(b)` does not raise and equals the expected block result.
  - `block_collapse(b * b * b)` does not raise and equals the expected result.
  - Add a non-square / mixed-block-size variant to confirm the zero blocks have the correct `(rows, cols)`.
- **Regression safety:** the full existing `blockmatrix` and matrix-expressions test modules must still pass.
- **Coverage expectation:** unknown. At minimum, each acceptance criterion maps to at least one assertion.

## Boundaries

- **Always:**
  - Reproduce the failure with a test before changing code.
  - Keep blocks of `BlockMatrix` results as matrix expressions with correct shapes.
  - Run the existing block-matrix and matrix-expression tests before declaring done.
- **Ask first:**
  - Changing `ZeroMatrix` arithmetic semantics globally (e.g. how `ZeroMatrix + ZeroMatrix` or `MatMul` with zeros simplifies). This could affect many callers outside `BlockMatrix`.
  - Changing the type of container used for `BlockMatrix.blocks`.
  - Altering `block_collapse` rule ordering in `sympy/strategies`.
  - Any public API change.
- **Never:**
  - Paper over the bug only by making `colblocksizes`/`rowblocksizes` accept scalar `Zero` without fixing the block types.
  - Remove or weaken existing tests.
  - Silently convert scalar `0` into a `ZeroMatrix` of guessed shape where the shape cannot be determined from the operands.

## Success Criteria

- [ ] `block_collapse(b * b * b)` returns without exception and equals `[[a**3, 0], [0, 0]]` (as a block or explicit matrix, consistent with current `b * b` output style).
- [ ] `b._blockmul(b)._blockmul(b)` returns without exception.
- [ ] `isinstance(b._blockmul(b).blocks[i, j], ZeroMatrix)` for every zero block, and each has the correct shape.
- [ ] A non-square block example yields zero blocks of shape `(rows of left block row, cols of right block column)`.
- [ ] New regression tests fail before the fix and pass after it.
- [ ] All pre-existing tests in the affected test modules pass.

## Open Questions

1. Which branch/version is the fix targeting? Does the bug still reproduce there, or has it already been fixed upstream?
2. What are the project's test command and test file location for `blockmatrix.py`?
3. Where exactly does `ZeroMatrix` collapse to scalar `Zero`? In `_blockmul` itself, when building the result block array, or in `ZeroMatrix`/`MatAdd`/`MatMul` simplification? This decides whether the fix is local to `blockmatrix.py` or touches core matrix-expression code.
4. Is it acceptable for the fix to rely on block-size information (`rowblocksizes`/`colblocksizes` of the operands) to rebuild correctly shaped `ZeroMatrix` blocks?
5. Should `colblocksizes`/`rowblocksizes` also become defensive, e.g. raise a clearer error for non-matrix blocks, or is that out of scope?
6. `block_collapse(b * b)` currently prints as an explicit `Matrix([[a**2, 0], [0, 0]])`. Is that the expected output form for the triple product too, or should the result stay a `BlockMatrix`?
7. Are other `BlockMatrix` operations (e.g. `_blockadd`, transpose, inverse) known to produce scalar `Zero` blocks, and should they be covered by this change or by a separate one?