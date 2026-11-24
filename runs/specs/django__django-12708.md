# Spec: Deleting `index_together` must not crash when `unique_together` covers the same fields

## Objective

When a model declares the same field set in both `unique_together` and `index_together`, a migration that removes the `index_together` entry fails. The error is raised in `django/db/backends/base/schema.py`, in `_delete_composed_index()` (line 378 in Django 1.11.10):

```
ValueError: Found wrong number (2) of constraints for ...
```

The lookup for the index to drop matches two database objects: the `_uniq` constraint and the `_idx` index. The schema editor cannot tell which one to remove, so it aborts. The user has no supported way past this.

**Who is affected:** Developers who keep a composite unique constraint and a composite index on the same columns. This includes developers moving from `index_together` to the `Meta.indexes` API added in 1.11. For them the removal is part of a refactor, not an intent to drop the index.

The issue raises two concerns:

1. **Crash (primary):** Removing `index_together` must work on its own when `unique_together` covers the same fields. It must drop only the plain index and leave the unique constraint in place.
2. **Needless re-creation (secondary):** Moving an index declaration from `index_together` to `Meta.indexes` should not drop and re-create a database index that is the same in substance.

**Acceptance criteria (from the user's view):**
- Given a model with fields `(a, b)` in both `unique_together` and `index_together`, generating and applying a migration that removes `index_together` succeeds.
- After that migration, the unique constraint on `(a, b)` still exists and is still enforced.
- After that migration, the non-unique composite index on `(a, b)` no longer exists, or the behaviour is documented if the backend treats the unique constraint as the index.
- The reverse migration re-creates the index without error.
- Concern 2 is in scope only if confirmed (see Open Questions). If confirmed: moving the same field set from `index_together` to `Meta.indexes` does not cause the index to be dropped and re-created when applied.

## Assumptions

1. The primary deliverable is concern 1, the crash fix. Concern 2 is a separate, independently testable capability that may need its own spec or ticket.
2. The fix targets the current development branch of Django, not a backport to 1.11.x, unless told otherwise.
3. The ambiguity comes from the constraint lookup, which filters by column set and "index" flag without excluding unique constraints. This is inferred from the error message and has not been verified in source.
4. All built-in backends (PostgreSQL, MySQL, SQLite, Oracle) are in scope. Some may report the unique constraint as an index during introspection.
5. The symmetric case is also in scope as a regression guard: deleting `unique_together` while `index_together` on the same fields remains.
6. Public APIs do not change. `unique_together`, `index_together`, and the migration operation signatures keep their current names and arguments.

## Tech Stack

- Django (reported on 1.11.10; the target branch version is unknown)
- Python (version unknown)
- Database backends: all built-in Django backends (assumed)

## Commands

Unknown. The issue gives no repository access or command information.

- Build: unknown
- Test: unknown (e.g. the Django test runner invocation for schema/migration tests is not specified in the issue)
- Lint: unknown

## Project Structure

Known from the issue:
- `django/db/backends/base/schema.py` contains `_delete_composed_index()`, where the error is raised.

Everything else is unknown:
- Location of schema-editor tests: unknown
- Location of migration autodetector tests: unknown
- Location of release notes and docs: unknown

## Code Style

Unknown. Follow existing Django conventions in the touched modules. No snippet is available from the issue.

## Testing Strategy

Framework and file locations are unknown. Required test coverage:

- **Schema-editor level:**
  - On a model with the same fields in `unique_together` and `index_together`, removing `index_together` succeeds.
  - The unique constraint survives.
  - The index is removed.
- **Symmetric case:** Removing `unique_together` while keeping `index_together` on the same fields succeeds and leaves the index.
- **Migration level:**
  - An end-to-end migration applies and reverses cleanly for the reported scenario.
- **Backends:** Tests run against every backend available in CI. Backend-specific introspection differences must be covered or explicitly skipped with a reason.
- **Concern 2 (if accepted):** Autodetector-level tests assert which operations are generated when a declaration moves from `index_together` to `Meta.indexes`.
- **Regression check:** The existing schema and migration test suites still pass.

## Boundaries

- **Always:**
  - Add a failing test that reproduces the `ValueError` before changing behaviour.
  - Preserve the unique constraint when removing the index.
  - Run the existing schema and migrations test suites.
- **Ask first:**
  - Changing the autodetector's generated operations (concern 2).
  - Changing the names of auto-generated constraints or indexes.
  - Backporting to a stable branch.
  - Altering the public signatures of schema-editor methods.
- **Never:**
  - Silence the error by dropping whichever constraint is found first.
  - Drop or weaken the unique constraint as a side effect.
  - Remove or loosen the "wrong number of constraints" safety check for genuinely ambiguous cases.

## Success Criteria

1. The reproduction no longer raises `ValueError`: a model with `(a, b)` in both `unique_together` and `index_together`, followed by removal of `index_together`.
2. After migrating, database introspection shows the unique constraint on `(a, b)` present.
3. After migrating, introspection shows no separate non-unique `_idx` index on `(a, b)`.
4. Reversing the migration restores the index without error.
5. The symmetric case, removing `unique_together` while keeping `index_together`, works and keeps the index.
6. All existing schema and migration tests pass on the supported backends.
7. Concern 2, if in scope: moving `(a, b)` from `index_together` to an equivalent `Meta.indexes` entry does not drop and re-create the index on migrate. Exactly how that is detected is to be agreed.

## Open Questions

1. **Scope split:** Should concern 2 ("moving the declaration should not re-create the index") be handled in this spec or split into a separate spec or ticket? It is independently testable and touches the autodetector rather than the schema editor.
2. **Equivalence for concern 2:** What counts as the "same" index when moving from `index_together` to `Meta.indexes`? The auto-generated name differs from a user-specified `Index(name=...)`. Options include:
   - matching on fields only;
   - requiring a rename operation;
   - documenting a manual `SeparateDatabaseAndState` workaround.
3. **Target branch:** Should this be fixed on the main development branch only, or also backported to 1.11.x or other stable branches?
4. **Backend behaviour:** Some backends may report a unique constraint as an index, or create no separate index when a unique constraint already covers the columns. What is the expected end state per backend?
5. **Interim workaround:** Should the docs or release notes describe how users already blocked can get past this today?
6. **Fix location:** Is it acceptable for the fix to live entirely in `_delete_composed_index()` and its callers? Or should the migration autodetector also coordinate `index_together` and `unique_together` changes, as the reporter suggests ("made coherent (migrations side?)")?
7. **Commands and test locations:** The exact test commands, test file locations, and supported Python and database versions for the target branch are unknown.