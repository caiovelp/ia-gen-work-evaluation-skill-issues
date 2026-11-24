# Spec: Clear the primary key after `delete()` on models with no dependencies

## Objective

When a model instance is deleted with `instance.delete()`, Django should set the instance's primary key to `None` afterwards. The issue reports that this does **not** happen for models that have no dependencies, meaning no related objects that need to be collected or cascaded.

The reporter points to `django/db/models/deletion.py`, lines 276–281, and says line 280 should update the model. This suggests a single-object shortcut in the deletion collector that returns early without clearing the PK. This is unverified; the source was not inspected.

**Who is affected:** Django users who call `.delete()` on an instance and then check `instance.pk`. Examples are code that tests `pk is None` to detect deleted or unsaved state, and code that re-saves an instance as a new row.

**Expected behaviour:** After `instance.delete()` returns, `instance.pk` is `None`. This must hold whether or not the model has relations or dependents, so dependency-free models behave the same as models deleted through the full collection path.

### Acceptance criteria

1. A model with no relations, saved and then deleted with `obj.delete()`, has `obj.pk is None` afterwards.
2. The row is removed from the database, as today.
3. The return value of `delete()` (deleted count and per-model breakdown) is unchanged from current behaviour.
4. Instances deleted through the existing path for models with dependencies still have their PKs cleared, so there is no regression.
5. No extra database queries are added to the dependency-free path, if it is a performance optimisation (unverified; see Open Questions).

## Assumptions

1. The project is the Django framework, and the affected code is the deletion collector in `django/db/models/deletion.py`.
2. The reported lines 276–281 belong to an early-return or "fast delete" branch used when exactly one instance with no dependencies is deleted.
3. The intended invariant, `pk is None` after delete, is already implemented on the normal path. The bug is only that the shortcut branch skips it.
4. "Set to None" means the model's primary-key attribute (`pk` / the PK field's attname). Other fields are not cleared.
5. This change applies to `Model.delete()` on a single instance. The issue does not cover `QuerySet.delete()`, which does not modify in-memory instances.
6. Signals (`pre_delete` / `post_delete`) are out of scope. Their current behaviour on this path must not change.
7. The fix must not change the issue's stated scope, for example by disabling the shortcut path.

## Tech Stack

- Language: Python (version unknown, depends on the target Django branch)
- Framework: Django (target branch or version unknown)
- Affected module: `django/db/models/deletion.py` (from the issue)

## Commands

Unknown. The repository was not inspected. Placeholders to be confirmed:

```
Test (targeted): UNKNOWN (e.g. Django's runtests script for the delete test app; exact invocation unverified)
Test (full):     UNKNOWN
Lint:            UNKNOWN
Build:           N/A / UNKNOWN
```

## Project Structure

Only what the issue states:

```
django/db/models/deletion.py   → Deletion collector; lines 276–281 reported as the faulty branch
```

- The test location is unknown. It is likely the existing delete-related test package in the Django test suite, but the path is unverified.

## Code Style

Follow existing Django conventions in `deletion.py`. No example snippet is included, because the source has not been seen. Keep the change minimal and consistent with how the existing non-shortcut path clears PKs. Reuse that mechanism rather than inventing a new one.

## Testing Strategy

- **Framework:** Django's own test suite (exact runner command unknown).
- **Regression test:** Create and save an instance of a model with no relations, call `.delete()`, and assert `instance.pk is None`. The test should fail before the fix and pass after.
- **Non-regression:** Run the existing deletion tests unchanged. Include a check that a model with dependents still has its PK cleared after delete.
- **Query count (optional):** If the shortcut path exists for performance, assert that it still uses the same number of queries, for example with an `assertNumQueries`-style check.
- **Level:** Unit and integration tests against the test database. No end-to-end tests are needed.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the bug.
  - Run the existing deletion test suite.
  - Keep the return value of `delete()` unchanged.
  - Keep the change confined to the reported branch.
- **Ask first:**
  - Changing the conditions under which the shortcut path is taken.
  - Touching `QuerySet.delete()` behaviour.
  - Changing signal dispatch.
  - Modifying files other than `deletion.py` and tests.
- **Never:**
  - Remove or weaken existing deletion tests.
  - Add extra queries to the shortcut path.
  - Clear fields other than the PK.
  - Change public API signatures.

## Success Criteria

- [ ] `obj.delete()` on a dependency-free model leaves `obj.pk is None`.
- [ ] The database row is gone, and the `delete()` return value matches current output.
- [ ] Models with dependencies still have their PK cleared, and all existing deletion tests pass.
- [ ] The query count on the dependency-free path is unchanged.
- [ ] A new regression test fails on the current code and passes with the fix.

## Open Questions

1. **Target version:** Which Django branch or version is targeted? The line numbers 276–281 depend on it.
2. **Shortcut branch:** Is the branch at lines 276–281 indeed a single-object fast-delete path that returns early? Is it the only path that skips PK clearing?
3. **Clearing mechanism:** How does the normal path clear PKs? Should the fix reuse that exact mechanism, for example setting the PK field's attname to `None`?
4. **Bulk deletes:** Should a multi-object `Collector` usage that hits the fast path also clear PKs, or only the single-instance case?
5. **Inherited models:** Does multi-table inheritance or a proxy model ever reach this branch? If so, should parent-link PKs also be cleared?
6. **Test location:** What is the preferred test location and the runner command for Django's suite in this checkout?
7. **Release notes:** Is a release note required for this bug fix on the target branch?