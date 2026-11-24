## Summary
Allow `xray.concat` to handle Datasets with different variables (ignore/fill missing variables when concatenating)

## Description
Right now `xray.concat` only works smoothly on Datasets that have the same variables. When the Datasets differ, the user has to do one of two things:
- Manually create dummy variables filled with `NaN` in the Datasets that lack them.
- Drop the mismatched variables entirely.

Neither option is good. This request proposes that `concat` handle this case itself.

## Product version
Not provided in the original request.

## Rationale
- Several users (@raj-kesavan, @richardotis, and the author) have asked how to concatenate xray Datasets with different variables. This shows it is a recurring need.
- The current workarounds are awkward. Adding `NaN`-filled dummy variables is manual and clumsy. Dropping variables loses data.
- `pd.concat` takes a more relaxed approach to matching DataFrames with different variables (it does an outer join). Supporting this in `xray.concat` would make it more consistent with pandas.

## Use case or scenario
A user has several xray Datasets to concatenate, but some variables appear in only some of the Datasets. The user wants to concatenate them directly, without first adding `NaN`-filled placeholder variables or dropping the variables that don't match.

## Possible solution
Add an option to `xray.concat` that handles missing variables for the user, presumably by filling them with `NaN` where absent, similar to the outer-join behavior of `pd.concat`. The original request suggests this option could be the default behavior, though it phrases that as an open question ("the default?").