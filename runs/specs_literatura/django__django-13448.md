## Summary

With Django 3.1, setting `"TEST": {"MIGRATE": False}` on a database makes `./manage.py test` crash during test database setup. While serializing the test database (`serialize_db_to_string`), Django queries the `django_admin_log` table, which does not exist. This raises `ProgrammingError: relation "django_admin_log" does not exist`, followed by `psycopg2.errors.InvalidCursorName`. Removing the `"TEST": {"MIGRATE": False}` setting lets the tests run normally.

## Steps to reproduce

1. Use a Django 3.1 project with a PostgreSQL database (psycopg2) and `django.contrib.admin` in use. `django_admin_log` appears in the traceback.
2. In the database configuration, add the test setting `"TEST": {"MIGRATE": False}`.
3. Run `./manage.py test`.

Note from the reporter: the project was upgraded from Django 1.4 through to 3.0 and is now being upgraded to 3.1, so legacy leftovers in the project might contribute to triggering the issue.

## Observed behavior

The test run crashes right away in `setup_databases` → `create_test_db` → `serialize_db_to_string`. Serialization queries `django_admin_log`, which does not exist in the test database, so the query raises `django.db.utils.ProgrammingError`. While handling that error, closing the cursor raises `psycopg2.errors.InvalidCursorName`. No tests run.

If the `"TEST": {"MIGRATE": False}` line is removed, the tests run normally.

## Expected behavior

With `"TEST": {"MIGRATE": False}` (new in Django 3.1), the test database should be set up without running migrations, and the test suite should run without crashing.

## Stack trace / error output

```
Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
    return self.cursor.execute(sql, params)
psycopg2.errors.UndefinedTable: relation "django_admin_log" does not exist
LINE 1: ...n_flag", "django_admin_log"."change_message" FROM "django_ad...
                                                             ^

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/django/db/models/sql/compiler.py", line 1156, in execute_sql
    cursor.execute(sql, params)
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 66, in execute
    return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 75, in _execute_with_wrappers
    return executor(sql, params, many, context)
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
    return self.cursor.execute(sql, params)
  File "/usr/local/lib/python3.6/site-packages/django/db/utils.py", line 90, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/utils.py", line 84, in _execute
    return self.cursor.execute(sql, params)
django.db.utils.ProgrammingError: relation "django_admin_log" does not exist
LINE 1: ...n_flag", "django_admin_log"."change_message" FROM "django_ad...
                                                             ^

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "./manage.py", line 15, in <module>
    main()
  File "./manage.py", line 11, in main
    execute_from_command_line(sys.argv)
  File "/usr/local/lib/python3.6/site-packages/django/core/management/__init__.py", line 401, in execute_from_command_line
    utility.execute()
  File "/usr/local/lib/python3.6/site-packages/django/core/management/__init__.py", line 395, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/usr/local/lib/python3.6/site-packages/django/core/management/commands/test.py", line 23, in run_from_argv
    super().run_from_argv(argv)
  File "/usr/local/lib/python3.6/site-packages/django/core/management/base.py", line 330, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/usr/local/lib/python3.6/site-packages/django/core/management/base.py", line 371, in execute
    output = self.handle(*args, **options)
  File "/usr/local/lib/python3.6/site-packages/django/core/management/commands/test.py", line 53, in handle
    failures = test_runner.run_tests(test_labels)
  File "/usr/local/lib/python3.6/site-packages/django/test/runner.py", line 695, in run_tests
    old_config = self.setup_databases(aliases=databases)
  File "/usr/local/lib/python3.6/site-packages/django/test/runner.py", line 616, in setup_databases
    self.parallel, **kwargs
  File "/usr/local/lib/python3.6/site-packages/django/test/utils.py", line 174, in setup_databases
    serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 78, in create_test_db
    self.connection._test_serialized_contents = self.serialize_db_to_string()
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 121, in serialize_db_to_string
    serializers.serialize("json", get_objects(), indent=None, stream=out)
  File "/usr/local/lib/python3.6/site-packages/django/core/serializers/__init__.py", line 128, in serialize
    s.serialize(queryset, **options)
  File "/usr/local/lib/python3.6/site-packages/django/core/serializers/base.py", line 90, in serialize
    for count, obj in enumerate(queryset, start=1):
  File "/usr/local/lib/python3.6/site-packages/django/db/backends/base/creation.py", line 118, in get_objects
    yield from queryset.iterator()
  File "/usr/local/lib/python3.6/site-packages/django/db/models/query.py", line 360, in _iterator
    yield from self._iterable_class(self, chunked_fetch=use_chunked_fetch, chunk_size=chunk_size)
  File "/usr/local/lib/python3.6/site-packages/django/db/models/query.py", line 53, in __iter__
    results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
  File "/usr/local/lib/python3.6/site-packages/django/db/models/sql/compiler.py", line 1159, in execute_sql
    cursor.close()
psycopg2.errors.InvalidCursorName: cursor "_django_curs_139860821038912_sync_1" does not exist
```

## Test case

Not provided in the original report.

## Code example

The setting that triggers the crash. The report gives only this fragment, not the full `DATABASES` configuration:

```python
"TEST": {"MIGRATE": False}
```

Command used:

```
./manage.py test
```

## Version and environment

- Django 3.1 (upgrading from Django 3.0; the project was originally upgraded from Django 1.4 through to 3.0)
- Python 3.6 (from the traceback paths `/usr/local/lib/python3.6/site-packages/`)
- PostgreSQL via psycopg2 (from the `psycopg2.errors` exceptions in the traceback)
- OS and exact PostgreSQL/psycopg2 versions: Not provided in the original report.