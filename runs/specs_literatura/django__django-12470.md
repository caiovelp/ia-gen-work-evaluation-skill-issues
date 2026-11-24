## Summary
When a parent model defines `Meta.ordering = ["-pk"]`, querying a child model that inherits from it (multi-table inheritance) produces a query ordered ascending (`ASC`) instead of descending (`DESC`).

## Steps to reproduce
1. Define the following models in an app named `myapp`:
   ```python
   from django.db import models

   class Parent(models.Model):
       class Meta:
           ordering = ["-pk"]

   class Child(Parent):
       pass
   ```
2. Build a queryset on the child model and print its SQL:
   ```python
   >>> print(Child.objects.all().query)
   ```
3. Inspect the `ORDER BY` clause of the generated SQL.

## Observed behavior
The generated query orders by the parent's primary key in ascending order:
```sql
SELECT "myapp_parent"."id", "myapp_child"."parent_ptr_id" FROM "myapp_child" INNER JOIN "myapp_parent" ON ("myapp_child"."parent_ptr_id" = "myapp_parent"."id") ORDER BY "myapp_parent"."id" ASC
```

## Expected behavior
The query should honor the inherited `ordering = ["-pk"]` and order descending, i.e. the `ORDER BY` clause should be `"myapp_parent"."id" DESC`.

## Stack trace / error output
Not provided in the original report. (No error is raised; the problem is the incorrect SQL shown under "Observed behavior".)

## Test case
A minimal test derived from the report's reproduction:
```python
# Models (in app "myapp")
from django.db import models

class Parent(models.Model):
    class Meta:
        ordering = ["-pk"]

class Child(Parent):
    pass
```
```python
# Check
sql = str(Child.objects.all().query)
# Expected: ORDER BY "myapp_parent"."id" DESC
# Observed: ORDER BY "myapp_parent"."id" ASC
assert sql.endswith('ORDER BY "myapp_parent"."id" DESC')
```

## Code example
```python
from django.db import models

class Parent(models.Model):
    class Meta:
        ordering = ["-pk"]

class Child(Parent):
    pass
```
```python
>>> print(Child.objects.all().query)
```

## Version and environment
Not provided in the original report. (The quoted identifiers in the SQL output suggest a database backend that uses double-quoted identifiers, but no Django version, Python version, or database backend is specified.)