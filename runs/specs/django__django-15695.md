# Spec: RenameIndex re-apply crash after backward on an unnamed `unique_together` index

## Objective

When `RenameIndex` targets an **unnamed** index (identified by fields, created via `unique_together`), the sequence **forwards → backwards → forwards** crashes. On PostgreSQL the second `database_forwards()` raises:

```
django.db.utils.ProgrammingError: relation "new_pony_test_idx" already exists
```

The cause is a state mismatch. Today `database_backwards()` for the unnamed case is a no-op that runs zero queries, so the index keeps the name `new_pony_test_idx`. Re-applying forwards then tries to rename the index to a name it already has.

**Who is affected:** Developers who reverse and re-apply migrations that contain `RenameIndex` with old fields, for example when switching branches or using `migrate app <previous>` followed by `migrate`. Third-party backends may also be affected.

**What success looks like:** Moving such a migration backward and then forward again completes without error. After the final forward step, the index is named `new_pony_test_idx`. The database and the migration state stay consistent across repeated cycles.

**Issue statement of intent:** "RenameIndex() should restore the old auto-generated name when an unnamed index for unique_together is moving backward."

> ⚠️ This intent conflicts with the issue's own proposed test. That test keeps the existing assertions that backwards runs 0 queries and that `new_pony_test_idx` still exists after backwards. See Open Questions Q1.

### Acceptance criteria
1. AC1: For an unnamed-index `RenameIndex` (old fields, `unique_together`), running `database_forwards`, then `database_backwards`, then `database_forwards` on PostgreSQL raises no exception.
2. AC2: After the second `database_forwards`, an index named `new_pony_test_idx` exists on the table.
3. AC3: Exactly one index covers those fields after the cycle. There are no duplicates and no orphaned auto-named indexes.
4. AC4: The backward behaviour matches whichever option Q1 resolves to, and the test asserts it explicitly:
   - **Option A:** Backwards stays a no-op with 0 queries, and forwards tolerates the index already having the target name.
   - **Option B:** Backwards restores the original auto-generated name.
5. AC5: Existing `RenameIndex` behaviour for **named** indexes (`old_name`) does not change, either forwards or backwards.
6. AC6: The operation's deconstruction output does not change.
7. AC7: The scenario passes on every database backend in the project's test matrix, not only PostgreSQL. SQLite, MySQL and Oracle behaviour is unknown and must be verified.

## Assumptions

1. The codebase is Django. The operation is `RenameIndex` in the migrations operations module. The exact source path is not shown in the issue, so it is **unknown**.
2. The relevant test is in `OperationTests` in `tests/migrations/test_operations.py`, around lines 2988–2997 according to the diff. It uses `operation`, `app_label`, `project_state`, `new_state`, `table_name` and `assertIndexNameExists`.
3. "Unnamed index" means a `RenameIndex` built with `old_fields`, not `old_name`, and pointing at an index created via `unique_together`.
4. The crash was observed on PostgreSQL. Other backends may fail differently or not at all.
5. The fix should not require changes to migration files or the autodetector output.
6. The fix should not need a new dependency or a schema/format change to migrations.

## Tech Stack

- Python and Django. Versions are **unknown**.
- PostgreSQL is the backend where the failure was reproduced. The version is **unknown**.
- Test framework: Django's test suite (`OperationTestBase` / `OperationTests`).

## Commands

The issue does not provide any commands. All of the following are **unknown** and need confirmation:
- Build: unknown
- Test (targeted): unknown. It should run `tests/migrations/test_operations.py` against PostgreSQL.
- Test (full migrations suite): unknown
- Lint/format: unknown

## Project Structure

Only what the issue shows:
```
tests/migrations/test_operations.py  → Migration operation tests (OperationTests); regression test goes here
```
- Location of the `RenameIndex` implementation: **unknown**.
- Location of the schema editor and index-rename backend code: **unknown**.

