# Spec: SQLite Table Remake With Expression-Based UniqueConstraint

## Objective

**Problem.** On Django 4.0a1 with the SQLite backend, running `AlterField` on a model with an expression-based `UniqueConstraint` (for example `UniqueConstraint(F('name'), F('value'), name='unique_name_value')`) crashes during `migrate` with:

```
django.db.utils.OperationalError: the "." operator prohibited in index expressions
```

According to the traceback, the failure happens in `django/db/backends/sqlite3/schema.py` → `_alter_field` → `_remake_table` → `self.execute(sql)`. SQLite cannot `ALTER` most column properties, so Django rebuilds the table. While it re-creates the constraint's index on the rebuilt table, the generated index SQL seems to contain table-qualified column references (e.g. `"myapp_tag"."name"`). SQLite does not allow these inside index expressions.

**Who is affected.** Django users on SQLite who declare `UniqueConstraint` with positional expressions (new in Django 4.0) and then run any migration that makes the SQLite schema editor remake the table.

**What success looks like.** The reported migration sequence (CreateModel → AddConstraint with `F()` expressions → AlterField on `value`) applies cleanly on SQLite. Afterwards the unique constraint/index still exists and is still enforced on the rebuilt table.

**Acceptance criteria (user-level):**
- Given the `Tag` model and the two migrations in the issue, `manage.py migrate` succeeds on SQLite.
- After migrating, inserting two `Tag` rows with the same `(name, value)` raises an `IntegrityError`.
- Other operations that trigger `_remake_table` also succeed when the model has an expression-based unique constraint: alter field, add field, remove field (including a field the constraint does not reference), and rename field.

## Assumptions

1. The root cause is that expression column references in index/constraint SQL are rendered with a table alias/qualifier. SQLite rejects these in `CREATE INDEX` expressions. This is inferred from the error message and is not yet confirmed against source code.
2. The bug only affects expression-based constraints (`UniqueConstraint(*expressions, ...)`). Field-based constraints (`UniqueConstraint(fields=[...])`) are not affected. Not verified.
3. The crash happens when the index is re-created during `_remake_table`. The initial `AddConstraint` succeeded in the report, which suggests that path generates valid SQL, possibly through a different code path.
4. The table name used during the remake (a temporary "new" table, then a rename) may be involved in the qualifier. Not verified.
5. The fix belongs in Django core (schema editor / expression compilation for indexes), not in user code or migrations.
6. Other backends (PostgreSQL, MySQL, Oracle) are out of scope, except that they must not regress.
7. This is a release blocker for the 4.0 line, since expression-based `UniqueConstraint` is a new 4.0 feature. Severity is assumed.

## Tech Stack

- Django 4.0a1, as reported. The target branch is unknown.
- SQLite backend (`django.db.backends.sqlite3`). The SQLite library version is unknown.
- Python version: unknown. The reporter is on Windows (`D:\...\.venv`).

## Commands

Unknown. The repository is not visible, so no build, test or lint commands can be stated with confidence.

- Build: unknown
- Test: unknown (the test runner invocation and settings module for SQLite are not visible)
- Lint: unknown
- Reproduce: `manage.py migrate` in a project containing the model and migrations from the issue (taken from the issue itself)

## Project Structure

Only these paths are known, from the traceback:

```
django/db/backends/sqlite3/schema.py   → SQLite schema editor (alter_field, _alter_field, _remake_table)
django/db/backends/base/schema.py      → Base schema editor (alter_field, execute)
django/db/backends/sqlite3/base.py     → SQLite cursor wrapper
django/db/migrations/operations/fields.py → AlterField.database_forwards
```

These locations are unknown:
- where constraint/index SQL is generated for expressions
- where the schema/migration tests live

## Code Style

Unknown. Follow existing project conventions; no snippet is visible beyond the user's model and migrations.

## Testing Strategy

- **Level:** schema-editor / migration tests that run on the SQLite backend. The exact test modules and framework invocation are unknown.
- **Regression test (required):** create a model with an expression-based `UniqueConstraint`, add the constraint, then perform an operation that triggers a SQLite table remake (at minimum `AlterField`). Assert:
  - no exception is raised
  - the constraint is still present when introspected on the rebuilt table
  - the constraint is still enforced (a duplicate insert raises `IntegrityError`)
- **Additional coverage (desirable):** the same checks for add field, remove field and rename field on SQLite, with expression-based unique constraints.
- **Cross-backend:** existing constraint/index tests must keep passing on other backends. The CI configuration is unknown.
- **Coverage target:** unknown.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep generated SQL valid on all supported backends.
  - Preserve the semantics of the constraint across the table remake.
- **Ask first:**
  - Changing the public API of `UniqueConstraint`, `Index` or expression compilation.
  - Changing SQL generated for non-SQLite backends.
  - Changing migration autodetector or serializer output.
- **Never:**
  - Silently drop the constraint during a remake to avoid the error.
  - Require users to rewrite their migrations as the fix.
  - Remove or skip existing failing tests without approval.

## Success Criteria

1. The exact reproduction from the issue (both migrations, SQLite) applies without error.
2. After the migration, the `unique_name_value` constraint exists on the `Tag` table, as shown by introspection.
3. After the migration, inserting a duplicate `(name, value)` raises `IntegrityError`.
4. `_remake_table`-triggering operations (alter, add, remove, rename field) succeed on SQLite for models with expression-based unique constraints.
5. The generated `CREATE UNIQUE INDEX` SQL for expression constraints on SQLite contains no table-qualified column references.
6. No regressions in existing schema, migration or constraint test suites on any backend.

## Open Questions

1. Which branch and versions should get the fix: 4.0 release branch, main, or both?
2. Does the same failure occur for expression-based `Index` (`Meta.indexes` with expressions), not only `UniqueConstraint`? Should that be in scope?
3. Does the bug also affect conditional (`condition=`) or `include=`/`opclasses` constraints during a remake on SQLite?
4. Is the qualifier introduced by the expression compiler for all backends? (Other backends tolerate it, so it may only surface on SQLite.) Or is it specific to the remake code path?
5. Why does the initial `AddConstraint` succeed while the remake fails? Do they use different SQL generation paths?
6. Which SQLite versions must be supported or tested?
7. What are the exact test commands, settings and test module locations for schema-editor tests in this repository?
8. If a remake renames or drops a column that the expression constraint references, what is the expected behavior? Should it update, drop or error?