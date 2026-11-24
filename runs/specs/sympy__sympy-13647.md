# Spec: Fix `Matrix.col_insert()` Misplacing Columns After the Insertion Point

## Objective

`Matrix.col_insert(pos, other)` returns a wrong result in SymPy 1.1.1. The inserted columns land in the right place. The original columns that should follow them come from the wrong source indices, so their contents look shifted.

**Reported reproduction (SymPy 1.1.1):**

```python
import sympy as sm
M = sm.eye(6)
V = 2 * sm.ones(6, 2)
M.col_insert(3, V)
```

**Actual output:**

```
⎡1  0  0  2  2  1  0  0⎤
⎢0  1  0  2  2  0  1  0⎥
⎢0  0  1  2  2  0  0  1⎥
⎢0  0  0  2  2  0  0  0⎥
⎢0  0  0  2  2  0  0  0⎥
⎣0  0  0  2  2  0  0  0⎦
```

**Expected output:** the original columns 3–5 of `eye(6)` appear unchanged after the inserted block.

```
⎡1  0  0  2  2  0  0  0⎤
⎢0  1  0  2  2  0  0  0⎥
⎢0  0  1  2  2  0  0  0⎥
⎢0  0  0  2  2  1  0  0⎥
⎢0  0  0  2  2  0  1  0⎥
⎣0  0  0  2  2  0  0  1⎦
```

**Required behavior:** for `R = M.col_insert(pos, V)`, where `M` is `m×n` and `V` is `m×k`:

- `R` has shape `m×(n+k)`.
- `R[:, :pos] == M[:, :pos]`
- `R[:, pos:pos+k] == V`
- `R[:, pos+k:] == M[:, pos:]`

**Users:** anyone building block matrices with `col_insert`. Silent wrong results are a correctness issue.

**Suspected origin:** the reporter suspects a regression from a recent matrix refactor (cc @siefkenj). The faulty logic is likely in the column-index mapping for columns after the insertion point. This is unconfirmed.

## Assumptions

1. This is a regression: `col_insert` gave correct results before the refactor mentioned in the issue.
2. The documented semantics (insert `other` before column `pos`, keep the remaining columns in order) are unchanged. Only the implementation is wrong.
3. The bug can show up whenever `pos > 0` and columns follow the insertion point. It may not be visible when `pos == 0` or `pos == cols`.
4. Other matrix classes (mutable, immutable, sparse) may share the same code path or have their own. All of them must give correct results.
5. `row_insert` may have a symmetric bug if it was refactored the same way. It should be checked but is not confirmed broken.
6. Negative `pos` and `pos` beyond the column count keep their existing normalization or clamping behavior.

## Tech Stack

- Python, SymPy (bug reported in version 1.1.1).
- Other versions and dependencies: unknown.

## Commands

All unknown; the issue does not include them.

- Test: unknown. The project's pytest/`bin/test` invocation is not visible.
- Build/Lint: unknown.

## Project Structure

Unknown. The issue does not show where `col_insert` and its internal helper are implemented, or where matrix tests live.

## Code Style

Unknown. Follow the conventions of the surrounding SymPy matrix code. No snippet is available from the issue.

## Testing Strategy

- Add a regression test using the exact reproduction above (`eye(6).col_insert(3, 2*ones(6, 2))`) and assert the full expected matrix.
- Cover these edge positions:
  - `pos = 0`
  - `pos = cols`
  - `pos` in the middle
  - negative `pos`
  - inserting into an empty matrix
- Use non-symmetric, non-identity matrices with distinct entries (e.g. `Matrix(3, 4, range(12))`). This catches row and column index mix-ups that identity or constant matrices can hide.
- Run the test across each matrix class that exposes `col_insert`, including sparse and immutable variants if they exist.
- Check `row_insert` with analogous tests.
- Framework and test file location: unknown.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix.
  - Keep the public `col_insert` signature and semantics.
  - Run the existing matrix test suite.
- **Ask first:**
  - Changing `pos` normalization or error behavior.
  - Refactoring shared matrix base-class code beyond the faulty index mapping.
  - Touching `row_insert` if it turns out to be correct.
- **Never:**
  - Change expected values in existing tests to match the buggy output.
  - Remove or skip failing tests.
  - Change the public API.

## Success Criteria

- [ ] `sm.eye(6).col_insert(3, 2*sm.ones(6, 2))` equals the expected 6×8 matrix above.
- [ ] For random `M` (m×n), `V` (m×k) and every `pos` in `[0, n]`, `col_insert` satisfies the four slice equalities in the Objective.
- [ ] The behavior holds for every matrix class that implements `col_insert`.
- [ ] `row_insert` is verified correct by analogous tests, or is fixed under the same criteria.
- [ ] The existing matrix test suite passes.

## Open Questions

1. Which commit or refactor introduced the regression, and what was the last correct release? (@siefkenj to confirm.)
2. Do sparse or immutable matrix classes use a separate `col_insert`/`_eval_col_insert` implementation that also needs checking?
3. Is `row_insert` affected by the same refactor?
4. What is the intended behavior for negative or out-of-range `pos`? Should it be pinned down in tests?
5. Should the fix be backported to a 1.1.x patch release?
6. What are the project's exact test commands and test file locations?