## Code Style

No style guide is visible. Follow the conventions of the surrounding code in `tests/migrations/test_operations.py`. The issue's diff shows those conventions:

```python
# Re-apply renaming.
with connection.schema_editor() as editor:
    operation.database_forwards(app_label, editor, project_state, new_state)
self.assertIndexNameExists(table_name, "new_pony_test_idx")
```

Conventions:
- Short `#` comments describe each step.
- Each step runs inside a `with connection.schema_editor() as editor:` block.
- Assertions use the existing `assertIndexNameExists` helper.
- Query counts are checked with `assertNumQueries` where that applies.

## Testing Strategy

- **Regression test:** Extend the existing unnamed-index `RenameIndex` test in `tests/migrations/test_operations.py` with the re-apply step shown in the issue. Write it first and confirm it fails on PostgreSQL.
- **Backward assertions:** Make the test state the decided backward contract explicitly (Q1):
  - Option A: query count and the index name after backwards.
  - Option B: the auto-generated name restored and `new_pony_test_idx` gone.
- **Repeated cycles (optional, recommended):** Cover forwards → backwards → forwards → backwards to show the operation is stable over more than one cycle.
- **Non-regression:** The existing tests for named-index `RenameIndex` and for `RenameIndex` with old fields must still pass unchanged.
- **Backends:** Run on PostgreSQL at minimum, plus the other backends in CI. The CI matrix is **unknown**.
- **Coverage expectations:** **unknown**.

## Boundaries

- **Always:**
  - Reproduce the crash with a failing test before changing any behaviour.
  - Keep the database and migration state consistent.
  - Keep deconstruction output stable.
  - Run the full migrations test module.
- **Ask first:**
  - Changing the documented or tested backward contract of `RenameIndex` for unnamed indexes (Q1).
  - Adding queries to `database_backwards` that are currently asserted to be 0.
  - Changing schema-editor or backend-level rename APIs.
  - Changing how auto-generated index names are computed.
- **Never:**
  - Remove or weaken the existing `assertNumQueries(0)` assertion or other existing assertions without approval.
  - Swallow database errors with broad `try/except`.
  - Change behaviour for named-index `RenameIndex`.
  - Alter unrelated operations.

## Success Criteria

- [ ] The issue's diff, with the re-apply step added, passes on PostgreSQL.
- [ ] After forwards → backwards → forwards, `new_pony_test_idx` exists and exactly one index covers the fields.
- [ ] The backward behaviour for unnamed indexes matches the option chosen in Q1 and is asserted in the test.
- [ ] All existing `RenameIndex` and migrations operation tests pass on every backend in CI.
- [ ] `operation.deconstruct()` output does not change.

## Open Questions

1. **Q1 – Backward contract:** Should `database_backwards` for an unnamed index restore the original auto-generated name, as the issue description says? Or should it stay a 0-query no-op, as the issue's own test still asserts, with `database_forwards` treating an index that already has the target name as a no-op? These two options are mutually exclusive, and the choice decides AC4.
2. **Q2:** If Option B is chosen, how should the original auto-generated name be determined? Should it be recomputed the way index names are normally generated, or looked up from the database by fields? Is that name guaranteed to be the same across backends and versions?
3. **Q3:** If Option A is chosen, how should forwards detect that the index already has the target name? Possible sources are database introspection or a comparison of the found index's name with `new_name`. Is introspection acceptable here?
4. **Q4:** Does the same crash or inconsistency happen on SQLite, MySQL and Oracle? Should the fix be verified on all of them?
5. **Q5:** Is this a regression from an earlier release, and should the fix be backported? Which versions are affected?
6. **Q6:** What are the exact commands to run the targeted test against PostgreSQL in this repository? Where does the `RenameIndex` implementation live?
7. **Q7:** Does the same issue apply to unnamed indexes from `index_together`, or only `unique_together`? Should the fix and tests cover both?