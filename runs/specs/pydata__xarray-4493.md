# Spec: Preserve lazy (dask) data when a DataArray is wrapped in a `(dims, data)` tuple

## Objective

When a dask-backed `xarray.DataArray` is passed as the data element of a `(dims, data)` tuple, xarray currently converts it to an in-memory `numpy.ndarray`. That evaluates the dask graph eagerly. Two public entry points show the problem:

1. **`Dataset.update`**: after `ds.update({"foo": (("x", "y"), ds.foo[1:, :]), ...})`, `ds.foo` is backed by numpy instead of dask.
2. **`Dataset` constructor**: `xr.Dataset({"a": (("x", "y"), ds.a)})` gives `type(ds2.a.data) == numpy.ndarray` when `ds.a` was dask-backed.

Both paths probably share one root cause: variable creation from a `(dims, DataArray)` tuple. The issue shows the expected behaviour by contrast. Passing a `DataArray` directly (`xr.Dataset({"a": xr.DataArray(x, dims=...)})`) keeps it lazy. Passing the raw dask array in the tuple is also expected to stay lazy.

**Users:** anyone building or updating Datasets with dask-backed arrays, for example large or out-of-core data. Eager evaluation can be slow, can exhaust memory, and silently changes the array type.

**Acceptance criteria (user stories):**
- As a user, when I build a Dataset from `{"name": (dims, dask_backed_dataarray)}`, the resulting variable is still dask-backed, keeps its chunks, and nothing is computed.
- As a user, when I call `Dataset.update` with `{"name": (dims, dask_backed_dataarray)}`, the updated variable is still dask-backed, keeps its chunks, and nothing is computed.
- As a user, the values I get back after computing are identical to today's (eager) results.

## Assumptions

1. The bug is in the shared code path that turns a `(dims, data)` tuple into a `Variable`. The suspected cause is that a `DataArray` passed as `data` is unwrapped via its `.values` (forcing computation) rather than its underlying lazy data. This is a hypothesis and has not been confirmed against the source.
2. A fix should unwrap a `DataArray` in the tuple to its underlying data (for example `.data` or `.variable._data`), keeping duck arrays (dask) intact rather than coercing them to numpy.
3. The expected semantics for dims, attrs and coordinates of the DataArray inside a tuple are **unchanged**. The tuple's `dims` take precedence. Whether the inner DataArray's coords and attrs are dropped or kept stays whatever it is today; only laziness changes.
4. The behaviour should hold for the dask versions xarray currently supports. The issue's environment is xarray 0.16.0 and dask 2.20.0; the target branch's minimum dask version is unknown.
5. Other lazy or duck-array backends (for example pint, sparse, lazily indexed backend arrays) wrapped in a DataArray inside a tuple should also not be coerced to numpy if that was not already intended. Scope is limited to not regressing them.
6. The fix is internal. No public API signature changes.

## Tech Stack

- Python library: xarray. The target version is unknown; the issue reports 0.16.0.
- Key dependencies: numpy, pandas, dask (optional). Versions supported by the target branch are unknown.

## Commands

Unknown. The repository is not visible. Likely candidates need confirmation:
- Test: unknown (pytest is used per the environment report; the exact invocation and flags are unknown)
- Lint/format: unknown
- Build: unknown

## Project Structure

Unknown. The repository is not visible. The relevant areas, by responsibility only:
- Variable construction from tuples and other array-likes (`(dims, data)` handling, data coercion)
- Dataset construction and `Dataset.update` (merge logic feeding variable construction)
- Existing dask-specific test module(s) and dataset/variable test modules

Exact file paths are unknown.

## Code Style

Unknown. Follow the existing conventions in the touched modules. No code snippet is available from the issue.

## Testing Strategy

- **Framework:** pytest (per the reported environment). Exact configuration is unknown.
- **Laziness detection:** use whatever helper the existing dask tests use to assert that no computation happens, such as a raise-on-compute scheduler or compute counter. Its name is unknown.
- **Regression tests to add** (in the existing dask test location, unknown path):
  1. Dataset constructor: `xr.Dataset({"a": (("x", "y"), dask_backed_dataarray)})` gives a variable whose `.data` is a dask array, with zero computes and chunks preserved.
  2. `Dataset.update` with `{"foo": (("x", "y"), ds.foo[1:, :]), "bar": ("x", ds.bar[1:])}` (the issue's MCVE) leaves `ds.foo` dask-backed, with zero computes and chunks matching the sliced input.
  3. Single-dimension case from the second report: `xr.Dataset({"a": ("d0", xr.DataArray(da.random.random(10)))})` stays lazy.
  4. Values after `.compute()` equal the numpy-equivalent result.
- **Non-regression:** the full existing test suite passes, especially tests for variable construction from tuples, DataArray-in-tuple semantics, and non-dask inputs (numpy, pandas, lists).
- **Coverage expectations:** unknown. New tests must cover both reported entry points.

## Boundaries

- **Always:**
  - Add regression tests reproducing both reported cases before changing behaviour.
  - Keep numeric results identical.
  - Run the full test suite.
  - Add a changelog/"what's new" entry if the project keeps one (location unknown).
- **Ask first:**
  - Changing what happens to the inner DataArray's coords, attrs or name when it is wrapped in a tuple.
  - Changing coercion behaviour for non-dask inputs.
  - Emitting new warnings.
  - Touching public API signatures.
- **Never:**
  - Compute dask arrays as a side effect of construction or update.
  - Remove or weaken existing tests.
  - Add new dependencies.

## Success Criteria

- [ ] `xr.Dataset({"a": (("x", "y"), ds.a)})` with dask-backed `ds.a` gives `isinstance(ds2.a.data, dask.array.Array)`, with no compute triggered.
- [ ] The issue's `Dataset.update` MCVE leaves `ds.foo` dask-backed with chunks equal to those of `ds.foo[1:, :]` before the update, with no compute triggered.
- [ ] `xr.Dataset({"a": ("d0", xr.DataArray(da.random.random(10)))})` stays dask-backed, with no compute triggered.
- [ ] Computed values match the eager equivalents.
- [ ] Existing behaviour for numpy, list and pandas inputs, and existing DataArray-in-tuple metadata semantics, are unchanged (the existing test suite passes).
- [ ] The new regression tests fail before the fix and pass after it.

## Open Questions

1. Is coercing a DataArray in a `(dims, data)` tuple to numpy ever intentional, for example as a documented way to strip metadata or to materialise data? If so, is a deprecation path needed instead of a silent behaviour change?
2. What should happen to the inner DataArray's coordinates, attrs and name when it is wrapped in a tuple? Should they stay dropped, as presumably today, and should dims that conflict with the DataArray's own dims raise, warn or silently override?
3. Should the fix also preserve other duck arrays (pint, sparse, cupy) and lazily indexed backend arrays wrapped in a DataArray, or is dask the only required scope?
4. Do other entry points share this path and need coverage too, such as `Dataset.assign`, `__setitem__` with tuples, `DataArray` coords given as tuples, or `merge`?
5. Which xarray branch/version is the target, and what is its minimum supported dask version?
6. What are the exact test, lint and build commands, and the file locations for variable construction and dask tests?