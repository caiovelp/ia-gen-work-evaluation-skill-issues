## Summary

`QuerySet.delete()` returns its result in an inconsistent format when zero objects are deleted. The per-model counter dictionary is empty for models with foreign keys, but contains the model label with a value of `0` for "simple" models without foreign keys.

## Steps to reproduce

1. Have a model that has foreign key relations (e.g. `my_app.File` / `my_app.FileAccess`).
2. Have a "simple" model without foreign keys (e.g. `my_app.BlockLibrary`).
3. Call `.delete()` on a QuerySet of the model with foreign keys that matches zero objects, and note the return value.
4. Call `.delete()` on a QuerySet of the simple model that matches zero objects, and note the return value.
5. Compare the two return values.

## Observed behavior

`QuerySet.delete()` returns a tuple `(X, Y)`:
- `X`: the total number of deleted objects, including objects deleted through foreign keys.
- `Y`: a dictionary of deleted-object counters per model. The key is the model's `_meta.label` and the value is the number of deleted objects of that model.

Example with objects deleted: `<class 'tuple'>: (2, {'my_app.FileAccess': 1, 'my_app.File': 1})`

When zero objects are deleted in total, the result depends on the model:
- For models with foreign keys: `<class 'tuple'>: (0, {})`
- For "simple" models without foreign keys: `<class 'tuple'>: (0, {'my_app.BlockLibrary': 0})`

## Expected behavior

The two cases should return results in the same format. Either both return an empty dictionary, or both return a dictionary with model-label keys and zero values.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report. The only output examples given are the return values quoted under "Observed behavior".

## Version and environment

Not provided in the original report.