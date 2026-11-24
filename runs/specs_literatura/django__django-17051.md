## Summary
Allow `QuerySet.bulk_create()` to return primary keys (IDs) when `update_conflicts` is used.

## Description
At present, `bulk_create()` does not set primary keys on the returned objects when a conflict-handling flag is enabled (`ignore_conflicts` or `update_conflicts`). This behavior is documented for `bulk_create`.

The reporter accepts that `ignore_conflicts` is a special case. When a row is ignored, PostgreSQL may not return its ID (a Stack Overflow thread is referenced). That reason does not hold for `update_conflicts`.

Example:

```python
MyModel.objects.bulk_create([MyModel(...)], update_conflicts=True, update_fields=[...], unique_fields=[...])
```

This generates a query without a `RETURNING my_model.id` clause:

```sql
INSERT INTO "my_model" (...)
VALUES (...)
	ON CONFLICT(...) DO UPDATE ...
```

The reporter tested this manually on PostgreSQL. With `RETURNING my_model.id` added, the query is valid and returns the ID.

The reporter also found the place in the Django source where `returning_fields` is removed when conflict handling is enabled. The original request links to it but does not quote the code.

## Product version
Not provided in the original request.

## Rationale
Using `bulk_create` as a bulk upsert is much more useful if the IDs of the inserted or updated rows come back. With `update_conflicts`, every row is either inserted or updated, so the reason for dropping IDs under `ignore_conflicts` does not apply. PostgreSQL also accepts a `RETURNING` clause on such a query.

## Use case or scenario
A developer calls `bulk_create()` with `update_conflicts=True`, `update_fields` and `unique_fields` to perform a bulk upsert. Afterwards they need the primary keys of the affected objects. Right now those primary keys are not set.

## Possible solution
Handle the two conflict modes differently in the code that currently removes `returning_fields`. Keep `returning_fields`, and so the `RETURNING` clause, when `update_conflicts` is used. Keep dropping them for `ignore_conflicts`.