# Spec: Concatenate Datasets with Mismatched Variables in `xray.concat`

## Objective

Let users concatenate `xray.Dataset` objects that do not all contain the same variables. `xray.concat` should handle missing variables itself.

**Current pain:** Users must do one of two things before calling `concat`:
- create dummy variables filled with `NaN` in the datasets that lack them, or
- drop the mismatched variables entirely.

Several users (@raj-kesavan, @richardotis, and the issue author) have reported this.

**Desired behavior:** `concat` offers an option, and possibly a new default, that performs an outer join over variables. A variable missing from some input datasets appears in the result, filled with missing values (`NaN`) at the positions contributed by those datasets.

**Consistency goal:** Behave like `pd.concat`, which takes a relaxed outer-join approach when combining DataFrames with different columns.

**Users:** People who use xray to combine datasets that are heterogeneous in which variables they hold, such as runs or files where some variables were not recorded.

### User stories
- As a user, I can concatenate `ds1` (variables `a`, `b`) and `ds2` (variable `a` only) along a dimension. The result contains `a` and `b`, and `b` is missing-valued along the `ds2` segment. I do not need to construct dummy variables.
- As a user, I can still ask for the old strict behavior, or drop non-shared variables, when I want it.
- As a user, I can predict the result because the semantics mirror `pd.concat`'s outer join.

## Assumptions
1. "Missing" is represented as `NaN` for floating-point data, as suggested in the issue. Fill behavior for other dtypes is unresolved; see Open Questions.
2. The change applies to concatenating `Dataset` objects. Concatenating `DataArray` objects is out of scope unless it routes through the same code path.
3. The filled region of a missing variable has the shape the variable would have had in that dataset. That is the variable's dimensions from the datasets where it exists, with sizes from the dataset where it is missing, including the concat dimension.
4. A variable that exists in some datasets but lacks the concat dimension can be handled sensibly under the new option. The exact rule is an open question.
5. The current behavior when variables mismatch is to raise an error, or otherwise require manual alignment. This is inferred from the issue and not verified against the code.
6. The current `concat` signature, the parameters it already has, and its internal implementation are unknown. This spec does not assume any existing parameter names.
7. Matching variables are identified by name.

## Tech Stack
- Library: `xray` (Python). Version is unknown.
- Related dependency referenced for semantics: `pandas` (`pd.concat`). Version is unknown.
- NumPy, for missing-value and dtype-promotion semantics. This is assumed, because xray is NumPy-based.

## Commands
Unknown, because the repository is not visible. The following are all to be confirmed:
- Build: unknown
- Test: unknown
- Lint: unknown

## Project Structure
Unknown. The locations of the `concat` implementation, its tests, and its documentation all need to be identified in the repository.

## Code Style
Unknown. Follow the existing conventions of the xray codebase, including docstring format for the new or changed parameter. No code snippet is available from the issue.

## Testing Strategy
The framework and test locations are unknown. Required test coverage is listed below.
- **Basic outer join:** two datasets where one lacks a data variable. The result contains the variable, with `NaN` in the missing segment and the original values elsewhere.
- **Multiple missing variables** across more than two datasets, in different orders.
- **Dtype handling:**
  - an integer variable missing from one dataset (promotion vs. error vs. other fill)
  - boolean, string/object, and datetime variables
- **Coordinates vs. data variables:** a missing non-index coordinate behaves as decided in Open Questions.
- **Variable without the concat dimension** present in only some datasets.
- **Strict mode:** the opt-out behavior raises on mismatch, if retained.
- **Inner/drop mode:** only variables shared by all datasets are kept, if offered.
- **Regression:** all existing `concat` tests pass unchanged, unless the default changes intentionally. Any intentional changes must be documented.
- **Metadata:** attributes and encoding of variables missing from some inputs are handled consistently, for example taken from the first dataset that has the variable.
- **Variable ordering** in the result is deterministic.

## Boundaries
- **Always:**
  - keep current behavior reachable via an explicit option
  - document the new option and its semantics in the `concat` docstring
  - add tests for every join mode offered
  - mirror `pd.concat` terminology where it applies
- **Ask first:**
  - changing the default behavior of `concat`, since this is backward-incompatible
  - adding a new public parameter name
  - silently promoting dtypes, such as int to float
  - extending the change to `DataArray` concat, `merge`, or alignment functions
- **Never:**
  - silently drop user data
  - change the semantics of existing parameters without approval
  - remove or weaken existing tests

## Success Criteria
- `xray.concat([ds1, ds2], dim=...)` succeeds when `ds1` and `ds2` have different sets of data variables. This holds either by default or with a documented option, per the decision on Open Question 1.
- In the result, every variable present in any input exists. Positions contributed by datasets lacking that variable are missing-valued (`NaN` for floats).
- Values from datasets that do contain the variable are unchanged.
- A strict mode exists that reproduces the prior behavior on mismatched variables.
- Behavior for non-float dtypes is defined, documented, and tested.
- The semantics are documented with explicit reference to the outer-join behavior of `pd.concat`.
- All existing tests pass, or intentional behavior changes are listed in release notes.

## Open Questions
1. **Default or opt-in?** Should outer-join become the default (the issue suggests "the default?"), or remain opt-in to preserve backward compatibility?
2. **API shape:** should this be a `join`-style parameter mirroring `pd.concat` (for example outer/inner), a boolean flag, or an extension of an existing parameter? Which parameters does `concat` already have?
3. **Inner join:** should an inner join (keep only shared variables) also be offered, in addition to outer and strict?
4. **Non-float dtypes:** how should missing values be filled for integers, booleans, strings, and datetimes? Options include promoting to float or object, using `NaT` for datetimes, raising, or accepting a user-supplied fill value.
5. **Fill value:** should users be able to specify a fill value other than `NaN`?
6. **Coordinates:** do the same rules apply to non-index coordinates as to data variables?
7. **Variables without the concat dimension:** if such a variable exists in only some datasets, should it be broadcast along the concat dimension and filled, or copied through as-is?
8. **Metadata:** when a variable exists in only some inputs, whose attributes and encoding should the result carry?
9. **Dimension mismatch:** how should dimension or index mismatches on non-concat dimensions interact with this feature? Is that the job of existing alignment logic, or out of scope?
10. **Scope:** should related functions, such as `DataArray` concatenation or other combining utilities, adopt the same behavior for consistency?