## Summary

Chaining `QuerySet.defer()` after `QuerySet.only()` does not remove the deferred field when it is the only field passed to `only()`. Instead of selecting only the primary key, the generated SQL selects **all** fields of the model. When `only()` is given more than one field, `defer()` works as expected.

## Steps to reproduce

1. Define a simple `Company` model with four fields: `id`, `name`, `trade_number` and `country`.
2. Evaluate the queryset `Company.objects.only("name").defer("name")` and inspect the generated SQL.
3. Evaluate the queryset `Company.objects.only("name").defer("name").defer("country")` and inspect the generated SQL.
4. For comparison, evaluate `Company.objects.only("name", "country").defer("name")` and inspect the generated SQL.

## Observed behavior

- `Company.objects.only("name").defer("name")` loads all fields:
  ```sql
  SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company"
  ```
- `Company.objects.only("name").defer("name").defer("country")` also loads all fields with the same query:
  ```sql
  SELECT "company"."id", "company"."name", "company"."trade_number", "company"."country" FROM "company"
  ```
- `Company.objects.only("name", "country").defer("name")` behaves correctly and loads only `id` and `country`:
  ```sql
  SELECT "company"."id", "company"."country" FROM "company"
  ```

## Expected behavior

For both `Company.objects.only("name").defer("name")` and `Company.objects.only("name").defer("name").defer("country")`, the generated SQL should select only the primary key:

```sql
SELECT "company"."id" FROM "company"
```

## Stack trace / error output

Not provided in the original report. No exception is raised. The problem is the incorrect SELECT clause shown above.

## Test case

The following cases and SQL come from the report, using a `Company` model with fields `id`, `name`, `trade_number` and `country`:

| QuerySet | Expected SQL | Actual SQL |
|---|---|---|
| `Company.objects.only("name").defer("name")` | `SELECT "company"."id" FROM "company"` | selects `id`, `name`, `trade_number`, `country` |
| `Company.objects.only("name").defer("name").defer("country")` | `SELECT "company"."id" FROM "company"` | selects `id`, `name`, `trade_number`, `country` |
| `Company.objects.only("name", "country").defer("name")` | `SELECT "company"."id", "company"."country" FROM "company"` | same as expected (works) |

## Code example

```python
# Unexpected: selects all fields
Company.objects.only("name").defer("name")
Company.objects.only("name").defer("name").defer("country")

# Works as expected: selects "id" and "country"
Company.objects.only("name", "country").defer("name")
```

## Version and environment

Not provided in the original report.