## Summary

A `RenameModel` operation on a model that already defines `db_table` should be a no-op, since the database table name does not change. Instead, it performs schema changes: on PostgreSQL it drops and recreates foreign key constraints, and on SQLite it recreates the table.

## Steps to reproduce

1. Have a model that explicitly defines `db_table`.
2. Create a `RenameModel` operation that renames this model, leaving `db_table` unchanged.
3. Apply the operation on PostgreSQL.
4. Apply the operation on SQLite.

## Observed behavior

- **PostgreSQL:** foreign key constraints are dropped and recreated.
- **SQLite:** the table is recreated. The reporter notes this is what normally happens for a table rename, but here the table name does not change.

## Expected behavior

When the model already has `db_table` defined, the `RenameModel` operation should be a no-op and make no database schema changes on any backend.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

- Affected database backends: PostgreSQL and SQLite.
- Software version: Not provided in the original report.