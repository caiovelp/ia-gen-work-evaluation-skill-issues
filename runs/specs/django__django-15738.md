# Spec: Autodetector ordering for unique_together removal when a field changes from ForeignKey to ManyToManyField

## Objective

When a model field is changed from `ForeignKey` to `ManyToManyField` and, in the same change, removed from a `unique_together` that included it, `makemigrations` should produce one migration that `migrate` applies cleanly. Today it fails.

**Who is affected:** Django users who change field types in models already deployed to production. They cannot delete or squash their earlier migrations.

**Observed behaviour (from the issue):**

1. The starting model is `Authors`, with:
   - `project_data_set = ForeignKey(ProjectDataSet, on_delete=PROTECT)`
   - `unique_together = (('project_data_set', 'state', 'start_date'),)`
2. The user changes the field to `ManyToManyField(ProjectDataSet)` and removes `unique_together` at the same time. This is required, because `unique_together` cannot reference an M2M field.
3. `python3 manage.py makemigrations` succeeds.
4. `python3 manage.py migrate` fails with:
   `ValueError: Found wrong number (0) of constraints for app_authors(project_data_set, state, start_date)`
5. The failure happens even on a freshly recreated database, so it does not depend on existing DB state.

**Current workaround:** Generate two migrations. The first removes `unique_together`, the second changes the field type. The user wants one migration.

**Suspected cause (to be confirmed, not asserted):** Django cannot alter an FK into an M2M in place, so the autodetector likely emits a field removal plus a field addition. The removal of the old column (and its constraint) appears to be ordered *before* the `AlterUniqueTogether` operation that removes the constraint. When `AlterUniqueTogether` then runs, it finds 0 matching constraints.

**User stories / acceptance criteria:**

- As a developer, when I change an FK to an M2M and drop a `unique_together` that referenced that FK in the same edit, `makemigrations` produces a migration that `migrate` applies without error.
- As a developer, the generated migration removes the unique constraint before it removes or replaces the field that the constraint references.
- As a developer, the database schema after migration matches what I would get from the two-step workaround: no unique constraint on the old columns, the FK column is gone, and the M2M join table exists.

## Assumptions

1. The bug is in the Django migrations **autodetector**, specifically in how it orders the operations it generates. It is not in the schema editor's constraint lookup.
2. An FK → M2M change is detected as a remove-field plus an add-field. It is not an `AlterField`.
3. The same ordering problem probably applies to `index_together` and to any other field removal that is paired with a removal of a `unique_together` / `index_together` entry referencing that field. Whether this is in scope is listed under Open Questions.
4. The fix must not require users to edit or delete existing migrations.
5. The behaviour is database-backend independent, since the user reports it is "not depending on database". The specific backend was not stated.
6. The attached reproduction project is not available to me. The model definitions in the issue are treated as the reproduction.
7. The target is the Django main branch. The affected version was not stated.

## Tech Stack

- Django. The version is **unknown** (not stated in the issue).
- Python 3 (`python3` is used in the issue). The minor version is unknown.
- Database backend: **unknown**. The issue says the error occurs regardless of DB.
- Relevant subsystems: migrations autodetector, migration operations (`RemoveField`, `AddField`, `AlterUniqueTogether`), schema editor.

## Commands

From the issue (user-level reproduction):

```
python3 manage.py makemigrations
python3 manage.py migrate
```

The Django test-suite commands (runner invocation, settings module, flags) are **unknown**. The repository is not visible to me.

## Project Structure

**Unknown.** The repository layout is not visible. Expected areas of interest, which must be confirmed against the real tree:

- The migrations autodetector source
- The migration operations source
- The tests for the autodetector and for migration operations

No paths are asserted.

## Code Style

**Unknown.** The project's style conventions are not visible. Follow the existing conventions of the surrounding autodetector code and tests.

Reproduction models, taken verbatim from the issue.

Before:
```python
class Authors(models.Model):
    project_data_set = models.ForeignKey(ProjectDataSet, on_delete=models.PROTECT)
    state = models.IntegerField()
    start_date = models.DateField()

    class Meta:
        unique_together = (('project_data_set', 'state', 'start_date'),)
```

After:
```python
class Authors(models.Model):
    project_data_set = models.ManyToManyField(ProjectDataSet)
    state = models.IntegerField()
    start_date = models.DateField()
```

Supporting models: `DataSet`, `Project` (M2M to `DataSet` through `ProjectDataSet`), and `ProjectDataSet` (FKs to both, with `unique_together = (('data_set', 'project'),)`).

## Testing Strategy

- **Autodetector unit test:** Build a before-state and an after-state matching the reproduction. Assert:
  - the generated operation types;
  - the operation order, with the unique_together removal (`AlterUniqueTogether` to empty or `None`) **before** the removal of `project_data_set`;
  - the addition of the M2M field.
- **Operation / integration test:** Apply the generated operations against a real test database. Assert that no `ValueError` is raised and that the final schema has:
  - no unique constraint on `(project_data_set, state, start_date)`;
  - no FK column;
  - an M2M through table.
- **Regression guard:** Existing autodetector and migration tests must still pass. Ordering changes must not break other dependency-ordering scenarios, such as adding a field and then adding `unique_together` on it.
- **Optional (pending Open Question 1):** Equivalent tests for `index_together`.
- Coverage expectations: **unknown**. Follow project norms.

## Boundaries

- **Always:**
  - Reproduce the failure with a test before changing behaviour.
  - Keep the change inside the autodetector's operation generation and ordering, unless the investigation proves otherwise.
  - Run the full migrations test suite.
- **Ask first:**
  - Changing the behaviour of the schema editor or of `AlterUniqueTogether` itself.
  - Changing the overall operation-generation order in ways that alter output for unrelated, already-working scenarios.
  - Extending scope to `index_together`, `Meta.constraints`, or `Meta.indexes`.
- **Never:**
  - Require users to rewrite or delete existing migrations.
  - Suppress or downgrade the "wrong number of constraints" error to hide the ordering problem.
  - Remove or weaken existing tests.

## Success Criteria

1. With the reproduction models, one `makemigrations` run followed by `migrate` completes without error on a fresh database.
2. The same holds on a database already at the pre-change migration state.
3. In the generated migration, the operation that removes the `unique_together` entry comes before the operation that removes the `project_data_set` FK field.
4. The resulting schema is equivalent to the result of the two-migration workaround.
5. A regression test covering this scenario exists and fails without the fix.
6. All pre-existing migrations and autodetector tests pass.

## Open Questions

1. **Scope:** Should the fix also cover `index_together` removal in the same scenario? What about other field-type changes that become remove plus add (not only FK → M2M)? What about the reverse direction, M2M → FK with `unique_together` added?
2. **Affected versions:** Which Django version did the reporter use? Which versions should receive the fix (main only, or backports)?
3. **Root cause confirmation:** Is the `RemoveField`-before-`AlterUniqueTogether` ordering hypothesis correct? Or does the generated migration contain some other combination, such as a missing `AlterUniqueTogether` or an `AlterField` attempt? The attached project is unavailable to verify this.
4. **Backend:** Does the error reproduce on every supported backend? SQLite remakes tables on field removal, which may drop the constraint implicitly. Does behaviour differ between backends?
5. **Partial removal:** What if `unique_together` keeps other tuples that do not involve the changed field? Only the tuples referencing the removed field should be removed first. Is that the expected behaviour?
6. **Test commands and paths:** What is the exact test runner invocation, and where do the autodetector and operations tests live? These are unknown without repository access.