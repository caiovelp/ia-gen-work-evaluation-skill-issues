# Spec: Support Construction of Empty `Array` (`sympy.Array([])`)

## Objective

In SymPy 1.4, `sympy.Array([])` raises an unhandled exception. `sympy.Matrix([])` succeeds for the same input.

```
ValueError: not enough values to unpack (expected 2, got 0)
```

The failure occurs during shape inference:

- `ndim_array.py`, `_scan_iterable_shape`, inner function `f`, line 120: `elems, shapes = zip(*[f(i) for i in pointer])`.
- For an empty `pointer`, `zip(*[])` yields nothing to unpack.

**Goal:** Constructing an N-dim array from an empty iterable should produce a valid empty array instead of crashing. This brings `Array` in line with `Matrix`, which already accepts empty input.

**Users:** SymPy users and downstream code that builds arrays programmatically. Such code may legitimately produce zero-length data, for example from filtered lists or generated components.

**User story:** As a SymPy user, I can call `Array([])` and get an empty array object. I can then inspect it (`shape`, `len`, `rank`, `tolist`) without errors, just as I can with `Matrix([])`.

**Scope:** This is a single capability (empty-array construction), so no capability map is needed.

## Assumptions

1. The issue's question "is this intended?" is answered "no". Empty arrays should be supported, given the parity with `Matrix([])`.
2. `Array([])` should produce a rank-1 array with `shape == (0,)`. This mirrors NumPy, where `np.array([]).shape == (0,)`. See Open Questions.
3. The fix belongs in shape inference (`_scan_iterable_shape` / `_handle_ndarray_creation_inputs` in `sympy/tensor/array/ndim_array.py`). The traceback points there. The exact change is out of scope for this spec.
4. Every concrete array class that shares this creation path should behave consistently, because they all go through `_handle_ndarray_creation_inputs`:
   - immutable dense
   - mutable dense
   - (likely) the sparse variants

   This sharing is inferred and not verified.
5. The behavior of non-empty arrays must not change.
6. The fix targets the current development branch, not a 1.4 backport.

## Tech Stack

- **Language:** Python. The traceback shows 3.7; the supported range for the target branch is unknown.
- **Library:** SymPy, module `sympy.tensor.array`. Files seen in the traceback:
  - `sympy/tensor/array/dense_ndim_array.py`
  - `sympy/tensor/array/ndim_array.py`
- **Dependencies:** Other dependencies and versions are unknown.

## Commands

Unknown. The repository was not inspected.

- **Build:** unknown. SymPy is pure Python, so no build step is assumed.
- **Test:** unknown. The test runner and invocation are to be confirmed, e.g. SymPy's own test runner vs. pytest.
- **Lint / code quality:** unknown.
- **Repro (taken from the issue):**
  ```python
  from sympy import Array
  Array([])
  ```

## Project Structure

Only the following paths are known, from the traceback:

```
sympy/tensor/array/ndim_array.py        → base NDimArray; shape inference (_scan_iterable_shape, _handle_ndarray_creation_inputs)
sympy/tensor/array/dense_ndim_array.py  → dense array classes (__new__, _new)
```

- **Test location for the array module:** unknown. Presumably there is a `tests/` directory under `sympy/tensor/array/`, but this is unverified.
- **Sparse array module path:** unknown.

## Code Style

The project's code style conventions were not visible in the issue and are unknown. Follow the existing style of `ndim_array.py`.

Expected user-facing behavior, as an illustrative target only (not implementation):

```python
>>> from sympy import Array
>>> a = Array([])
>>> a.shape
(0,)
>>> len(a)
0
>>> a.rank()
1
>>> a.tolist()
[]
```

## Testing Strategy

- **Framework:** unknown (to confirm from the repository).
- **Regression tests** in the existing test file(s) for N-dim array creation:
  - `Array([])` constructs without error, with the expected `shape`, `len`, `rank`, and `tolist()`.
  - The same behavior for each concrete array class that uses the shared creation path: immutable/mutable dense, and sparse if applicable.
  - Explicit shapes:
    - `Array([], (0,))` is consistent with the inferred-shape case.
    - The behavior of `Array([], ())` and of other zero-size shapes, e.g. `(0, 3)`, is defined once the Open Questions are resolved.
  - Equality: an empty array equals another empty array of the same shape.
- **Existing tests:** all `sympy.tensor.array` tests continue to pass, so non-empty construction is unchanged.
- **Coverage target:** unknown. At minimum, the empty-iterable branch of shape inference must be exercised.

## Boundaries

**Always:**
- Add regression tests reproducing the issue.
- Keep behavior for non-empty inputs unchanged.
- Apply the behavior consistently across array classes that share the creation path.

**Ask first:**
- Choosing semantics for ambiguous inputs (see Open Questions):
  - nested empties such as `[[]]`
  - `Array([], ())`
  - shape/data size mismatches
- Changing the public behavior of `Matrix` or any non-array API.
- Changing how a scalar / rank-0 array is represented.

**Never:**
- Silence the error with a broad `try/except` that masks other malformed inputs.
- Alter or remove existing tests to make the change pass.
- Introduce new dependencies.

## Success Criteria

1. `Array([])` returns an array object without raising. `shape == (0,)`, `len == 0`, `rank() == 1`, and `tolist() == []`, assuming Assumption 2 is confirmed.
2. Criterion 1 holds for every array class that shares the N-dim creation path: immutable/mutable dense, and sparse if applicable.
3. `Array([], (0,))` produces an array equal to `Array([])`.
4. Non-empty array construction and all existing `sympy.tensor.array` tests are unaffected.
5. New regression tests covering criteria 1–3 exist and pass.
6. Malformed inputs still raise clear errors and do not silently produce wrong shapes. Examples:
   - ragged nesting
   - a shape whose size differs from the data length

## Open Questions

1. **Inferred shape:** Should `Array([])` have shape `(0,)` (NumPy-like, rank 1) or `()`? Note that `()` currently denotes a rank-0/scalar array.
2. **Nested empties:** What should `Array([[]])` infer? Is `(1, 0)` expected, consistent with NumPy? What about `Array([[], []])`?
3. **Explicit zero-size shapes:** Should `Array([], (0, 3))` or `Array([], (3, 0))` be accepted? What does `tolist()` return for them?
4. **`Array([], ())`:** Should it be an error (size mismatch: rank-0 needs 1 element) or something else?
5. **Sparse variants:** Do the sparse array classes share `_handle_ndarray_creation_inputs`? Must they also support empty construction in this change?
6. **Matrix parity:** `Matrix([])` yields a 0×0 matrix. Should conversions between an empty `Array` and `Matrix` be in scope (e.g. `Array(Matrix([]))` or `.tomatrix()` on an empty array), or deferred?
7. **Empty-array operations:** Should operations be verified in this change, or left to follow-ups? Examples include indexing errors, iteration, arithmetic, `tensorproduct`, and `derive_by_array`.
8. **Logistics:** What are the correct test command, test file location, and target branch? Are backports expected?