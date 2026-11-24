# Spec: `migrate --database` must route all post-migration permission work to the named database

## Objective

When `manage.py migrate` is run with an explicit database, Django still makes at least one database read **after** the migrations finish that ignores that database. Instead, the read is sent to the configured `DATABASE_ROUTERS`. The reporter says this happens while permissions are being added, which suggests the `django.contrib.auth` post-migrate permission-creation step. That location is unverified.

**Who is affected:** projects with a custom database router whose `db_for_read` / `db_for_write` depends on request-scoped state, such as a thread-local tenant set by middleware. During a management command there is no request, so the router raises an error. Here it raises `InvalidTenantException`. The reporter sees `read {}` printed (a `db_for_read` call with empty hints) just before the exception.

**Expected behaviour:** when a database is named for `migrate`, every database call made in the context of that command uses the named database. This includes post-migrate signal handlers that ship with Django, such as permission creation. The router's `db_for_read` / `db_for_write` should not be needed to choose a database for these calls.

**User stories / acceptance criteria:**
- As an operator of a multi-tenant service, I can run `migrate` with a database argument and have it succeed even though my router raises an error when no tenant is set.
- As a Django maintainer, I can rely on Django's built-in post-migrate work (at least permission creation) reading and writing only through the `using` database it receives.

## Assumptions

1. "Database parameter" means the `--database` option of the `migrate` management command. The issue does not name the exact flag.
2. "Adding Permissions" refers to the automatic creation of `auth.Permission` rows (and possibly the related `contenttypes.ContentType` lookups) that runs after migration through the `post_migrate` signal. The exact function and file are **not visible in the issue** and must be confirmed in the codebase.
3. The read that does not respect the database is a query, or a related-object/manager access, that goes through the default manager instead of a manager bound to the `using` database. Since `hints` is `{}`, it is probably a read with no instance hint. This is a hypothesis, not a confirmed root cause.
4. The router in the report is only a reproducer. Fixing the problem means changing Django's database selection, not supporting routers that raise errors in general.
5. Router `allow_migrate` calls are still expected and correct during `migrate`. They decide *whether* to migrate, not *which* database to use. The reporter's router returns `None` there and is not part of the failure.
6. Other built-in post-migrate handlers, such as content types, may have the same problem. The minimum scope is the permission-creation path.
7. The affected Django version is not stated. The behaviour is assumed to exist on the current main branch.

## Tech Stack

- Django (version **unknown**; not stated in the issue)
- Python (version **unknown**)
- Involved components, as described in the issue: the `migrate` management command, database routers (`DATABASE_ROUTERS`), and the auth permission machinery (`django.contrib.auth`, and likely `django.contrib.contenttypes`)

## Commands

**Unknown.** The issue does not include the repository's build, test, or lint commands.
- Reproduce: `manage.py migrate` with a database argument (exact flag assumed to be `--database <alias>`) in a project configured as in the issue.
- Test runner command: **unknown** (to be confirmed from the repository).
- Lint command: **unknown**.

## Project Structure

**Unknown.** No repository layout is visible. The relevant areas, to be located:
- The `migrate` management command implementation
- The `post_migrate` handler(s) that create permissions (in `django.contrib.auth`)
- The content type lookup/cache used by permission creation (in `django.contrib.contenttypes`)
- The existing tests for multi-database behaviour and for auth management/permission creation

## Code Style

Follow the existing Django code style in the files being changed. No style snippet can be quoted because the source is not visible. Where possible, the fix should use the patterns already used nearby to bind queries to a specific database, such as passing `using` explicitly or using database-bound managers. It should not introduce a new mechanism.

## Testing Strategy

- **Framework / location:** Django's own test suite, using its multi-database test support. The exact test module and runner command are **unknown**.
- **Regression test:**
  - Install a test router whose `db_for_read` and `db_for_write` raise an error, or record any call to them.
  - Run `migrate` against a non-default database, or call the permission-creation handler directly with a non-default `using` alias.
  - Assert that no `db_for_read` / `db_for_write` call happens and that permissions are created in the named database.
- **Cases to cover:**
  - Fresh database, where all permissions must be created.
  - Database where some permissions or content types already exist, which exercises the "look up existing" read path.
  - Running against `default` with the same router, to check for no behavioural regression.
- **Coverage expectation:** every database read and write in the permission-creation path runs with the explicit alias under test.

## Boundaries

- **Always:**
  - Keep the fix limited to database selection: pass or bind `using` explicitly.
  - Add a regression test that fails before the fix.
  - Keep router `allow_migrate` semantics unchanged.
- **Ask first:**
  - Widening the change to other `post_migrate` handlers, such as content type creation, or to other management commands.
  - Changing the public signatures of signal handlers or managers.
  - Changing content type cache behaviour, which is shared across databases.
- **Never:**
  - Add special cases for the reporter's router or for thread-local tenancy.
  - Suppress or catch router exceptions to hide the problem.
  - Change behaviour for callers that do not pass a database.

## Success Criteria

1. With a router whose `db_for_read` / `db_for_write` raise an error, `migrate` against a named database completes without calling those methods during permission creation.
2. All `auth.Permission` rows, and any content types that permission creation needs, are read from and written to the named database only.
3. A regression test reproducing the issue (`db_for_read` called with empty hints during post-migrate permission creation) fails before the change and passes after it.
4. The existing multi-database, auth, and contenttypes tests still pass.
5. Running `migrate` without a database argument behaves exactly as it did before.

## Open Questions

1. Which Django version(s) did the reporter observe this on, and should the fix be backported?
2. What is the exact source of the stray read? Candidates include a content type lookup or cache access, a related-object access on a model instance, or a queryset that is not bound to `using`. This needs confirming in the code.
3. Should the scope include **all** built-in `post_migrate` handlers (for example content type creation and removal of stale content types), or only permission creation as the title says?
4. Should this guarantee also cover third-party `post_migrate` receivers? Django can only pass `using` to them; it cannot enforce that they use it. Should this be documented?
5. Is the content type cache keyed by database? Could a cached `ContentType` loaded from one database be used to create permissions in another?
6. Does `--database` have to also suppress `db_for_write` calls, or only reads? The report shows only a read, but the stated expectation covers "all DB calls."