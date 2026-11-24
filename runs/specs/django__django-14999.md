# Spec: RenameModel Is a Database No-Op When the Table Name Does Not Change

## Objective

A `RenameModel` migration operation on a model with an explicit `Meta.db_table` should not change the database schema when the effective table name is the same before and after the rename.

**Current (incorrect) behavior reported in the issue:**
- **PostgreSQL:** the operation drops and recreates the foreign key constraints that point to the model.
- **SQLite:** the operation rebuilds the table, as it would for a real table rename.

**Desired behavior:** the database is left untouched. The migration state still records the new model name, so the ORM, related fields and later migrations see the renamed model.

**Users:** developers who rename a model class for code clarity while keeping a fixed `db_table`. They expect the migration to be free and safe to run on production databases. Dropping and recreating constraints or rebuilding the table on a large table means locking, slow migrations and avoidable risk.

**User story:** As a developer, I rename `class Foo` to `class Bar` where `Meta.db_table = "legacy_foo"` stays the same. I want the generated `RenameModel` migration to run without issuing any schema-altering SQL.

## Assumptions

1. This is Django's migrations framework. `RenameModel` is the built-in migration operation and the schema editor is Django's backend schema editor.
2. "No-op" applies to the database operations only, in both directions (forwards and backwards). The state change (model renamed in the project state) must still happen.
3. The comparison uses the *effective* table name of the old and new model states (`_meta.db_table`), not whether `db_table` was written explicitly. If the effective names are equal, the operation is a database no-op.
4. When the effective table names differ, the current behavior (table rename, related field updates, M2M updates) stays exactly as it is today.
5. The fix should behave the same on every supported backend: PostgreSQL, SQLite, MySQL and Oracle. The issue only names PostgreSQL and SQLite.
6. Foreign key columns on related models are named after the field, not the target model, so with an unchanged table they need no change.
7. The autodetector already generates `RenameModel` for this case and does not need to change. Only the operation's database behavior is in scope.

## Tech Stack

- Python / Django. Exact versions are **unknown**; they are not stated in the issue.
- Backends involved: PostgreSQL and SQLite (reported). MySQL and Oracle are assumed to be affected as well.

## Commands

**Unknown.** The issue does not state the build, test or lint commands. To be filled in from the repository's contributing docs and test runner configuration. Tests must be runnable against at least SQLite and PostgreSQL.

## Project Structure

**Unknown.** The issue does not reference file paths. Expected areas, to be confirmed against the repository:
- Implementation of the `RenameModel` migration operation (model operations module)
- Migration operation tests (operations test suite)

## Code Style

**Unknown.** Follow the existing style of the migrations operations module and its tests. No snippet is available from the issue.

## Testing Strategy

Use the project's existing migration operation test suite. Framework and location are unknown and to be confirmed. Required test coverage:

1. **Forwards no-op**
   - Setup: rename a model whose old and new states share the same `db_table`, with at least one other model holding a FK to it.
   - Assert: zero schema queries are executed during `database_forwards`, for example with a query-count or captured-SQL assertion.
2. **Backwards no-op**
   - Same setup as test 1.
   - Assert: `database_backwards` executes zero schema queries.
3. **State still updated**
   - Assert: after `state_forwards`, the project state contains the new model name and not the old one.
   - Assert: related fields in the state point to the new model.
4. **Regression test for real renames**
   - Setup: a model *without* a fixed `db_table`, or with differing `db_table` values.
   - Assert: it is still renamed in the database, and FKs still work afterwards.
5. **Backend coverage**
   - Run on SQLite and PostgreSQL at minimum.
   - The test must catch the SQLite table rebuild and the PostgreSQL FK drop/recreate.

## Boundaries

- **Always:**
  - Keep `state_forwards` behavior unchanged.
  - Keep the existing behavior when table names differ.
  - Cover both forwards and backwards directions.
  - Add regression tests.
- **Ask first:**
  - Changing autodetector output.
  - Changing behavior for auto-created M2M through tables (see Open Questions).
  - Changing schema editor APIs used by other operations.
- **Never:**
  - Skip the state update.
  - Silently change behavior for renames where the table name actually changes.
  - Remove or weaken existing migration tests.

## Success Criteria

- [ ] A `RenameModel` whose old and new effective `db_table` are equal issues **no** schema SQL forwards on any supported backend. This means no FK constraint drop/recreate on PostgreSQL and no table rebuild on SQLite.
- [ ] The same holds for the backwards direction.
- [ ] After the migration, the project state reflects the new model name, and models related to it resolve correctly.
- [ ] A `RenameModel` where the table name changes behaves exactly as before, and all existing tests pass.
- [ ] New tests fail on the current code and pass after the change, on at least SQLite and PostgreSQL.

## Open Questions

1. **Auto-created M2M through tables.** If the renamed model has an auto-created M2M, the through table's name may be derived from `db_table` and so stay unchanged. Its column name (for example `foo_id` → `bar_id`) is derived from the *model name* and would normally be renamed. Two options:
   - Skip everything, which makes the operation a strict no-op.
   - Still rename the M2M column, which keeps the database consistent with the new state.

   Which is intended? A strict no-op could leave the column name out of sync with what the ORM expects.
2. **Table name comparison.** Should equality be case-insensitive or account for backend quoting and truncation? For example, Oracle truncates names, and `"Foo"` vs `"foo"` may matter on some backends.
3. **One-sided `db_table`.** Should the no-op also apply when only one side sets `db_table` explicitly but the effective names happen to match? This spec assumes yes (Assumption 3).
4. **Compatibility.** Is there any backend or third-party reliance on the current FK drop/recreate side effect, such as constraint name regeneration, that would make a no-op a compatibility concern?
5. **Target branch.** Which Django version(s) or branch should this target, and does it qualify for a backport?