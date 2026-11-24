# Spec: Fix `Matrix.is_upper` raising `IndexError` for tall (rows > cols) matrices

## Objective

`Matrix.is_upper` raises `IndexError` when called on a matrix with more rows than columns, for example `sympy.zeros(4, 2).is_upper`. It should return a boolean.

**Root cause (from the issue):** the implementation is

```python
return all(self[i, j].is_zero
           for i in range(1, self.rows)
           for j in range(i))
```

The inner loop runs `j` up to `i - 1` without checking `self.cols`. For a 4x2 matrix it visits `(2, 1)`, `(3, 0)`, `(3, 1)` and `(3, 2)`. Column index `2` is out of range, so `a2idx` raises the error.

**Who is affected:** any SymPy user or internal caller that checks `is_upper` on a non-square matrix with `rows > cols`. This may include callers that test triangularity before solving or decomposing a matrix (unverified).

**What success looks like:** `is_upper` returns a correct boolean for matrices of any shape. "Upper triangular" for a rectangular matrix means every entry `(i, j)` with `i > j` is zero, and only indices that exist in the matrix are checked.

User stories:
- As a user, `sympy.zeros(4, 2).is_upper` returns `True` instead of raising.
- As a user, a tall matrix with a nonzero entry below the main diagonal (for example at `(3, 1)` of a 4x2 matrix) returns `False` from `is_upper`.
- As a user, square and wide (rows < cols) matrices behave exactly as before.

## Assumptions

1. The definition of upper triangular for a non-square matrix is: `A[i, j]` is zero for all valid `i > j`. This is the standard definition, and it matches the current behaviour for square and wide matrices.
2. The intended fix limits the column range to valid indices, so that `j < min(i, self.cols)`. The return type and semantics stay the same; only out-of-range indexing is removed.
3. The traceback uses Python 2 `print` syntax, which suggests an older SymPy version. I assume the same defect exists in the code base being fixed, possibly at a different file or line.
4. `is_upper` is a property, as shown by `.is_upper` in the reproduction, even though the issue title writes `is_upper()`. Its public signature must not change.
5. The `.is_zero` semantics stay unchanged. Symbolic entries whose zero-ness cannot be decided still behave as they do today; that is out of scope.
6. Only `is_upper` is known to be broken. Sibling properties such as `is_lower`, `is_upper_hessenberg`, `is_lower_hessenberg` and `is_diagonal` might share the same indexing pattern, but the issue does not show them (see Open Questions).
7. The bug applies to all matrix classes that inherit this implementation from `sympy/matrices/matrices.py`: dense, mutable and immutable. Whether sparse matrices override it is unknown.

## Tech Stack

- Language: Python. The exact supported versions are unknown, but the issue's example uses Python 2 syntax.
- Library: SymPy, at an unknown version.
- Files referenced in the issue's traceback (line numbers may differ in the target revision):
  - `sympy/matrices/matrices.py`: `is_upper` (around line 1112), `extract` (around line 352), `a2idx` (around line 5261)
  - `sympy/matrices/dense.py`: `__getitem__` (around line 119)
- Other dependencies and versions: unknown.

## Commands

The issue does not state any commands. All of the following are **unknown** and must be confirmed from the repository:

```
Build:        unknown
Test (all):   unknown
Test (matrices module only): unknown
Lint:         unknown
Dev / REPL reproduction:     python -c "import sympy; print(sympy.zeros(4, 2).is_upper)"   # derived from the issue's reproduction
```

## Project Structure

Known from the issue:
```
sympy/matrices/matrices.py   → Matrix base implementation, including is_upper, extract, a2idx
sympy/matrices/dense.py      → Dense matrix implementation, including __getitem__
```
Unknown: where matrix tests live and how they are named. A likely location is a `tests/` directory under `sympy/matrices/`, but this must be confirmed.

## Code Style

The existing style, taken from the issue, is a generator expression inside `all(...)` that iterates over index ranges and checks `.is_zero`:

```python
return all(self[i, j].is_zero
           for i in range(1, self.rows)
           for j in range(i))
```

