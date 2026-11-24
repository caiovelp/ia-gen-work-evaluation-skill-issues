# Spec: Squashed migrations should drop `index_together` after an `index_together` → `indexes` transition

## Objective

In Django 4.2, `Meta.index_together` is deprecated in favour of `Meta.indexes`. A project that has already migrated from `index_together` to `indexes` still has historical migrations that reference `index_together`, through `CreateModel` options or `AlterIndexTogether` operations. Loading those migrations emits deprecation warnings.

The documented way to clean up migration history is `squashmigrations`. Today the squashed output still contains `index_together`, so the warnings remain. The only workaround is to rewrite migrations by hand. The issue calls this a 4.2 release blocker for that reason.

**Goal:** when a migration history moves a model from `index_together` to equivalent `indexes`, squashing it should produce migrations that contain no `index_together` references. That removes the deprecation warnings without any manual rewriting.

**Users:** Django project maintainers upgrading to 4.2+ who want a warning-free migration history ahead of `index_together` removal.

**Acceptance criteria (user-level):**
- Given migrations that create a model with `index_together`, then transition to equivalent `Meta.indexes`, running `squashmigrations` produces a squashed migration with no `index_together` option and no `AlterIndexTogether` operation.
- Loading or applying the squashed migration emits no `index_together` deprecation warning.
- The database schema after applying the squashed migration matches the schema after applying the original migrations, including index names.

## Assumptions

1. The fix belongs in the migration optimizer, i.e. operation reduction used by `squashmigrations`. It does not belong in the autodetector or in a new command.
2. The typical transition is what the autodetector generates when a user replaces `index_together` with `indexes`. This is believed to be a `RenameIndex` with `old_fields=...` (so existing DB indexes are renamed, not dropped and recreated), plus removal of `index_together`. The exact operation sequence still needs to be confirmed (see Open Questions).
3. Folding into `CreateModel` is the relevant case. A `CreateModel` with `index_together` followed by transition operations should collapse into a single `CreateModel` with `indexes` only.
4. "Equivalent" means same model, same field list in the same order, with the resulting index name preserved as the user's `Meta.indexes` name.
5. The target is the Django 4.2 branch (release blocker), with forward-port to main.
6. Migrations already squashed or partially transitioned are out of scope beyond what the optimizer can reduce.
7. Behaviour for `unique_together` is unchanged.

## Tech Stack

- Python / Django (4.2 release line). The exact supported Python versions are **unknown**.
- Components involved (based on assumptions; locations not visible in the issue): migration operations (`CreateModel`, `AlterIndexTogether`, `AddIndex`, `RenameIndex`, `RemoveIndex`), the migration optimizer, and the `squashmigrations` management command.

## Commands

- Build: **unknown** (not stated in the issue)
- Test: **unknown**. Presumably Django's own test runner, targeting the migrations test suites. The exact command and flags need confirmation.
- Lint: **unknown**
- Reproduce: `python manage.py squashmigrations <app_label> <migration_name>` on a project with the transition described above, then load the squashed migrations with deprecation warnings enabled (e.g. `python -W error::DeprecationWarning ...`). The exact warning class name is **unknown**.

## Project Structure

**Unknown.** The issue gives no paths. The expected areas to touch are the migration operations module, the optimizer, and the corresponding migration/optimizer tests, plus release notes for 4.2.x. These need confirming against the repository.

## Code Style

**Unknown** from the issue. Follow existing conventions in the migration operations' `reduce()` implementations and the existing optimizer tests, which typically assert an input operation list optimizes to an expected output list.

## Testing Strategy

- **Unit (optimizer) tests:** given an input list of operations, assert the optimized output. Cases:
  - `CreateModel(options={"index_together": [...]})` followed by a `RenameIndex(old_fields=...)` collapses to `CreateModel(options={"indexes": [Index(fields=..., name=new_name)]})` with no `index_together`.
  - `CreateModel` with multiple `index_together` entries where only some are renamed. Converted entries move to `indexes` and the remaining ones stay in `index_together`.
  - `AlterIndexTogether` followed by the transition operations reduces correctly. The exact case is pending confirmation of the real operation sequence.
  - Negative cases: field lists that don't match, a different model, or intervening operations that block reduction must **not** be reduced.
- **Command-level test:** `squashmigrations` on a fixture app with the transition produces output with no `index_together`.
- **Warning test:** loading the squashed migration raises no `index_together` deprecation warning.
- **Schema equivalence:** applying the original and the squashed migrations yields the same indexes, with the same names, on supported backends.
- Coverage expectation: **unknown**. At minimum, every new reduction path needs positive and negative tests.

## Boundaries

- **Always:**
  - Preserve schema equivalence and index names between the squashed and original migrations.
  - Add optimizer tests for every new reduction.
  - Keep reductions conservative: if equivalence isn't certain, don't reduce.
- **Ask first:**
  - Changing autodetector output or the shape of operations it generates.
  - Changing the public signatures of migration operations.
  - Backporting scope beyond 4.2.
  - Any change to deprecation timing or warning text.
- **Never:**
  - Silently drop `index_together` entries that have no equivalent `indexes` entry.
  - Change `unique_together` behaviour.
  - Suppress the deprecation warning instead of removing the cause.
  - Alter applied-migration semantics for existing databases.

## Success Criteria

1. Squashing a migration history that contains the full `index_together` → `indexes` transition yields squashed migrations containing no `index_together` and no `AlterIndexTogether`.
2. No `index_together` deprecation warning is emitted when loading or running the squashed migrations.
3. Partial transitions keep only the untransitioned `index_together` entries.
4. Schema, including index names, is identical between the original and squashed histories.
5. The existing migrations/optimizer test suites pass, and the new optimizer and squash tests pass.
6. A release note entry is added for the 4.2.x fix (exact file **unknown**).

## Open Questions

1. What exact operation sequence does the autodetector emit for an `index_together` → `indexes` change? Is it `RenameIndex(old_fields=...)` alone, `AddIndex` + `AlterIndexTogether`, or something else? The reduction rules depend on this.
2. The issue refers to "see comment" without its content. What scenario or reproduction does that comment describe?
3. Should transitions that are *not* preceded by a `CreateModel` in the squashed range also be handled? Example: `AlterIndexTogether(...)` → `AlterIndexTogether(set())` where `RenameIndex` sits in between.
4. Should matching consider field order and index name only, or also other `Index` attributes (`db_tablespace`, `opclasses`, `condition`), and treat any mismatch as non-equivalent?
5. Should this be backported only to 4.2 or also to earlier supported branches?
6. What are the expected test command, test locations, and release-notes file in the repository?
7. If a project's history never reaches a `CreateModel` within the squash range, is it acceptable that some warnings remain, and should that be documented?