# Spec: MigrationRecorder Respects Database Router `allow_migrate` Rules

## Objective

Make Django's `MigrationRecorder` follow the configured database routers' `allow_migrate` rules. If the routers do not allow migrations on a connection, the recorder must not create the `django_migrations` table there.

**Who is affected:** projects with multiple databases where:

- one connection (e.g. `'default'`) holds the Django-managed schema, and
- other connections are read-only or externally owned sources (e.g. models with `managed = False`).

For these projects, Django must never create tables on the non-managed connections.

**Current behaviour (from the issue):**

1. The test runner calls `migrate` against every connection when it creates the test databases. The issue points to `setup_databases` in `django/test/runner.py`, which calls `create_test_db` in `django/db/backends/creation.py`.
2. `MigrationExecutor.apply_migration` (`django/db/migrations/executor.py`) calls `self.recorder.record_applied`.
3. `MigrationRecorder.record_applied` (`django/db/migrations/recorder.py`) calls `self.ensure_schema()` first.
4. `ensure_schema()` creates the `django_migrations` table if it is missing. It does not consult the routers.
5. As a result, the table gets created on connections where the router says `allow_migrate` is `False`.

The reporter suspects that `applied_migrations` and `record_unapplied` have the same problem.

**Desired behaviour:** on a connection where routers disallow migrating the recorder's `Migration` model:

- the recorder never creates its table;
- it never writes rows to it;
- it never reads from it in a way that requires the table to exist.

On allowed connections, behaviour is unchanged.

### User stories / acceptance criteria

- **US1.** Given a router whose `allow_migrate` returns `True` only for `'default'`, when `migrate` runs against a non-default connection (directly or via test database setup), then no `django_migrations` table is created on that connection.
- **US2.** Given the same router, when `migrate` runs against `'default'`, then `django_migrations` is created and migrations are recorded exactly as today.
- **US3.** Given no routers configured, or routers that return `None` for the recorder's model, behaviour is identical to today: the table is created and used on every connection that is migrated.
- **US4.** On a disallowed connection:
  - `record_applied` and `record_unapplied` complete without error and without touching the database;
  - `applied_migrations` reports no applied migrations without raising.

## Assumptions

1. The recorder is gated by the standard router check `allow_migrate(db, app_label, **hints)` (exposed as `router.allow_migrate` / `allow_migrate_model`). It is evaluated against the recorder's internal `Migration` model, the same way schema operations are gated today. The exact model/app_label used is an implementation detail to confirm in Plan.
2. The router in the issue uses the legacy signature `allow_migrate(self, db, model)`. We assume the fix targets the current router API, and the legacy signature is out of scope.
3. A router returning `None` means "no opinion". If all routers return `None`, migration is allowed (existing router-chain semantics).
4. Schema operations inside migrations (`CreateModel`, etc.) already consult `allow_migrate`. Only the recorder bypasses it, and only the recorder is in scope.
5. On a disallowed connection, "no applied migrations" is the correct answer for `applied_migrations`. It returns an empty result of the same type it returns today.
6. The fix lives in `django/db/migrations/recorder.py`. Changes to callers (executor, loader, `migrate` command, test runner) are only made if required. This needs confirming during Plan.
7. The behaviour must hold both for the test-runner path and for a direct `manage.py migrate --database=<alias>` invocation.

## Tech Stack

- Python / Django. Exact supported Python and Django versions are **unknown** from the issue.
- Components named in the issue:
  - `django/db/migrations/recorder.py`
  - `django/db/migrations/executor.py`
  - `django/test/runner.py`
  - `django/db/backends/creation.py`

## Commands

| Purpose | Command |
|---|---|
| Build | **Unknown** (not stated in the issue) |
| Test (full suite) | **Unknown** (not stated in the issue) |
| Test (targeted: migrations / multi-db) | **Unknown** (not stated in the issue) |
| Lint | **Unknown** (not stated in the issue) |

## Project Structure

Only the paths named in the issue are known:

