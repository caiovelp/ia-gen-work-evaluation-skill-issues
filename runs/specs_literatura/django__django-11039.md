## Summary

`sqlmigrate` wraps its output in `BEGIN`/`COMMIT` even when the database does not support transactional DDL. The migration executor only adds the outer `BEGIN`/`COMMIT` if the migration is atomic **and** the schema editor can roll back DDL. The current `sqlmigrate` logic only considers `migration.atomic`, so its output does not match what the executor actually runs.

## Steps to reproduce

1. Use a database backend where `connection.features.can_rollback_ddl` is `False`. Alternatively, mock that feature to `False`.
2. Pick an atomic migration (`migration.atomic` is `True`).
3. Run `sqlmigrate` for that migration.
4. Inspect the generated SQL output.

## Observed behavior

The `sqlmigrate` output is wrapped in `BEGIN`/`COMMIT`. This happens even though the database cannot roll back DDL, because `sqlmigrate` only checks `migration.atomic`.

## Expected behavior

`sqlmigrate` should behave like the migration executor. It should only wrap the output in `BEGIN`/`COMMIT` when the migration is atomic **and** the database can roll back DDL (`connection.features.can_rollback_ddl` is `True`). When the database cannot roll back DDL, the output should not contain the outer `BEGIN`/`COMMIT`.

## Stack trace / error output

Not provided in the original report.

## Test case

The report suggests a test in `tests/migrations/test_commands.py`, based on an existing test for non-atomic migrations:

- Mock `connection.features.can_rollback_ddl` to `False`. Do not override `MIGRATION_MODULES` to point to a non-atomic migration.
- Run `sqlmigrate` on an atomic migration.
- Assert that the output is not wrapped in `BEGIN`/`COMMIT`.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report. The issue applies to any database backend where `connection.features.can_rollback_ddl` is `False`.