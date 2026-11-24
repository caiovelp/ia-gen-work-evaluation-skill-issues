# Spec: Restore Correct Shape for `Matrix.hstack` / `Matrix.vstack` with Zero-Dimension Matrices

## Assumptions

1. The 1.0 behavior (`(0, 6)`) is the correct, intended behavior, and the 1.1 result (`(0, 3)`) is a regression, not a deliberate change.
2. `hstack` and `vstack` should be symmetric. The issue only demonstrates `hstack`, but the title names `vstack` as well. So `vstack` of matrices with shapes `(0,0), (1,0), (2,0), (3,0)` is assumed to have the same defect and should return `(6, 0)`.
3. The likely root cause is an internal shortcut for "empty" (null) matrices. For example, a join path that discards or replaces a matrix when `rows == 0` or `cols == 0`, which drops the column count of the preceding accumulated result. This is an unverified hypothesis. The repository was not inspected.
4. The fix belongs in the shared matrix base or common layer that all matrix classes inherit from. It is not specific to the mutable dense `Matrix` class. The exact module and file are unknown.
5. Shape rules follow standard block-matrix concatenation:
   - **hstack:** the result has the common row count and the **sum** of column counts.
   - **vstack:** the result has the **sum** of row counts and the common column count.
   - A zero-size dimension is still a valid dimension that must agree or be summed.
6. Matrices with a mismatched non-joined dimension should still raise a shape error. For example, hstack of `(0, 2)` and `(1, 2)` should fail. The exception is a fully empty `(0, 0)` matrix: it is assumed to be compatible with any shape, as it was in 1.0. This needs confirmation (see Open Questions).
7. Element values and order in the result must be unchanged for non-degenerate inputs.

## Objective

Restore correct, consistent shape computation for `Matrix.hstack` and `Matrix.vstack` when any input matrix has a zero dimension.

- **User:** SymPy users who build matrices incrementally or programmatically. In this kind of code, empty blocks such as `(0, n)` and `(n, 0)` occur naturally.
- **Problem:** In SymPy 1.1, `Matrix.hstack` of `(0,0), (0,1), (0,2), (0,3)` returns shape `(0, 3)`. In SymPy 1.0 it returned `(0, 6)`.
- **Inconsistency:** The equivalent case with one row works correctly. Shapes `(1,0), (1,1), (1,2), (1,3)` give `(1, 6)`.
- **Why it matters:** The wrong shape silently corrupts downstream shape logic. Later operations then fail, or worse, succeed with the wrong dimensions.

**Acceptance criteria (user stories):**

- As a user, when I hstack matrices with 0 rows, the column counts are summed, exactly as they are for matrices with ≥1 row.
- As a user, when I vstack matrices with 0 columns, the row counts are summed, exactly as they are for matrices with ≥1 column.
- As a user, I get the same shape results regardless of the concrete matrix class:
  - mutable dense
  - immutable dense
  - sparse variants, if they share `hstack`/`vstack`

## Tech Stack

- Language: Python. The supported versions for this SymPy line are unknown.
- Library: SymPy. The regression was introduced between 1.0 and 1.1. The target branch or version for the fix is unknown.
- Relevant APIs: `Matrix.hstack`, `Matrix.vstack`, `Matrix.zeros`, `.shape`. The underlying `row_join`/`col_join` may be involved; this is unverified.

## Commands

| Purpose | Command |
|---|---|
| Reproduce | `python -c "import sympy as sy; print(sy.Matrix.hstack(*[sy.Matrix.zeros(0, i) for i in range(4)]).shape)"`, expected `(0, 6)` |
| Build | Unknown (not visible in issue) |
| Test | Unknown (project test runner and invocation not visible in issue) |
| Lint | Unknown |

## Project Structure

Unknown. The issue does not show the repository layout, so the following are all unknown:

- the location of the matrix source modules
- which module defines `hstack`/`vstack`
- where matrix tests live

## Code Style

Unknown from the issue. Follow the existing conventions of the SymPy matrices module and its test files. New tests should mirror the reproduction style from the issue:

```python
M1 = Matrix.zeros(0, 0)
M2 = Matrix.zeros(0, 1)
M3 = Matrix.zeros(0, 2)
M4 = Matrix.zeros(0, 3)
assert Matrix.hstack(M1, M2, M3, M4).shape == (0, 6)
```

