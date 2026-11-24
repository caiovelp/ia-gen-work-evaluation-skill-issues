## Summary

Running `makemigrations` and then `migrate` fails with `ValueError: Found wrong number (0) of constraints` when a single change does both of the following:

- converts a `ForeignKey` field to a `ManyToManyField`
- removes a `unique_together` that included that field

## Steps to reproduce

1. Create the models shown in "Code example – initial models". `Authors.project_data_set` is a `ForeignKey` to `ProjectDataSet`, and `Authors` has `unique_together = (('project_data_set', 'state', 'start_date'),)`.
2. Run `python3 manage.py makemigrations` and `python3 manage.py migrate` to create and apply the initial migration.
3. Change `Authors` to match "Code example – modified `Authors` model" in one edit:
   - change `project_data_set` from `ForeignKey` to `ManyToManyField(ProjectDataSet)`
   - remove the `unique_together` from `Authors.Meta`, because it can't include a many-to-many field
4. Run `python3 manage.py makemigrations`.
5. Run `python3 manage.py migrate`.

## Observed behavior

The migration fails with:

```
ValueError: Found wrong number (0) of constraints for app_authors(project_data_set, state, start_date)
```

The reporter says the error does not depend on the database. They deleted the database and got the same error.

The reporter cannot delete the earlier initial migrations because the database is in production.

Workaround used by the reporter:

1. Remove `unique_together` only, then run `makemigrations` and `migrate`.
2. Change the field from `ForeignKey` to `ManyToManyField`, then run `makemigrations` and `migrate` again.

This works, but it produces two migrations instead of one.

## Expected behavior

`makemigrations` and `migrate` should succeed for this change done in one step. That is, removing the `unique_together` and changing the field to `ManyToManyField` should produce one migration that applies without error.

## Stack trace / error output

```
ValueError: Found wrong number (0) of constraints for app_authors(project_data_set, state, start_date)
```

The original report gives no full traceback.

## Test case

Not provided in the original report. The reporter says a sample project was attached that shows the error when you run `makemigrations` and then `migrate`, but the attachment is not part of this report.

## Code example

**Initial models:**

```python
class Authors(models.Model):
    project_data_set = models.ForeignKey(
        ProjectDataSet,
        on_delete=models.PROTECT
    )
    state = models.IntegerField()
    start_date = models.DateField()

    class Meta:
        unique_together = (('project_data_set', 'state', 'start_date'),)


class DataSet(models.Model):
    name = models.TextField(max_length=50)


class Project(models.Model):
    data_sets = models.ManyToManyField(
        DataSet,
        through='ProjectDataSet',
    )
    name = models.TextField(max_length=50)


class ProjectDataSet(models.Model):
    """
    Cross table of data set and project
    """
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('data_set', 'project'),)
```

**Modified `Authors` model (the change that triggers the error):**

```python
class Authors(models.Model):
    project_data_set = models.ManyToManyField(
        ProjectDataSet,
    )
    state = models.IntegerField()
    start_date = models.DateField()
```

## Version and environment

Not provided in the original report. The commands are run with `python3 manage.py`. The reporter says the error happens regardless of the database, but does not name the database backend or the Django version.