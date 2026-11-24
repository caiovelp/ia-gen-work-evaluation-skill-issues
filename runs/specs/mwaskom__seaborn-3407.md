# Spec: `pairplot` / `PairGrid` support for DataFrames with MultiIndex columns

## Assumptions

1. The bug is in seaborn's `axisgrid.py` (`PairGrid.map_diag`, called from `pairplot`), as the traceback shows. The exact seaborn and pandas versions are not given in the issue. The traceback lines (`axisgrid.py:2144`, `map_diag` at line 1490) suggest a recent 0.12.x-era release.
2. "MultiIndex DataFrame" means a DataFrame whose **columns** are a `pd.MultiIndex`. Each variable key is a tuple such as `("A", "1")`. A MultiIndex on the row index is out of scope.
3. A full tuple key is a valid, unambiguous column selector. `df[("A", "1")]` returns a Series in pandas.
4. The error message `"['1'] not in index"` means that `var` in `self.data[var]` reaches pandas as a list or array (for example, `['A', '1']`) rather than as a tuple. Pandas then treats it as a list of level-0 keys. **This is a hypothesis.** One possible cause is that the diagonal variables are stored in a NumPy array, which turns a sequence of tuples into a 2-D array. This has not been confirmed against the source.
5. The expected behaviour is that `sns.pairplot(df)` works on the MRE without the user flattening the columns. It should produce the same grid as the flattened workaround, except for axis label text.
6. Other `PairGrid` code paths (`map_offdiag`, `map_lower`, `map_upper`, `map`, the `hue` handling, and the `vars` / `x_vars` / `y_vars` parameters) may share the same tuple-key fragility. They are in scope only for the cases listed under Success Criteria.
7. The workaround in the issue (`"".join(column)`) is user-side. Seaborn should not silently rename or flatten the user's columns.

## Objective

Users who call `sns.pairplot(df)` (or build a `sns.PairGrid(df)` and call its map methods) on a DataFrame with MultiIndex columns currently get a `KeyError` from inside `PairGrid.map_diag`. The goal is to make seaborn treat each full column key (a tuple) as a single variable throughout the pair-grid pipeline, so that:

- the default `pairplot(df)` call in the MRE renders a 4×4 grid without error, and
- the plotted data on each axis is identical to the data in the flattened-column workaround.

**User:** a data analyst whose DataFrame has hierarchical column labels, for example from `pivot_table`, `groupby().agg()` with several functions, or `pd.concat(..., keys=...)`.

**User story:** As an analyst with a MultiIndex-column DataFrame, I can call `sns.pairplot(df)` directly without flattening my columns first.

## Tech Stack

- Python, seaborn (version affected: unknown; reported traceback matches `axisgrid.py` with `pairplot` → `PairGrid.map_diag`)
- pandas (version unknown; traceback goes through `MultiIndex._get_indexer_strict` / `_raise_if_missing`)
- NumPy, matplotlib
- Minimum supported versions of each dependency: unknown, see the repository's packaging metadata.

## Commands

Not visible from the issue. All are **unknown**:

- Install (dev): unknown
- Test: unknown (likely pytest, unconfirmed)
- Lint: unknown
- Build docs: unknown

## Project Structure

Only what the traceback reveals:

```
seaborn/axisgrid.py   → PairGrid, pairplot (map_diag is where the error is raised)
```

Location of the test suite and the test file for axisgrid: **unknown**.

## Code Style

Not visible from the issue. Follow the conventions in the existing `seaborn/axisgrid.py` and its test module. No code snippet is provided here, to avoid inventing style.

## Testing Strategy

- **Level:** unit and regression tests for `PairGrid` and `pairplot`, placed in the existing axisgrid test module (path unknown).
- **Fixture:** a DataFrame with 2-level MultiIndex columns, mirroring the MRE: `("A","1"), ("A","2"), ("B","1"), ("B","2")`, numeric. Use a fixed random seed.
- **What to assert:**
  - no exception is raised;
  - the grid has the expected axes shape;
  - the data plotted on each diagonal axis matches `df[col]` for the corresponding tuple key;
  - the data on each off-diagonal axis matches the corresponding `(x, y)` tuple pair.
- **Regression guard:** existing single-level-column tests must continue to pass unchanged.
- Coverage target: unknown, follow project norms.

## Boundaries

- **Always:**
  - Treat a column key as opaque, so that a tuple key is one variable.
  - Add a regression test reproducing the MRE.
  - Run the full axisgrid test suite before committing.
- **Ask first:**
  - Changing how axis labels are rendered for tuple keys (for example `"A-1"` versus `"('A', '1')"`).
  - Extending the fix to `FacetGrid`, `JointGrid`, or the objects interface.
  - Raising minimum pandas or NumPy versions.
- **Never:**
  - Mutate or flatten the user's DataFrame columns.
  - Change behaviour for single-level column DataFrames.
  - Remove or loosen existing tests.

## Success Criteria

1. Running the exact MRE from the issue completes without raising and returns a `PairGrid` whose axes array is 4×4.
2. Each diagonal histogram is built from `df[("A","1")]`, `df[("A","2")]`, `df[("B","1")]` and `df[("B","2")]` respectively, in column order.
3. Each off-diagonal scatter at row *i*, column *j* uses `y = df[vars[i]]` and `x = df[vars[j]]`, with tuple keys.
4. Behaviour is consistent across `diag_kind="hist"` and `diag_kind="kde"`, and across `kind="scatter"` and at least one other `kind` (for example `"kde"` or `"reg"`).
5. `corner=True` works with MultiIndex columns.
6. Passing tuple keys explicitly via `vars=[("A","1"), ("B","2")]`, and via `x_vars` / `y_vars`, selects exactly those columns.
7. *(Pending the open question)* `hue=("B","1")` with a categorical column under a tuple key works.
8. Axis labels for tuple-keyed variables are non-empty and identify the column. The exact format depends on the Open Questions.
9. All pre-existing `PairGrid` and `pairplot` tests still pass.

## Open Questions

1. **Root cause confirmation:** is `var` arriving at `self.data[var]` as an array or list because the variable list is stored as a NumPy array, which would convert a list of tuples into a 2-D array? Or is there another cause?
2. **Scope:** should the fix cover only `pairplot` / `PairGrid`, or also audit `FacetGrid` (`row` / `col` / `hue` with tuple keys) and `JointGrid` for the same issue?
3. **Hue with a tuple key:** is `hue=("B","1")` expected to work, and should the legend title render the tuple?
4. **Axis label format** for tuple keys: should it use the default `str(tuple)`, a joined form, or something configurable? Is there an existing seaborn convention?
5. **Deeper MultiIndex levels and mixed key types:** should non-string levels, such as integers, be explicitly supported and tested?
6. **Partial keys:** if a user passes a level-0 key like `vars=["A"]` that maps to several columns, should seaborn raise a clear error, or is that undefined behaviour?
7. **Version support:** what are the affected seaborn release and the minimum pandas version that must be supported? Some pandas versions may differ in how `df[array]` resolves on a MultiIndex.
8. **Release:** is a changelog or release-note entry required, and in which file? The path is unknown.