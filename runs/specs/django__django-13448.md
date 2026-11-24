# Spec: Test DB setup with `"TEST": {"MIGRATE": False}` must not crash

## Objective

Django 3.1 added the database setting `"TEST": {"MIGRATE": False}`, which lets a project skip migrations when building the test database. In the reported project, `./manage.py test` crashes during `setup_databases` when this setting is enabled. Removing the setting makes the tests run.

**Who is affected:** Developers on Django 3.1 who want faster test database setup by skipping migrations. The reporter's project was upgraded from Django 1.4 to 3.0 and is now moving to 3.1.

**Observed behaviour, from the traceback:**

1. `DiscoverRunner.run_tests` calls `setup_databases` (`django/test/runner.py`).
2. `setup_databases` calls `create_test_db`, passing `serialize=connection.settings_dict['TEST'].get('SERIALIZE', True)` (`django/test/utils.py`).
3. `create_test_db` calls `serialize_db_to_string()` (`django/db/backends/base/creation.py`, line 78).
4. `serialize_db_to_string` iterates over model querysets and queries `django_admin_log`.
5. PostgreSQL raises `relation "django_admin_log" does not exist`.
6. While that error is being handled, closing the server-side cursor fails with `psycopg2.errors.InvalidCursorName: cursor "_django_curs_..._sync_1" does not exist`.

**Interpretation, to be confirmed:** With `MIGRATE: False`, the test database contains no tables for at least some installed apps. Here, `django.contrib.admin`'s `LogEntry` table is missing. Serialization still runs and queries every model, so it fails on the first missing table.

**Expected behaviour:**
- Setting `"TEST": {"MIGRATE": False}` lets the test database be created without running migrations.
- `./manage.py test` then completes setup without errors.
- Tests that use the ORM can run against tables that reflect the current model state.

**Acceptance criteria:**
- AC1: With `"TEST": {"MIGRATE": False}` and default `SERIALIZE` (True), `setup_databases` completes without raising.
- AC2: With `MIGRATE: False`, the tables for installed apps' models exist in the test database, including contrib apps such as `admin`, `auth` and `contenttypes`. Tests can therefore query them.
- AC3: With `MIGRATE: False` and `SERIALIZE: True`, serialization of the test database succeeds. Behaviour that depends on serialized contents, such as `serialized_rollback`, keeps working.
- AC4: Behaviour with `MIGRATE: True` (the default) is unchanged.
- AC5: The secondary `InvalidCursorName` error no longer hides the primary error. This is a scope question; see Open Questions.

## Tech Stack

- Django 3.1.x. The exact patch version is unknown.
- Python 3.6, per the traceback paths.
- PostgreSQL via `psycopg2`. The server and driver versions are unknown.
- Other backends (SQLite, MySQL, Oracle) may be affected but have not been verified.

## Commands

- Reproduction in the reporter's project: `./manage.py test`, with `"TEST": {"MIGRATE": False}` in the `DATABASES` entry.
- Django's own test-suite command: unknown, not shown in the issue.
- Build and lint commands: unknown.

## Project Structure

Locations visible in the traceback, under `site-packages/django/`:

- `test/runner.py`: `DiscoverRunner.run_tests` and `setup_databases`
- `test/utils.py`: module-level `setup_databases`
- `db/backends/base/creation.py`: `create_test_db`, `serialize_db_to_string`
- `db/models/sql/compiler.py`: `execute_sql`, where the cursor close fails
- `core/management/commands/test.py`: the `test` command

The location of Django's own tests for this area is unknown.

## Code Style

Unknown. Follow the existing conventions of the Django codebase; no example is available in the issue.

## Testing Strategy

- **Regression test:** Create a test database with `TEST['MIGRATE'] = False` and serialization enabled. Assert that creation succeeds and that model tables exist. Cover at least one contrib app that has migrations, such as `admin.LogEntry`.
- **Control test:** Run with `MIGRATE: True` and confirm the behaviour is unchanged.
- **Backends:** Run against PostgreSQL, because the reported failure, including the cursor-close error, is PostgreSQL-specific. Also run on SQLite to check that the behaviour is backend-agnostic.
- Test framework, file locations and coverage requirements are unknown. Use Django's existing test-suite conventions.

## Boundaries

- **Always:**
  - Keep the default `MIGRATE: True` path behaviour identical.
  - Add a regression test that reproduces the crash before the fix.
  - Respect the `SERIALIZE` setting.
- **Ask first:**
  - Changing the public meaning of `TEST['MIGRATE']` or `TEST['SERIALIZE']`.
  - Changing the error handling in `SQLCompiler.execute_sql` (the cursor-close masking).
  - Backporting to the 3.1 maintenance branch.
- **Never:**
  - "Fix" the problem by silently disabling serialization when `MIGRATE` is False, unless this is approved as the intended semantics.
  - Swallow database errors during test setup.

## Success Criteria

- The reproduction (`"TEST": {"MIGRATE": False}` with `./manage.py test` on PostgreSQL) no longer crashes in `setup_databases`.
- AC1–AC4 are covered by automated tests that pass. AC5 is covered too if it is accepted into scope.
- The existing test-database creation tests still pass.
- The release notes or docs for `TEST['MIGRATE']` accurately describe what gets created when migrations are skipped.

## Assumptions

1. The crash is a Django bug, not legacy cruft in the reporter's project. The failing table belongs to `django.contrib.admin`, which is standard.
2. The intended semantics of `MIGRATE: False` are to skip migrations but still create tables from the current models, like `syncdb`. It is not meant to create no tables at all.
3. `SERIALIZE` defaults to True and the reporter did not change it.
4. The `InvalidCursorName` error is a side effect of the first failure inside a server-side (chunked) cursor on PostgreSQL. It is not an independent root cause.
5. The target is the Django 3.1 line, with a possible backport.

## Open Questions

1. Is Assumption 2 correct: should `MIGRATE: False` create tables for all apps from their models? The alternative is that users are expected to also set `SERIALIZE: False`, or to create the schema themselves.
2. Does the crash reproduce on a fresh 3.1 project with `django.contrib.admin` installed? This would rule out the reporter's legacy configuration, e.g. `MIGRATION_MODULES` or custom routers.
3. Should the `InvalidCursorName` error that masks the original `ProgrammingError` be fixed in this change (AC5), or tracked separately?
4. Which other backends need verification beyond PostgreSQL?
5. Which Django 3.1 patch version is affected, and should the fix be backported?
6. Should the documentation for `TEST['MIGRATE']` be clarified regardless of the fix?