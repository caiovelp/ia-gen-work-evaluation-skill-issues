## Summary
Squashing migrations that transition a model from `Meta.index_together` to `Meta.indexes` does not remove the `index_together` deprecation warnings. The reporter considers this a release blocker for 4.2: without it, the only way to get rid of the warnings is to rewrite migrations by hand.

## Steps to reproduce
The original report gives no exact steps. Based on its description:
1. Have a model whose migration history uses `Meta.index_together`.
2. Change the model to use `Meta.indexes` instead, and create the corresponding migration.
3. Squash the migrations that cover the `index_together` → `indexes` transition.
4. Run code that loads the squashed migrations.

## Observed behavior
The `index_together` deprecation warnings are still emitted after squashing. The only way to remove them is to rewrite the migrations manually.

## Expected behavior
Squashing migrations that include the `Meta.index_together` → `Meta.indexes` transition should produce squashed migrations that no longer trigger the `index_together` deprecation warnings.

## Stack trace / error output
Not provided in the original report. The exact deprecation warning text is not included.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- The reporter flags this as a release blocker for version 4.2. The project is presumably Django, given the `Meta.index_together` and `Meta.indexes` options.
- The report refers to an earlier comment for context, but that comment is not included.
- No other environment details are provided.