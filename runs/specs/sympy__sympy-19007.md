# Spec: Correct element access for BlockMatrix with symbolic indices or block sizes

## Objective

**Problem.** Indexing a `BlockMatrix` with a symbolic index returns an element of one specific block, even when the index could fall in more than one block. In the reported case:

```python
from sympy import *
n, i = symbols('n, i', integer=True)
A = MatrixSymbol('A', 1, 1)
B = MatrixSymbol('B', n, 1)
C = BlockMatrix([[A], [B]])
C[i, 0]   # currently returns (A)[i, 0]
```

`C[i, 0]` returns `(A)[i, 0]`. That is wrong. Row `i` falls in `A` only when `i == 0`, and in `B` when `1 <= i < 1 + n`. The library cannot know which block holds the element, so it must not resolve to one.

**Who this is for.** SymPy users who work with block matrix expressions, especially blocks with symbolic dimensions, and who index those matrices with symbolic or concrete indices.

**What success looks like.**

- Element access on a `BlockMatrix` resolves to a block's element only when the containing block can be proven.
- Otherwise, the result stays an unevaluated element of the whole block matrix, such as `C[i, 0]`.
- Every case that resolves correctly today keeps working.

### Acceptance criteria

Use the matrices from the issue: `A` is 1×1, `B` is n×1, and `C = [[A],[B]]`.

1. **Undetermined block.** `C[i, 0]`, with `i` a symbolic integer and no further assumptions, returns an unevaluated element of `C`. It must not return an element of `A` or `B`.
2. **Concrete index, first block.** `C[0, 0]` returns `A[0, 0]`.
3. **Concrete index, later block.** `C[1, 0]` returns `B[0, 0]`. The row index must be shifted by the sizes of the preceding blocks.
4. **Symbolic index provably in a later block.** If the index is provably in range for a later block, the result resolves to that block with the offset applied. Example: `C[n, 0]` with `n` positive → `B[n - 1, 0]`, if SymPy's assumptions can establish this.
5. **Columns behave the same way.** The same rules apply to column indexing in a block row. Example: `BlockMatrix([[A.T, B.T]])[0, i]` stays unevaluated.
6. **Fully numeric block matrices are unchanged.** Results for explicit `Matrix` blocks or fixed-size `MatrixSymbol` blocks with integer indices stay the same.
7. **Printing.** `pprint(C[i, 0])` shows an element of `C`, not `(A)[i, 0]`.

## Assumptions

1. The defect lies in how `BlockMatrix` maps a global `(i, j)` to a `(block, local i, local j)` pair. It most likely compares the index against cumulative block sizes and treats a "not provably True" comparison as False, or the other way round.
2. The right fallback when the block cannot be determined is the generic unevaluated matrix element (`MatrixElement` of the `BlockMatrix`). It is not a `Piecewise` over the blocks.
3. Index bounds checking, meaning errors for provably out-of-range indices, is outside this fix. Existing behavior there should be kept.
4. Only `BlockMatrix` is in scope. Whether `BlockDiagMatrix` shares the same code path is unknown. If it does, it gets the same fix.
5. Block-row heights and block-column widths can each be symbolic, independently of each other.
6. Indices that are integer-valued expressions, such as `i + 1`, should be handled through the same provability rule as plain symbols.

## Tech Stack

- Python, SymPy. The issue does not state the target versions, so they are **unknown**.
- Area: matrix expressions (`BlockMatrix`, `MatrixSymbol`, `MatrixElement`). The exact module path is **unknown**, because it is not visible in the issue.

## Commands

The exact commands are **unknown**, since they cannot be seen in the issue. They are to be confirmed from the repository:

- Test: unknown. It is presumably the project's standard test runner, aimed at the matrix-expressions tests.
- Lint/style check: unknown.
- Build: unknown. It may not apply to a pure-Python change.

## Project Structure

**Unknown.** The following must be located in the repository:

- The source file that defines `BlockMatrix` and its element-access logic.
- The matching test file for block matrices.

## Code Style

**Unknown.** Follow the existing conventions of the file being modified.

Comparisons against symbolic sizes should use SymPy's three-valued logic, where a relation can be True, False, or undetermined. Branching on the truthiness of a relational should not be used.

## Testing Strategy

- **Level:** unit tests in the existing block-matrix test module. The location is unknown.
- **Regression test:** the exact example from the issue. Assert that `C[i, 0]` is not equal to `A[i, 0]`, and that it is an unevaluated element of `C`.
- **Cases to cover:**
  - Concrete indices into the first and later blocks, checking the offset arithmetic.
  - A symbolic index with no assumptions, which stays unevaluated.
  - A symbolic index whose block is provable from assumptions, which resolves.
  - The column-direction equivalents of the above.
  - A symbolic first block size, such as `A` being n×1 and `B` being 1×1, with a concrete index like `C[1, 0]`. It stays unevaluated, because `1 < n` is undetermined.
  - Existing all-numeric block matrix tests, which must still pass unchanged.
- **Coverage expectation:** every branch of the index-to-block mapping is exercised. These branches are: provably in this block, provably not in this block, and undetermined.

## Boundaries

- **Always:**
  - Resolve to a block only when membership is provable.
  - Add regression tests for the issue example.
  - Run the existing matrix-expression test suite.
- **Ask first:**
  - Returning `Piecewise` results instead of unevaluated elements.
  - Changing out-of-range error behavior.
  - Changing `BlockDiagMatrix` or other subclasses beyond a shared code path.
  - Altering printing.
- **Never:**
  - Silently pick a block when membership is undetermined.
  - Change results for fully determined numeric cases.
  - Remove or weaken existing tests.

## Success Criteria

- `C[i, 0]` from the issue returns an unevaluated element of `C`, and its pretty-print does not show `(A)[i, 0]`.
- `C[0, 0] == A[0, 0]` and `C[1, 0] == B[0, 0]`.
- Symbolic indices whose block is provable through assumptions resolve to the correct block, with the correct local offset.
- Column indexing follows the same rules as row indexing.
- All pre-existing block-matrix and matrix-expression tests pass.

## Open Questions

1. When the block cannot be determined, is an unevaluated `MatrixElement` of the `BlockMatrix` the preferred result? Or is a `Piecewise` over the candidate blocks wanted?
2. When the row is provably in one block but the column is undetermined, should the result stay fully unevaluated? Or should it partially resolve, for example to an element of a single block row?
3. What should happen with provably out-of-range or negative symbolic indices: raise an error, or return unevaluated? Should current behavior be preserved?
4. Should `BlockDiagMatrix` be checked for, and fixed for, the same defect within this change?
5. Which SymPy versions and branches are the target? Are the repository's test and lint commands as unknown here?