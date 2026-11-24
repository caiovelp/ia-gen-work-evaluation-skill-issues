# Spec: Validate `n_neighbors` type in Neighbors estimators

## Objective

Passing a float for `n_neighbors` to a scikit-learn Neighbors estimator currently fails deep inside the Cython tree code. The error message is unhelpful:

```python
from sklearn.neighbors import NearestNeighbors
from sklearn.datasets import make_blobs
X, y = make_blobs()
neighbors = NearestNeighbors(n_neighbors=3.)
neighbors.fit(X)
neighbors.kneighbors(X)
```
```
~/checkout/scikit-learn/sklearn/neighbors/binary_tree.pxi in sklearn.neighbors.kd_tree.NeighborsHeap.__init__()

TypeError: 'float' object cannot be interpreted as an integer
```

**Goal:** catch a non-integer `n_neighbors` early, at the scikit-learn API level, and raise a clear error that names the parameter and the expected type.

The issue mentions two possible policies:

- **Preferred:** raise a helpful error.
- **Alternative:** be lenient and cast to an integer.

This spec adopts the preferred policy (see Assumptions).

**Users:** scikit-learn users who pass `n_neighbors` either in an estimator constructor or as an argument to `kneighbors(...)`.

**Entry points that must be covered:**

1. The constructor parameter, e.g. `NearestNeighbors(n_neighbors=3.)`, followed by `fit` and/or `kneighbors`.
2. The method argument, e.g. `neighbors.kneighbors(X, n_neighbors=3.)`.

The issue states that point 2 must "also work". This spec reads that as "must also be validated with the same helpful error" (see Open Questions).

### Acceptance criteria

- **AC1:** `NearestNeighbors(n_neighbors=3.)` produces a clear, scikit-learn-level error once validation runs. The error is raised before reaching `NeighborsHeap.__init__` / `binary_tree.pxi`.
- **AC2:** `NearestNeighbors(n_neighbors=3).fit(X).kneighbors(X, n_neighbors=3.)` raises the same kind of clear error, again before reaching the tree code.
- **AC3:** The error message names the parameter (`n_neighbors`), states that an integer is expected, and includes the offending value and/or its type.
- **AC4:** Integer values keep working unchanged. This covers both Python `int` and NumPy integer types (assumed, see Open Questions).
- **AC5:** The existing behavior for invalid integer values (e.g. `n_neighbors <= 0`, or `n_neighbors > n_samples`) is not regressed.
- **AC6:** Validation applies regardless of the `algorithm` choice ('kd_tree', 'ball_tree', 'brute', 'auto'). It must not depend on which backend happens to fail.

## Assumptions

1. The resolution is to **raise an error**, not to silently cast floats to int, per the issue author's stated preference.
2. A float with an integral value (e.g. `3.`) is still rejected. It is not cast.
3. NumPy integer scalars (e.g. `np.int64(3)`) are valid integers and must be accepted.
4. Constructor validation follows the scikit-learn convention of not validating in `__init__`. So for the constructor path, the error is raised at `fit` (or at the first use), not at construction time.
5. The fix belongs in shared Neighbors base code, so that all estimators exposing `n_neighbors` benefit. Examples are `NearestNeighbors`, `KNeighborsClassifier` and `KNeighborsRegressor`. The exact class/module layout is unknown, beyond `sklearn/neighbors/` and `sklearn/neighbors/binary_tree.pxi` as seen in the traceback.
6. Booleans are not explicitly addressed. They are assumed out of scope unless trivially covered (see Open Questions).

## Tech Stack

- Python / Cython (`sklearn/neighbors/binary_tree.pxi`, `sklearn.neighbors.kd_tree`, as seen in the traceback).
- NumPy.
- Supported Python/NumPy versions and the validation helper utilities available in this version of scikit-learn: **unknown**.

## Commands

All unknown, because the repository was not visible:

- Build: unknown (an in-place Cython build of scikit-learn is required)
- Test: unknown (likely pytest-based; exact invocation unknown)
- Lint: unknown

## Project Structure

- `sklearn/neighbors/` contains the Neighbors estimators (known from the traceback).
- `sklearn/neighbors/binary_tree.pxi` contains the Cython tree implementation where the current failure occurs (known from the traceback).
- The location of the Neighbors base classes, the location of the tests for `sklearn/neighbors`, and the location of the changelog / what's-new file are all **unknown**.

## Code Style

Follow the existing scikit-learn conventions in `sklearn/neighbors/`; none are visible in the issue. Error messages should follow the existing scikit-learn style, for example naming the parameter and showing the received value. The exact style is unknown.

## Testing Strategy

- **Framework:** unknown (presumed pytest, as in scikit-learn).
- **Required tests:**
  - A float `n_neighbors` in the constructor raises the expected exception type, with a message matching `n_neighbors` (AC1, AC3).
  - A float `n_neighbors` passed to `kneighbors(X, n_neighbors=...)` raises the expected exception type with the expected message (AC2, AC3).
  - Ideally, both cases are parametrized over `algorithm` values (AC6) and over the affected estimators (AC5 scope).
  - Integer and NumPy-integer `n_neighbors` still work (AC4).
- **Location of the test file:** unknown.

## Boundaries

- **Always:**
  - Validate at the Python/API level before calling into Cython tree code.
  - Keep messages explicit about the parameter name and the expected type.
  - Add regression tests for both entry points.
- **Ask first:**
  - Choosing lenient casting instead of an error.
  - Changing the exception type of existing `n_neighbors` checks.
  - Extending validation to other methods/functions (e.g. `kneighbors_graph`) or other integer params.
  - Modifying Cython code.
- **Never:**
  - Silently change results for valid integer inputs.
  - Validate inside `__init__`, contrary to scikit-learn convention.
  - Remove or weaken existing tests.

## Success Criteria

- Both snippets from the issue raise a clear error that names `n_neighbors` and states that an integer is expected. Neither traceback reaches `NeighborsHeap.__init__`.
- New regression tests cover both entry points and pass.
- The existing `sklearn/neighbors` test suite still passes.
- Integer inputs (Python and NumPy) behave exactly as before.

## Open Questions

1. **Meaning of "also works":** the issue says `neighbors.kneighbors(X, n_neighbors=3.)` must "also work". Does that mean it raises the same helpful error, or that it should succeed? This spec assumes the former, consistent with the "raise an error" preference.
2. **Error or cast:** should we raise an error (preferred by the issue author) or cast floats to int? Is that decision final?
3. **Exception type:** should a non-integer type raise `TypeError` or `ValueError`? What is the existing convention for `n_neighbors <= 0` in this codebase?
4. **Integral floats:** should integral floats such as `3.0` be rejected, the same as `3.5`?
5. **Scope of estimators:** which estimators and functions should get the check? Candidates include `KNeighborsClassifier`, `KNeighborsRegressor`, `kneighbors_graph`, `KNeighborsMixin.kneighbors_graph`, and other estimators that use neighbors internally (e.g. `LocalOutlierFactor`, if present in this version).
6. **Booleans:** should `n_neighbors=True` be rejected?
7. **Shared helper:** is there an existing scikit-learn validation helper for integer parameters that should be reused?
8. **Changelog:** is a changelog / what's-new entry required, and where does it go?