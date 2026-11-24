## Summary
On Django 1.11.10, a migration that removes an `index_together` crashes with a `ValueError` when a `unique_together` exists on the same fields. Removing the index finds two constraints on those fields (the `_uniq` one and the `_idx` one) instead of one, so the migration cannot proceed.

The reporter found this while moving an index declaration from `index_together` to the `Options.indexes` feature introduced in Django 1.11. They were not trying to remove the index from the database, only to change how it is declared in code.

## Steps to reproduce
1. Create a model with two fields.
2. Add the same two fields to both `unique_together` and `index_together` in the model's `Meta`.
3. Create and apply the migration.
4. Remove the `index_together` declaration from the model. In the reporter's case, the index was being moved to `Options.indexes`.
5. Create and apply the migration for this change.

## Observed behavior
The migration fails in `_delete_composed_index()` with `ValueError: Found wrong number (2) of constraints for ...`. The lookup finds two constraints on the fields: the unique constraint (`_uniq`) and the index (`_idx`). The reporter found no way around this failure.

Also, moving an index declaration from `index_together` to `Options.indexes` results in the index being deleted and re-created, rather than being treated as the same index.

## Expected behavior
The reporter describes two separate expectations:
1. Deleting an `index_together` should work when a `unique_together` exists on the same fields. Either the index can be deleted on its own, or the deletion is handled consistently with `unique_together` (possibly on the migrations side).
2. Moving an index declaration (e.g., from `index_together` to `Options.indexes`) should not cause the index to be re-created.

## Stack trace / error output
Only the following is given in the original report (the full traceback is not included, and the message is cut off as shown):
```
django/db/backends/base/schema.py, line 378, in _delete_composed_index()
ValueError: Found wrong number (2) of constraints for
```

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- Django 1.11.10
- Database backend, Python version and OS: Not provided in the original report.