Conventions to keep:
- `is_upper` stays a property that returns a boolean, with the same name and no new parameters.
- Use the same idiom, `all(...)` over a generator, and stay consistent with neighbouring properties in the same file.
- The project's line-length, formatting and docstring conventions are unknown; follow the surrounding code.
- If the docstring has examples (doctests), they may need a tall-matrix example. The doctest conventions are unknown.

## Testing Strategy

- **Framework:** unknown. Confirm what the SymPy test suite uses in this revision.
- **Location:** unknown. It is probably the existing matrices test module, next to any current `is_upper` tests.
- **Test levels:**
  - Unit tests for `is_upper` across matrix shapes, which is the main concern.
  - A regression test that reproduces the issue exactly: `zeros(4, 2).is_upper` must not raise.
  - Optionally, a doctest in the `is_upper` docstring showing a tall matrix, if the project uses doctests.
- **Shape coverage required:**
  - Tall (rows > cols): all zeros → `True`; zero below the diagonal but nonzero on or above it → `True`; nonzero strictly below the diagonal → `False`.
  - Square: existing behaviour unchanged.
  - Wide (rows < cols): existing behaviour unchanged.
  - Edge shapes: a single column `n x 1`, a single row `1 x n`, and `1 x 1`. Empty matrices (`0 x n`, `n x 0`) are included only if the project supports them (see Open Questions).
- **Coverage expectations:** unknown. At minimum, every branch of the changed expression must be exercised by the shapes above.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Run the matrices test suite (command unknown) before considering the change done.
  - Keep `is_upper`'s public signature, return type and semantics for square and wide matrices.
  - Follow the existing code idiom in `sympy/matrices/matrices.py`.
- **Ask first:**
  - Changing sibling properties (`is_lower`, Hessenberg checks, `is_diagonal`, and so on), even if they show the same bug.
  - Changing `a2idx`, `extract` or `__getitem__` behaviour. These are shared indexing paths; the bug is in the caller's index ranges, not in the bounds checking.
  - Changing how `.is_zero` / `None` (undecidable) entries are treated.
  - Changes to sparse or other matrix subclasses beyond what inherits the base fix.
- **Never:**
  - Catch or suppress `IndexError` as the fix. That hides the defect instead of computing the correct index set.
  - Weaken the bounds checking in `a2idx`.
  - Remove or loosen existing `is_upper` tests.
  - Change unrelated matrix behaviour.

## Success Criteria

1. `sympy.zeros(4, 2).is_upper` returns `True` and raises no exception.
2. For any `m x n` matrix `A` with `m > n`, `A.is_upper` returns `True` if and only if `A[i, j].is_zero` holds for every `0 <= j < n` with `j < i < m`.
3. A 4x2 matrix with a nonzero entry at `(3, 1)` or `(2, 0)` returns `False`.
4. A 4x2 matrix with nonzero entries only at `(0, 0)`, `(0, 1)` or `(1, 1)` returns `True`.
5. `is_upper` never indexes outside `[0, rows) x [0, cols)` for any shape.
6. Results for square and wide matrices are identical to the behaviour before the change. All existing `is_upper` tests still pass.
7. Edge shapes `n x 1`, `1 x n` and `1 x 1` return correct results without raising.
8. A regression test for the exact reproduction in the issue is committed.
9. The full matrices test suite passes (command unknown).

## Open Questions

1. **Sibling properties:** do `is_lower`, `is_upper_hessenberg`, `is_lower_hessenberg`, `is_diagonal` or other shape predicates have the same out-of-range pattern for tall or wide matrices? Should they be fixed in this change or tracked separately?
2. **Sparse matrices:** does `SparseMatrix` (or any other subclass) override `is_upper`? If so, does it need the same fix and the same tests?
3. **Empty matrices:** what should `is_upper` return for `0 x n` and `n x 0` matrices? Should they be part of the test matrix?
4. **Target version:** which SymPy revision or branch is being fixed? The traceback line numbers and Python 2 syntax suggest an older code base. Should the fix be backported?
5. **Commands and test layout:** what are the exact commands to run the matrices tests and the doctests, and where do the existing `is_upper` tests live?
6. **Docstring:** should the `is_upper` docstring state the rectangular-matrix definition explicitly and include a tall-matrix example?
7. **Callers:** do any internal callers, such as solvers or decompositions, depend on `is_upper` raising for tall matrices, or work around it? Changing the result from raising to returning a boolean could change their control flow.