## Testing Strategy

- **Level:** Unit tests in the existing matrix test suite. The location and framework are unknown; the framework is presumably whatever SymPy's matrix tests already use.
- **Regression cases (required):**
  - hstack of `(0,0),(0,1),(0,2),(0,3)` → `(0, 6)`
  - vstack of `(0,0),(1,0),(2,0),(3,0)` → `(6, 0)`
  - hstack of `(1,0),(1,1),(1,2),(1,3)` → `(1, 6)` (must remain correct)
  - vstack of `(0,1),(1,1),(2,1),(3,1)` → `(6, 1)`
- **Edge cases:**
  - hstack/vstack with a single argument returns that matrix's shape.
  - hstack/vstack with no arguments: existing behavior is preserved (unknown; see Open Questions).
  - All inputs `(0,0)` → `(0, 0)`.
  - `(0, 0)` appears at the start, the middle, and the end of the argument list.
  - Mixed zero-width and non-zero-width blocks, e.g. hstack of `(2,0),(2,3),(2,0)` → `(2, 3)`, with element values preserved.
- **Error cases:** Incompatible non-joined dimensions still raise the existing shape error. Example: hstack of `(0,2)` and `(1,2)`.
- **Class coverage:** Run the regression cases against every matrix class that exposes `hstack`/`vstack`. The full list of classes is unknown.
- **Direct joins:** Cover `row_join`/`col_join` directly with the same empty-dimension cases if they are the underlying mechanism.
- **Coverage expectation:** All new branches in the join or stack logic are exercised. The project's numeric coverage threshold is unknown.

## Boundaries

- **Always:**
  - Add regression tests that fail before the fix and pass after.
  - Keep `hstack`/`vstack` behavior symmetric.
  - Preserve element values and ordering.
  - Run the full matrix test suite.
- **Ask first:**
  - Changing which mismatched-shape combinations raise errors versus being accepted.
  - Changing the special-case semantics of `(0, 0)` matrices.
  - Touching sparse-matrix-specific join implementations.
  - Any change to public method signatures.
- **Never:**
  - Change the result for non-degenerate inputs.
  - Remove or weaken existing tests.
  - Special-case only the exact example from the issue instead of fixing the general rule.

## Success Criteria

1. `Matrix.hstack(Matrix.zeros(0,0), Matrix.zeros(0,1), Matrix.zeros(0,2), Matrix.zeros(0,3)).shape == (0, 6)`.
2. `Matrix.vstack(Matrix.zeros(0,0), Matrix.zeros(1,0), Matrix.zeros(2,0), Matrix.zeros(3,0)).shape == (6, 0)`.
3. `Matrix.hstack(Matrix.zeros(1,0), Matrix.zeros(1,1), Matrix.zeros(1,2), Matrix.zeros(1,3)).shape == (1, 6)` (unchanged).
4. For any compatible inputs, the shape is determined by these two rules alone. It never depends on whether a dimension happens to be zero.
   - hstack: rows are the common row count; columns are the sum of the column counts.
   - vstack: rows are the sum of the row counts; columns are the common column count.
5. Criteria 1–4 hold for every matrix class sharing these methods.
6. Incompatible shapes still raise the same exception type as before.
7. The existing matrix test suite passes with no modifications to existing assertions.

## Open Questions

1. Is the 1.0 result `(0, 6)` definitively the intended behavior? Did any 1.1 changelog or discussion intentionally alter empty-matrix stacking?
2. Should a `(0, 0)` matrix stay universally compatible in hstack/vstack, acting as an identity element regardless of the other operands' shapes? Or should only matching non-joined dimensions be allowed? For example, should hstack of `(0,0)` and `(2,3)` succeed with `(2, 3)`?
3. Should hstack of `(0, n)` and `(k, m)` with `k > 0` be an error, or be accepted? What did 1.0 do?
4. Which matrix classes must be covered (dense mutable/immutable, sparse mutable/immutable, others)? Do any of them have their own `row_join`/`col_join` implementations?
5. What is the expected behavior of `hstack()`/`vstack()` with zero arguments?
6. Which branch or release should the fix target? Is a backport to the 1.1.x line required?
7. What are the project's exact test, lint, and build commands, and where are the matrix tests located?