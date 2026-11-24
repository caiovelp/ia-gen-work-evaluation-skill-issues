## Summary

On a model with a self-referencing foreign key and a default `Meta.ordering`, ordering a related queryset by the relation's `_id` field (`order_by("record__root_id")`) produces incorrect SQL:

- The model's default ordering (`"-id"`) is applied instead of the requested ordering, so the sort direction comes out inverted.
- An unnecessary extra `LEFT OUTER JOIN` is added.

`order_by("record__root")` produces the same incorrect SQL. `order_by("record__root__id")` produces correct SQL. The problem does not occur when `root` points to a third, different model.

## Steps to reproduce

1. Define these models in an app. The SQL output shows the app label `orion`.
   ```python
   class OneModel(models.Model):
       class Meta:
           ordering = ("-id",)
       id = models.BigAutoField(primary_key=True)
       root = models.ForeignKey("OneModel", on_delete=models.CASCADE, null=True)
       oneval = models.BigIntegerField(null=True)

   class TwoModel(models.Model):
       id = models.BigAutoField(primary_key=True)
       record = models.ForeignKey(OneModel, on_delete=models.CASCADE)
       twoval = models.BigIntegerField(null=True)
   ```
2. Build a queryset that orders by the self-referencing FK's `_id` field through a relation:
   ```python
   qs = TwoModel.objects.filter(record__oneval__in=[1, 2, 3])
   qs = qs.order_by("record__root_id")
   print(qs.query)
   ```
3. Look at the generated SQL.
4. Repeat with `order_by("record__root")` and with `order_by("-record__root_id")`.
5. For comparison, repeat with `order_by("record__root__id")`.

## Observed behavior

**`order_by("record__root_id")`**

- The query sorts `DESC` even though ascending order was requested. The direction appears to come from `OneModel.Meta.ordering = ("-id",)`.
- The query has two joins: an `INNER JOIN` to `orion_onemodel` and an unnecessary `LEFT OUTER JOIN` to `orion_onemodel` aliased as `T3`.
- It orders by `T3."id"` instead of `"orion_onemodel"."root_id"`.

**`order_by("record__root")`**

- Produces exactly the same SQL as `order_by("record__root_id")`.

**`order_by("-record__root_id")`**

- Produces the same two-join query but with an `ASC` sort.
- The requested descending order is inverted relative to the model's default ordering. The reporter notes this inversion does not happen in a simple (non-self-referencing) case.

**Cases that work**

- `order_by("record__root__id")` produces the expected SQL: a single `INNER JOIN` and `ORDER BY "orion_onemodel"."root_id" ASC`.
- A foreign key from `root` to a third model does not show the problem.

## Expected behavior

The explicit `order_by()` should take precedence over the related model's default `Meta.ordering`:

- `order_by("record__root_id")` should sort ascending.
- `order_by("-record__root_id")` should sort descending.
- Neither should add the extra self-join.
- Both should behave like `order_by("record__root__id")`: a single `INNER JOIN` and `ORDER BY "orion_onemodel"."root_id"` in the requested direction.

## Stack trace / error output

No exception is raised. The generated SQL, as given in the original report, is below.

**`order_by("record__root_id")` (incorrect; `order_by("record__root")` gives the same SQL):**
```sql
SELECT "orion_twomodel"."id", "orion_twomodel"."record_id", "orion_twomodel"."twoval" FROM "orion_twomodel" INNER JOIN "orion_onemodel" ON ("orion_twomodel"."record_id" = "orion_onemodel"."id") LEFT OUTER JOIN "orion_onemodel" T3 ON ("orion_onemodel"."root_id" = T3."id") WHERE "orion_onemodel"."oneval" IN (1, 2, 3) ORDER BY T3."id" DESC
```

**`order_by("-record__root_id")` (incorrect):**
```sql
SELECT "orion_twomodel"."id", "orion_twomodel"."record_id", "orion_twomodel"."twoval" FROM "orion_twomodel" INNER JOIN "orion_onemodel" ON ("orion_twomodel"."record_id" = "orion_onemodel"."id") LEFT OUTER JOIN "orion_onemodel" T3 ON ("orion_onemodel"."root_id" = T3."id") WHERE "orion_onemodel"."oneval" IN (1, 2, 3) ORDER BY T3."id" ASC
```

**`order_by("record__root__id")` (correct):**
```sql
SELECT "orion_twomodel"."id", "orion_twomodel"."record_id", "orion_twomodel"."twoval" FROM "orion_twomodel" INNER JOIN "orion_onemodel" ON ("orion_twomodel"."record_id" = "orion_onemodel"."id") WHERE "orion_onemodel"."oneval" IN (1, 2, 3) ORDER BY "orion_onemodel"."root_id" ASC
```

**Workaround with `annotate(root_id=F("record__root_id")).order_by("root_id")` (correct):**
```sql
SELECT "orion_twomodel"."id", "orion_twomodel"."record_id", "orion_twomodel"."twoval" FROM "orion_twomodel" INNER JOIN "orion_onemodel" ON ("orion_twomodel"."record_id" = "orion_onemodel"."id") WHERE "orion_onemodel"."oneval" IN (1, 2, 3) ORDER BY "orion_onemodel"."zero_id" ASC
```
The column name `zero_id` is reproduced as written in the original report.

## Test case

This is a minimal check derived from the reported reproduction. It uses the models from "Steps to reproduce" and assumes the expected behavior described above.

```python
qs = TwoModel.objects.filter(record__oneval__in=[1, 2, 3])

# Expected: ordering by the _id attname matches ordering by root__id
# (single INNER JOIN, ORDER BY "orion_onemodel"."root_id" ASC).
assert str(qs.order_by("record__root_id").query) == str(qs.order_by("record__root__id").query)

# Expected: descending order is honored and not inverted by OneModel.Meta.ordering.
assert str(qs.order_by("-record__root_id").query) == str(qs.order_by("-record__root__id").query)
```

## Code example

Workaround from the report. It produces a single `INNER JOIN` with an `ASC` sort:

```python
from django.db.models import F

qs = TwoModel.objects.filter(record__oneval__in=[1, 2, 3])
qs = qs.annotate(root_id=F("record__root_id"))
qs = qs.order_by("root_id")
print(qs.query)
```

Using `order_by("record__root__id")` also gives correct SQL.

## Version and environment

- Django 2.2.10: issue first observed.
- Django 3.0.6: issue verified to still occur.
- Database backend, Python version and OS: Not provided in the original report.