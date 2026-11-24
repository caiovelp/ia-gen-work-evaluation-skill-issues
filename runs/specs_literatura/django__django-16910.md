## Summary

On Django 4.2, combining `QuerySet.only()` with `select_related()` across a **reverse** `OneToOneField` relation does not restrict the columns selected from the related model. All fields of the related model still appear in the generated SQL. On Django 4.1.9, only the requested fields are selected, so this is a regression.

## Steps to reproduce

1. Define two models where `Secondary` has a `OneToOneField` to `Main` (with `primary_key=True` and `related_name='secondary'`). See **Code example** below. In the report, these models are in an app whose tables are prefixed `bugtest_`.
2. Build a queryset on `Main` that follows the reverse one-to-one relation with `select_related()` and restricts fields with `only()`:
   ```python
   Main.objects.select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')
   ```
3. Inspect the generated SQL.
4. Compare the result on Django 4.2.1 with the result on Django 4.1.9.

## Observed behavior

On Django 4.2.1, the query selects every column of `bugtest_secondary`, including `secondary_field_2` and `secondary_field_3`, which were not requested in `only()`:

```sql
SELECT "bugtest_main"."id", "bugtest_main"."main_field_1", "bugtest_secondary"."main_id", "bugtest_secondary"."secondary_field_1", "bugtest_secondary"."secondary_field_2", "bugtest_secondary"."secondary_field_3" FROM "bugtest_main" LEFT OUTER JOIN "bugtest_secondary" ON ("bugtest_main"."id" = "bugtest_secondary"."main_id")
```

## Expected behavior

Only the fields named in `only()` should be selected from the related model, along with the required key columns. This is what Django 4.1.9 generates:

```sql
SELECT "bugtest_main"."id", "bugtest_main"."main_field_1", "bugtest_secondary"."main_id", "bugtest_secondary"."secondary_field_1" FROM "bugtest_main" LEFT OUTER JOIN "bugtest_secondary" ON ("bugtest_main"."id" = "bugtest_secondary"."main_id")
```

## Stack trace / error output

Not provided in the original report. No exception is raised; the problem is the content of the generated SQL, shown above.

## Test case

The following minimal check is derived from the report's snippet and the expected SQL. It uses the models from **Code example**:

```python
qs = Main.objects.select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')
sql = str(qs.query)

assert 'secondary_field_1' in sql
assert 'secondary_field_2' not in sql   # fails on Django 4.2.1, passes on 4.1.9
assert 'secondary_field_3' not in sql   # fails on Django 4.2.1, passes on 4.1.9
```

## Code example

Models:

```python
class Main(models.Model):
    main_field_1 = models.CharField(blank=True, max_length=45)
    main_field_2 = models.CharField(blank=True, max_length=45)
    main_field_3 = models.CharField(blank=True, max_length=45)

class Secondary(models.Model):
    main = models.OneToOneField(Main, primary_key=True, related_name='secondary', on_delete=models.CASCADE)
    secondary_field_1 = models.CharField(blank=True, max_length=45)
    secondary_field_2 = models.CharField(blank=True, max_length=45)
    secondary_field_3 = models.CharField(blank=True, max_length=45)
```

Query:

```python
Main.objects.select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')
```

## Version and environment

- **Affected:** Django 4.2 (the generated SQL shown is from Django 4.2.1)
- **Working:** Django 4.1.9
- **Database backend, Python version, OS:** Not provided in the original report.