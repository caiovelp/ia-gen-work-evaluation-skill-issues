# Spec: Fix `to_unstacked_dataset` Roundtrip for Single-Dimension Variables

## Objective

`DataArray.to_unstacked_dataset` should invert `Dataset.to_stacked_array`. Today the roundtrip fails when every stacked variable has only the sample dimension(s). In that case nothing is left to stack beyond the variable name.

**Who is affected:** Users who stack several variables into one array (for example, to feed a model) and later need the original `Dataset` back.

**Current behavior:**

```python
arr = xr.DataArray(np.arange(3), coords=[("x", [0, 1, 2])])
data = xr.Dataset({"a": arr, "b": arr})
stacked = data.to_stacked_array('y', sample_dims=['x'])
unstacked = stacked.to_unstacked_dataset('y')
# MergeError: conflicting values for variable 'y' on objects to be combined.
# You can skip this check by specifying compat='override'.
```

**Desired behavior:** `stacked.to_unstacked_dataset('y')` returns a `Dataset` equal to `data`. It must not raise, and it must not leave a leftover `y` coordinate behind.

**User story:** As a user who stacks variables with `to_stacked_array(..., sample_dims=[...])`, I want `to_unstacked_dataset` to give me back my original `Dataset`, whatever the dimensionality of the variables.

## Assumptions

1. The bug is in `DataArray.to_unstacked_dataset`, not in `Dataset.to_stacked_array`. The stacked array produced in the MCVE is assumed to be valid and correctly shaped.
2. The `MergeError` probably comes from the per-variable pieces still carrying a scalar coordinate for the stacked dimension (`y`). That coordinate has a different value for each variable, so merging the pieces conflicts. This is a hypothesis to confirm during investigation, not a prescribed fix.
3. The roundtrip contract is `to_stacked_array(...).to_unstacked_dataset(...)`, judged with `Dataset.identical` or at least `Dataset.equals`. Which of the two is an open question.
4. The fix must not change behavior for cases that already work. This includes variables with extra dimensions beyond `sample_dims`, and mixes of 1-D and N-D variables.
5. The fix must not suppress the conflict globally, for example by switching to `compat='override'` unconditionally. Real conflicts in other coordinates should still surface.
6. The reported version is xarray 0.15.1. The fix targets the current development branch.
7. Dtype upcasting that `to_stacked_array` itself causes is out of scope. That happens when variables of different dtypes are stacked together.

## Tech Stack

- Python library: xarray. The reporter uses 0.15.1; the target branch is unknown.
- Key dependencies, per the issue environment: numpy, pandas (the `MultiIndex` for the stacked dimension).
- Test framework: pytest is listed in the reporter's environment. The project's own test tooling is **unknown, not visible in the issue**.

## Commands

**Unknown, not visible in the issue.** These need confirming from the repository:

- Build/install: unknown
- Test: unknown (pytest is likely; exact invocation and target test file unknown)
- Lint/format: unknown

## Project Structure

**Unknown, not visible in the issue.** Locations still to be identified:

- The implementation of `DataArray.to_unstacked_dataset`: unknown file
- The implementation of `Dataset.to_stacked_array`: unknown file
- Existing tests covering the stack/unstack roundtrip: unknown file(s)
- Docs/changelog entry location (e.g. a "what's new" file): unknown

## Code Style

Follow the existing conventions of the module that contains `to_unstacked_dataset`. Those conventions are not visible here.

The regression test should mirror the MCVE, in this illustrative shape. The test name and placement are to be decided.

```python
def test_to_stacked_array_to_unstacked_dataset_single_dim():
    arr = xr.DataArray(np.arange(3), coords=[("x", [0, 1, 2])])
    data = xr.Dataset({"a": arr, "b": arr})
    stacked = data.to_stacked_array("y", sample_dims=["x"])
    unstacked = stacked.to_unstacked_dataset("y")
    assert_identical(data, unstacked)  # helper name per project conventions
```

## Testing Strategy

- **Level:** Unit tests in the project's existing test suite, next to the current `to_stacked_array` / `to_unstacked_dataset` tests (location unknown).
- **Regression test:** Encode the exact MCVE (all variables 1-D, sharing sample dim `x`) as a failing test before the fix.
- **Additional cases to cover:**
  - All variables have only the sample dims, with more than one sample dim (e.g. `sample_dims=['x', 't']`) if supported.
  - Variables with different values (e.g. `a = arr`, `b = arr * 2`), so the test checks that values map back to the right variable names.
  - Mixed: one 1-D variable and one variable with an extra non-sample dimension. This path already works and must keep working.
  - A single variable only.
- **Existing tests:** All current stack/unstack tests must keep passing unchanged.
- **Coverage expectation:** Unknown project threshold. The new code path must be exercised by the regression test.

## Boundaries

**Always:**
- Add a regression test reproducing the MCVE.
- Keep the public signature of `to_unstacked_dataset` (and `to_stacked_array`) unchanged.
- Run the relevant existing test module(s) before considering the change done.
- Add a changelog entry if the project keeps one (location unknown).

**Ask first:**
- Changing the output structure of `to_stacked_array`, such as the `MultiIndex` levels or coordinate names.
- Using `compat='override'` or otherwise loosening merge conflict checks.
- Changing behavior for existing multi-dimensional cases, including dropped or retained coordinates and attrs.
- Adding any new dependency.

**Never:**
- Remove or weaken existing tests to make the fix pass.
- Silently drop non-stacked coordinates that users rely on.
- Modify vendored or third-party code.

## Success Criteria

1. The MCVE runs without raising.
2. For the MCVE, `stacked.to_unstacked_dataset('y')` is equal to the original `data`. The strictness (`equals` vs `identical`) is set by Open Question 1.
3. The result has no residual coordinate named after the stacked dimension (`y`), as a scalar or otherwise.
4. Variable names (`a`, `b`), the sample dimension `x`, its coordinate values, and the data values are all preserved.
5. Roundtrips that already worked return the same results as before. This covers variables with extra dimensions and mixed 1-D/N-D datasets.
6. The new regression test fails before the change and passes after it. The full existing test suite for this area passes.

## Open Questions

1. Should the roundtrip be **`identical`** (including attrs and names) or just **`equals`** (values and coords)? What is the expected handling of `DataArray.name` and attrs?
2. Is the `MultiIndex` built by `to_stacked_array` correct and well-formed when there are no non-sample dimensions? Or is part of the fix expected on the stacking side?
3. Should `to_unstacked_dataset` accept stacked arrays whose `MultiIndex` has only the variable level, plus the case where extra levels exist but are all-NaN for some variables? Is the latter in scope?
4. What `level` argument behavior is expected in the single-dim case, given it defaults to `0`?
5. Which branch or version should the fix target, and does the project require a changelog entry?
6. What are the exact test, lint, and build commands, and where do the existing roundtrip tests live?