## Summary

`admin_views.test_multidb` fails with `sqlite3.OperationalError: database is locked` when the Django test suite runs against persistent (file-based) SQLite test databases, which is needed to use `--keepdb`. The failure happens in `setUpClass` of `admin_views.test_multidb.MultiDatabaseTests`, while `setUpTestData` creates a superuser. It does not happen when `TEST["NAME"]` is set only for the `default` database.

## Steps to reproduce

1. In a Django source checkout, edit `tests/test_sqlite.py` so that both the `default` and `other` databases use a persistent test database name (see the diff under "Code example"):
   - `default` → `'TEST': {'NAME': 'test_default.sqlite3'}`
   - `other` → `'TEST': {'NAME': 'test_other.sqlite3'}`
2. Run:
   ```
   tests/runtests.py admin_views.test_multidb -v 3 --keepdb --parallel 1
   ```
3. Database setup completes ("System check identified no issues (0 silenced)."). Then the test errors in `setUpClass`.

## Observed behavior

`setUpClass` of `admin_views.test_multidb.MultiDatabaseTests` errors with `django.db.utils.OperationalError: database is locked`. The error is raised in `setUpTestData` (`tests/admin_views/test_multidb.py`, line 40) at the call to `create_superuser(username='admin', password='something', email='test@test.org', ...)`.

The reporter says that "at least some test" fails this way. `admin_views.test_multidb` is the example given.

When `TEST["NAME"]` is set only for `default` (and not for `other`), the problem does not occur.

## Expected behavior

The `admin_views.test_multidb` tests should run without a "database is locked" error when persistent SQLite test databases are configured for both `default` and `other`, so that `--keepdb` can be used.

## Stack trace / error output

Relevant test runner output (paths abbreviated by the reporter with `…`):

```
Operations to perform:
 Synchronize unmigrated apps: admin_views, auth, contenttypes, messages, sessions, staticfiles
 Apply all migrations: admin, sites
Running pre-migrate handlers for application contenttypes
Running pre-migrate handlers for application auth
Running pre-migrate handlers for application sites
Running pre-migrate handlers for application sessions
Running pre-migrate handlers for application admin
Running pre-migrate handlers for application admin_views
Synchronizing apps without migrations:
 Creating tables...
	Running deferred SQL...
Running migrations:
 No migrations to apply.
Running post-migrate handlers for application contenttypes
Running post-migrate handlers for application auth
Running post-migrate handlers for application sites
Running post-migrate handlers for application sessions
Running post-migrate handlers for application admin
Running post-migrate handlers for application admin_views
System check identified no issues (0 silenced).
ERROR
======================================================================
ERROR: setUpClass (admin_views.test_multidb.MultiDatabaseTests)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/sqlite3/base.py", line 391, in execute
	return Database.Cursor.execute(self, query, params)
sqlite3.OperationalError: database is locked

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
 File "…/Vcs/django/django/test/testcases.py", line 1137, in setUpClass
	cls.setUpTestData()
 File "…/Vcs/django/tests/admin_views/test_multidb.py", line 40, in setUpTestData
	username='admin', password='something', email='test@test.org',
 File "…/Vcs/django/django/contrib/auth/models.py", line 158, in create_superuser
	return self._create_user(username, email, password, **extra_fields)
 File "…/Vcs/django/django/contrib/auth/models.py", line 141, in _create_user
	user.save(using=self._db)
 File "…/Vcs/django/django/contrib/auth/base_user.py", line 66, in save
	super().save(*args, **kwargs)
 File "…/Vcs/django/django/db/models/base.py", line 741, in save
	force_update=force_update, update_fields=update_fields)
 File "…/Vcs/django/django/db/models/base.py", line 779, in save_base
	force_update, using, update_fields,
 File "…/Vcs/django/django/db/models/base.py", line 870, in _save_table
	result = self._do_insert(cls._base_manager, using, fields, update_pk, raw)
 File "…/Vcs/django/django/db/models/base.py", line 908, in _do_insert
	using=using, raw=raw)
 File "…/Vcs/django/django/db/models/manager.py", line 82, in manager_method
	return getattr(self.get_queryset(), name)(*args, **kwargs)
 File "…/Vcs/django/django/db/models/query.py", line 1175, in _insert
	return query.get_compiler(using=using).execute_sql(return_id)
 File "…/Vcs/django/django/db/models/sql/compiler.py", line 1321, in execute_sql
	cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/utils.py", line 67, in execute
	return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
 File "…/Vcs/django/django/db/backends/utils.py", line 76, in _execute_with_wrappers
	return executor(sql, params, many, context)
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/utils.py", line 89, in __exit__
	raise dj_exc_value.with_traceback(traceback) from exc_value
 File "…/Vcs/django/django/db/backends/utils.py", line 84, in _execute
	return self.cursor.execute(sql, params)
 File "…/Vcs/django/django/db/backends/sqlite3/base.py", line 391, in execute
	return Database.Cursor.execute(self, query, params)
django.db.utils.OperationalError: database is locked
```

## Test case

No new test case was provided. The existing test `admin_views.test_multidb.MultiDatabaseTests` reproduces the failure when run with the settings change below:

```
tests/runtests.py admin_views.test_multidb -v 3 --keepdb --parallel 1
```

## Code example

Settings change applied to `tests/test_sqlite.py` to enable persistent SQLite test databases:

```diff
diff --git i/tests/test_sqlite.py w/tests/test_sqlite.py
index f1b65f7d01..9ce4e32e14 100644
--- i/tests/test_sqlite.py
+++ w/tests/test_sqlite.py
@@ -15,9 +15,15 @@
 DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
+        'TEST': {
+            'NAME': 'test_default.sqlite3'
+        },
     },
     'other': {
         'ENGINE': 'django.db.backends.sqlite3',
+        'TEST': {
+            'NAME': 'test_other.sqlite3'
+        },
     }
 }
```

## Version and environment

- Django: run from a source checkout (`…/Vcs/django`). The exact version or commit is not provided in the original report.
- Database backend: `django.db.backends.sqlite3`, with persistent test databases for both `default` and `other`.
- Test runner options: `--keepdb --parallel 1 -v 3`.
- Python version, SQLite version and OS: Not provided in the original report.