## Summary
After upgrading to Django 2.2, system checks raise `models.E028` when models in different apps use the same `db_table` name, even though each app uses its own database. The same setup worked in Django 2.0.

## Steps to reproduce
1. Create a project with a `base` app whose models use a central database.
2. Create one or more other apps (e.g. `app2`) whose models use their own separate databases.
3. In `base` and `app2`, define models (both named `ModelName` in the report) that use the same table name (`db_table = 'table_name'`).
4. Run the project under Django 2.2, so that system checks run.

## Observed behavior
Django 2.2 reports error `models.E028` and rejects two models in different apps that share a table name, even though they are stored in different databases. The reporter rolled back to Django 2.0.

## Expected behavior
Models in different apps that point to different databases should be allowed to share a table name, as in Django 2.0. The reporter asks whether the new error is intended behavior.

## Stack trace / error output
```
table_name: (models.E028) db_table 'table_name' is used by multiple models: base.ModelName, app2.ModelName.
```

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- Fails with: Django 2.2
- Works with: Django 2.0 (the reporter rolled back to this version)
- Setup: multiple databases. A `base` app uses a central database, and the other apps use their own databases.
- Python version, database backends and OS: Not provided in the original report.