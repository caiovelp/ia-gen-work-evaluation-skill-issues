# Spec: Restore objects in FK-safe order in `deserialize_db_from_string` (serialized_rollback)

## Objective

Setting `serialized_rollback = True` on a `TransactionTestCase` should reliably restore the database contents that were captured when the test database was created.

**Current flow (from the issue):**
1. `BaseDatabaseCreation.create_test_db` stores `connection._test_serialized_contents = connection.creation.serialize_db_to_string()`.
2. `TransactionTestCase._fixture_setup` calls `connection.creation.deserialize_db_from_string(connection._test_serialized_contents)`.

**Problem:** `serialize_db_to_string` orders models with `serializers.sort_dependencies`. That function only accounts for natural-key dependencies. It does not place FK targets before the models that reference them, and it cannot do so in general, because circular FKs are allowed. `deserialize_db_from_string` then calls `obj.save()` for each object without wrapping the loop in a transaction. If an object holding an FK is saved before the object it references, an `IntegrityError` can occur.

**Proposed direction (from the reporter):** Wrap the deserialize/save loop in `transaction.atomic(using=self.connection.alias)`. This mirrors `loaddata`, whose `handle()` already wraps loading in `transaction.atomic(using=self.using)`.

**User:** Django developers whose test suites use `serialized_rollback = True` on any database backend.

**Success looks like:** Serialized rollback restores every captured row, whatever the model or app registry ordering, including FKs that point "forward" in serialization order and circular FKs. No `IntegrityError` is raised.

## Assumptions

1. The bug and its fix live in `django/db/backends/base/creation.py`, specifically `deserialize_db_from_string`. This is the only path the issue shows.
2. The codebase is the Django version shown in the diff. It still uses `django.utils.six`, so it is the Python 2/3-compatible era.
3. Serialization order is deterministic, because the app registry keeps apps and models in `OrderedDict`. A deterministic regression test is therefore feasible.
4. A transaction alone is enough only on backends where FK constraints are deferred until commit. Django creates FKs as `DEFERRABLE INITIALLY DEFERRED` on PostgreSQL, so the fix works there.
5. On backends that check FKs immediately or do not enforce them at insert time, the transaction alone may not fix the bug. This needs verification (see Open Questions).
6. The public behaviour and signatures of `serialize_db_to_string` and `deserialize_db_from_string` must not change.
7. `serializers.sort_dependencies` is not to be changed to handle FK ordering. The issue states this is impossible in general because of cycles.

## Tech Stack

- Python and Django. Exact versions are **unknown**; the codebase predates the removal of `django.utils.six`.
- Modules referenced in the issue:
  - `django.db.transaction`
  - `django.core.serializers`
  - `django.db.router`
  - `django.apps.apps`
  - the `loaddata` management command
- Database backends affected: all backends supported by Django. Per-backend behaviour is **unknown**.

## Commands

**Unknown.** The issue gives no build or test commands. They are to be confirmed from the repository's contributor docs and test runner:
- Build: unknown
- Test (full suite / targeted): unknown
- Lint: unknown

## Project Structure

Known from the issue:
- `django/db/backends/base/creation.py` contains `BaseDatabaseCreation`, `serialize_db_to_string`, `deserialize_db_from_string` and `create_test_db`.
- `TransactionTestCase._fixture_setup` is in an unknown file, presumably Django's test framework module.
- `serializers.sort_dependencies` is in an unknown file within `django.core.serializers`.
- The `loaddata` command `handle()` is the reference pattern for transactional loading.

Unknown:
- Where the regression test should live.
- Which test apps or models with FKs exist for it.

## Code Style

Follow the existing style of `creation.py`. The reporter's proposed change is the reference for shape and scope: a minimal change that adds `transaction` to the existing `from django.db import router` import and wraps the existing loop:

```python
data = StringIO(data)
with transaction.atomic(using=self.connection.alias):
    for obj in serializers.deserialize("json", data, using=self.connection.alias):
        obj.save()
```

Other conventions (linting, line length) are **unknown**.

## Testing Strategy

**Regression test (required).** It must be deterministic and must fail before the fix and pass after it.
- Use models whose serialization order, driven by app registry order, puts an object with an FK **before** the object it references.
- Serialize with `serialize_db_to_string`, clear the tables, call `deserialize_db_from_string`, and assert that all objects are restored with correct FK values and no `IntegrityError`.

**Circular FK case.** Two models that reference each other, both restored successfully.

**Backend coverage.** The test must run on every backend in the CI matrix. It must not be skipped on backends where a bare transaction is insufficient; those backends need a working fix.

**Non-regression.** Existing `serialized_rollback` and `loaddata` tests keep passing.

Framework, test location and coverage thresholds are **unknown**; use Django's existing test suite conventions.

## Boundaries

**Always:**
- Keep the change scoped to `deserialize_db_from_string` and its direct needs.
- Use the connection's alias for any transaction or constraint handling.
- Add a deterministic regression test.

**Ask first:**
- Changing `serializers.sort_dependencies` or the serialization format/order in `serialize_db_to_string`.
- Disabling or deferring constraint checks per backend, for example via backend-specific constraint toggles.
- Changing the public signatures of the creation methods.

**Never:**
- Swallow `IntegrityError`s to make the test pass.
- Weaken FK integrity in the restored data.
- Remove or skip existing tests.
- Alter `loaddata` behaviour as part of this fix.

## Success Criteria

- [ ] `deserialize_db_from_string` performs all saves inside a single atomic block on `self.connection.alias`.
- [ ] A regression test that triggers FK-before-target ordering fails on the current code and passes after the fix.
- [ ] Circular FK data serialized by `serialize_db_to_string` restores without error.
- [ ] After restoration, every restored row's FK values reference existing rows. If constraints were deferred or disabled during load, integrity is verified at the end.
- [ ] Behaviour is correct on every backend in the CI matrix, or any backend limitation is explicitly documented and approved.
- [ ] No existing `serialized_rollback` or `loaddata` tests regress.

## Open Questions

1. **Is `transaction.atomic` alone sufficient on all backends?** It fixes the problem where FK constraints are deferred until commit (PostgreSQL). On backends with immediate FK checks, saving a referencing row first may still fail inside the transaction. Should the fix also disable constraint checking during the load and then run an integrity check before commit, as `loaddata` may do?
2. Does `loaddata` disable constraint checks in addition to using a transaction? The issue shows only the `atomic` wrapper. If it does, should `deserialize_db_from_string` mirror that exactly?
3. Which existing test models or apps can produce a deterministic "FK serialized before its target" ordering? Or should new test models be added?
4. Which Django versions or branches should receive the fix (backport scope)?
5. Should a release note be added, given that this is user-visible test-framework behaviour?
6. What are the exact commands to run the targeted and full test suites in this repository?