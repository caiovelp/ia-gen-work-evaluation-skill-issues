# Spec: Make `auth.0011_update_proxy_permissions` tolerate pre-existing proxy-model permissions

## Objective

**Problem.** When upgrading to Django 2.2, `python manage.py migrate` fails while applying `auth.0011_update_proxy_permissions` with:

```
django.db.utils.IntegrityError: duplicate key value violates unique constraint
"..._auth_permission_content_type_id_..._uniq"
DETAIL: Key (content_type_id, codename)=(12, add_agency) already exists.
```

The migration moves proxy-model permissions from the concrete model's `ContentType` to the proxy model's own `ContentType`. If a `Permission` with the same `codename` already exists on the target content type, the `(content_type_id, codename)` unique constraint on `auth_permission` is violated. The reporter hit this when upgrading from 2.0.13 and from 2.1.8. The title points to one known trigger: models that were deleted and **recreated as a proxy** under the same name.

**Who is affected.** Django users upgrading existing projects to 2.2 whose `auth_permission` table already holds rows for a proxy model's content type alongside the matching rows on the concrete model's content type.

**What success looks like.** `auth.0011_update_proxy_permissions` finishes on databases where both rows already exist. It does not lose data silently, and it leaves the permission table in a consistent, explainable state. The user learns about any conflicting rows the migration could not move automatically.

### Acceptance criteria (behavioral)

1. **AC1 – No crash on conflict.** If a permission with the same `codename` already exists on the proxy's content type, the forward migration does not raise `IntegrityError`.
2. **AC2 – Non-conflicting permissions still move.** Proxy permissions with no conflict are reassigned from the concrete content type to the proxy content type, exactly as the migration does today.
3. **AC3 – Conflicts are reported.** For every conflicting permission, the migration writes a human-readable message to the migration output. The message names the app/model and codename and tells the user to check the affected permission rows manually.
4. **AC4 – Atomicity per conflict.** A conflict on one permission does not prevent other permissions, models or apps from being processed. It does not leave the migration half-applied in a way that breaks a re-run.
5. **AC5 – Reverse migration.** Backward migration likewise does not crash when the same conflict exists in the reverse direction.
6. **AC6 – Idempotence.** Re-running the migration logic on an already-migrated database is a no-op and produces no errors.
7. **AC7 – No silent destruction.** The migration does not delete or merge conflicting `Permission` rows, or their user/group assignments, unless that behavior is explicitly approved (see Open Questions).

## Assumptions

1. The bug is in the data migration `django/contrib/auth/migrations/0011_update_proxy_permissions.py` introduced in Django 2.2. It is not a problem in the reporter's own project setup.
2. The duplicate rows on the proxy content type exist legitimately. They come from cases such as a model recreated as a proxy, a rename, or a `post_migrate` permission creation that already ran for the proxy content type.
3. The unique constraint `(content_type_id, codename)` on `auth_permission` is correct and must not change.
4. The fix belongs in Django itself, targeted at the 2.2 line (and the main branch at that time), and must work on all supported database backends.
5. "Report the conflict" means writing to the migration's standard output or warning channel. It does not mean raising an exception.
6. The migration is never edited to depend on project-specific models. It uses only the historical models available through `apps`.
7. The `(content_type_id, codename)` value shown in the traceback reflects the actual state. The `co.ntent_type_id` typo in the report is a copy/paste artifact.

## Tech Stack

- Python and Django (affected version: 2.2; upgrade sources reported: 2.0.13, 2.1.8)
- `django.contrib.auth` and `django.contrib.contenttypes`
- Reporter's database: PostgreSQL (inferred from the error format). The fix must stay backend-agnostic.
- Exact supported Python and database versions for the target branch: **unknown**

## Commands

Not visible from the issue; all **unknown**:

- Build: unknown
- Test: unknown (presumably Django's own test runner; exact invocation and test label unknown)
- Lint: unknown
- Reproduce: `python manage.py migrate` (from the issue) on a database that already contains conflicting proxy permissions

## Project Structure

Known from the issue and the migration name only:

- `django/contrib/auth/migrations/0011_update_proxy_permissions.py`: the failing data migration (path inferred from the migration label `auth.0011_update_proxy_permissions`)
- Test location for auth migrations: **unknown**

## Code Style

Follow the existing conventions of the Django codebase. The specific style guide and lint configuration cannot be seen from the issue: **unknown**.

## Testing Strategy

- **Regression test for AC1/AC3.** Create a concrete model and a proxy model, and pre-create a `Permission` with the same codename on both content types. Run the migration's forward function. Assert that it raises no exception and that a conflict message is emitted.
- **AC2.** In the same scenario, include a non-conflicting permission. Assert that it ends up on the proxy content type.
- **AC5.** Run the reverse function in the mirrored conflict scenario. Assert that it raises no exception.
- **AC6.** Run the forward function twice. Assert that the second run changes nothing.
- **AC7.** Assert that the conflicting `Permission` rows still exist and that user/group links to them are untouched.
- **Existing tests.** The existing tests for `0011_update_proxy_permissions` keep passing unchanged.
- Test framework and exact location: Django's internal test suite. Path and command are **unknown**.

## Boundaries

- **Always:**
  - Use historical models (`apps.get_model`) inside the migration.
  - Keep the fix backend-agnostic.
  - Add regression tests reproducing the conflict.
  - Keep existing non-conflict behavior identical.
- **Ask first:**
  - Deleting or merging duplicate `Permission` rows.
  - Reassigning user or group permission links between duplicates.
  - Changing the unique constraint.
  - Adding a new migration rather than editing `0011` in place.
  - Backporting scope.
- **Never:**
  - Swallow all `IntegrityError`s indiscriminately without reporting.
  - Silently drop permissions or user/group grants.
  - Make the migration depend on project or app code outside `contrib.auth` and `contrib.contenttypes`.

## Success Criteria

- [ ] On a database containing a permission with the same codename on both the concrete and the proxy content type, `migrate` completes `auth.0011_update_proxy_permissions` without `IntegrityError` (forward and backward).
- [ ] Non-conflicting proxy permissions are reassigned exactly as before the fix.
- [ ] Each skipped conflict produces an output message identifying app label, model and codename, with guidance to review it manually.
- [ ] No `Permission` rows, or their user/group assignments, are deleted or altered for conflicting entries.
- [ ] A second application of the migration logic is a no-op.
- [ ] New regression tests cover these cases, and all existing auth migration tests pass.

## Open Questions

1. **Conflict resolution policy.** Which behavior is wanted when a duplicate exists?
   - (a) Skip and warn (proposed default).
   - (b) Merge user/group grants into the proxy permission and delete the concrete one.
   - (c) Something else.
2. **Fix location.** Should `0011` be edited in place, given that it already ran successfully for many users? Or should the fix go into a follow-up migration?
3. **Backport target.** Which release branches should receive the fix (2.2.x patch release)?
4. **Warning channel.** How should the conflict be reported: plain stdout, `warnings.warn`, or a system check? What exact message wording is wanted?
5. **Reproduction data.** Can the reporter share the exact model history for `agency` (concrete → deleted → recreated as proxy, or a rename)? Can they share the matching `auth_permission` and `django_content_type` rows? The linked full stack trace was not available in the issue.
6. **Proxy edge cases.** Are there other triggers to cover, such as a proxy of a proxy, a model switching from concrete to proxy, or a custom `default_permissions`/`permissions` in `Meta`?
7. **Atomicity.** Should each model's update run in its own atomic block (savepoint)? This matters on PostgreSQL, where a failed statement aborts the transaction, and is a decision for whoever implements this.
8. **Commands.** Which test command and test module path should be used for the regression tests?