```
django/db/migrations/recorder.py   → MigrationRecorder (ensure_schema, record_applied, record_unapplied, applied_migrations)
django/db/migrations/executor.py   → MigrationExecutor.apply_migration (calls recorder.record_applied)
django/test/runner.py              → setup_databases (runs migrate per connection for test DBs)
django/db/backends/creation.py     → create_test_db (invokes migrate)
```

The test location for this change is **unknown**. It should sit beside the existing migration-recorder and multi-db router tests.

## Code Style

Follow the existing conventions of the files above. No code snippet is available from the issue, and the conventions are **unknown** beyond "match surrounding code".

## Testing Strategy

- **Framework:** Django's own test suite (runner and invocation **unknown**).
- **Unit level (recorder).** Use a test router that disallows migrations on a secondary alias, then assert:
  - `ensure_schema()` does not create the table on the disallowed alias;
  - `record_applied()` and `record_unapplied()` are silent no-ops there;
  - `applied_migrations()` returns an empty result and does not raise when the table is absent.
- **Integration level (executor / migrate).** Run `migrate` against a disallowed alias with migrations present. Assert that:
  - the command succeeds;
  - `django_migrations` does not exist on that alias;
  - the allowed alias is recorded normally.
- **Regression.**
  - With no routers, every existing recorder and migrate test passes unchanged.
  - With a router returning `None`, the table is still created.
- **Test-DB setup path.** Test database creation with a router like the one in the issue must not create `django_migrations` on non-default test databases.
- **Coverage expectation:** every public recorder method (`ensure_schema`, `record_applied`, `record_unapplied`, `applied_migrations`, plus `flush` if it exists) has an allowed-case and a disallowed-case test.

## Boundaries

- **Always:**
  - consult the router chain before any DDL or DML the recorder issues;
  - preserve current behaviour when routing allows it or has no opinion;
  - add tests for both allowed and disallowed connections.
- **Ask first:**
  - changing the return type or semantics of `applied_migrations`;
  - changing the router API or `allow_migrate` hints;
  - modifying the `migrate` command, the loader, or test-runner behaviour beyond the recorder;
  - any change that affects `migrate --fake` / `--fake-initial` or `showmigrations` output.
- **Never:**
  - create the migrations table on a connection the routers disallow;
  - silently change behaviour for single-database projects;
  - remove or weaken existing migration tests.

## Success Criteria

1. With a router allowing migrations only on `'default'`, running `migrate` on any other alias leaves that database with **no** `django_migrations` table, and exits successfully.
2. With the same router, `'default'` gets `django_migrations` populated with every applied migration, identical to current behaviour.
3. On a disallowed alias:
   - `MigrationRecorder.record_applied` and `record_unapplied` execute no SQL;
   - `applied_migrations` returns an empty result without querying a nonexistent table.
4. Test database setup for a multi-db project with such a router creates no `django_migrations` table on non-default test databases.
5. With no routers configured, the full existing migrations test suite passes unchanged.
6. New tests cover the cases in criteria 1–4 and fail on the current code.

## Open Questions

1. **Router check.** Which `app_label` / model should the check use: the recorder's internal `Migration` model (`allow_migrate_model`), or `allow_migrate(db, 'migrations', model_name='migration')`? Routers that key on `app_label` will behave differently depending on the choice.
2. **Disallowed reads.** On a disallowed connection, should `applied_migrations` return empty, or should it still read an existing table if one is already present (e.g. created by an older Django)?
3. **Plan display.** On a disallowed connection, `migrate` will "apply" migrations whose operations are all skipped by the router, but it will record nothing. Every subsequent run will therefore re-plan them all. Is that acceptable, or should the executor or `migrate` short-circuit when the recorder is disallowed?
4. **Other commands.** Should `showmigrations`, `migrate --plan`, and `makemigrations` consistency checks adopt the same rule, or are they out of scope?
5. **`RunSQL` / `RunPython`.** Operations that rely on hints rather than a model may still run on disallowed connections. Is that out of scope for this issue?
6. **Version scope.** Which Django version(s) should receive the fix, and should the legacy `allow_migrate(db, model)` signature in the issue be considered at all?
7. **Release notes.** Is this classified as a bug fix (release-notes entry) or a behaviour change needing a deprecation path?