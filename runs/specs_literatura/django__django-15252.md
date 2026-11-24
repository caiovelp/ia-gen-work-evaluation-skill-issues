## Summary

In a multi-database setup, `MigrationRecorder` ignores the database router's `allow_migrate` rules. When `migrate` runs against a connection where the router forbids migrations, `MigrationRecorder.ensure_schema()` still creates the migrations-tracking table there.

## Steps to reproduce

1. Configure a project with multiple database connections:
   - `default`: the Django project's own database.
   - Several other connections to external databases, used only for reading information through models with `managed = False`.
2. Configure a database router whose `allow_migrate` returns `True` only for `default` (see **Code example**).
3. Run the functional test suite so that test databases are created for each connection.
   - The `migrate` command runs against each connection during test database creation. The reporter refers to `django/test/runner.py`, `setup_databases` (around line 300), which calls `django/db/backends/creation.py`, `create_test_db` (around line 377).
4. Observe that the migrations table is created on the non-`default` connections.

## Observed behavior

When `migrate` runs against each connection:

1. It tries to apply the project's migrations and record each one as applied. `django/db/migrations/executor.py`, `apply_migration`, makes several calls to `self.recorder.record_applied`.
2. `record_applied` first calls `self.ensure_schema()` (`django/db/migrations/recorder.py`, `record_applied`, around line 66).
3. `ensure_schema` checks whether the table for the `Migration` model exists in the connection. If it does not, it creates the table.

As a result, the migrations table is created on every connection, including those where the router's `allow_migrate` returns `False`.

The reporter suspects that other `MigrationRecorder` methods, specifically `applied_migrations` and `record_unapplied`, have similar issues. This was not separately confirmed in the report.

## Expected behavior

`MigrationRecorder` should respect the router's `allow_migrate` rules. With the router below, the migrations table should be created only on the `default` connection. Django should never create tables on any other connection.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Router used by the reporter:

```python
class Router(object):
    def allow_migrate(self, db, model):
        if db == 'default':
            return True
        return False
```

## Version and environment

Not provided in the original report. The Django version is not stated. The line numbers referenced above (`runner.py` ~300, `creation.py` ~377, `recorder.py` ~66) are approximate and come from the reporter's copy of Django. The setup is multi-database, with additional connections to external databases accessed through unmanaged models (`managed = False`).