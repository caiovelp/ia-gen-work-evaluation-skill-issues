# Spec: Return primary keys from `QuerySet.bulk_create()` when `update_conflicts=True`

## Assumptions

1. Only one capability is in scope: returning generated values (at least primary keys) from `bulk_create()` when `update_conflicts=True`. No capability map is needed.
2. `ignore_conflicts=True` stays as it is. Ignored rows produce no `RETURNING` row on PostgreSQL, so the returned rows can't be matched to the input objects. That case is out of scope.
3. The issue's claim is taken as given: on PostgreSQL, `INSERT ... ON CONFLICT (...) DO UPDATE ... RETURNING <pk>` is valid and returns one row per input row, whether the row was inserted or updated.
4. With `DO UPDATE`, PostgreSQL returns the rows in the same order as the input `VALUES`, so returned PKs can be assigned to objects by position. This matches how `bulk_create()` assigns PKs today without conflict handling. It needs confirming (see Open Questions).
5. The change is limited to backends that support both `RETURNING` on bulk insert and the conflict-update syntax. Backends without `RETURNING` support (assumed to include MySQL) keep their current behaviour, with no error and no PKs set.
6. The change is scoped to the existing returning-fields mechanism. The issue says it is stripped at one place in the source, but the link target is not visible here, so the exact location is unknown. Any field the mechanism already returns (e.g. other `db_returning` fields) should follow the same rule as the PK.
7. The public API is unchanged. There are no new parameters, and the signature and arguments of `bulk_create()` stay the same.
8. The fix is behavioural, not opt-in. Callers who used `update_conflicts=True` before will now get PKs set on their objects.

## Objective

**What:** When `QuerySet.bulk_create()` is called with `update_conflicts=True` (plus `update_fields` and `unique_fields`) on a backend that supports it, the generated SQL should include the `RETURNING` clause. The returned primary keys should then be set on the model instances passed in and returned, just as they are for a plain `bulk_create()`.

**Why:** `bulk_create(update_conflicts=True, ...)` is used as a bulk upsert. Today the objects come back without PKs, whether each row was inserted or updated. Callers then need a second query to find the IDs, which costs time and invites race conditions.

**Who:** Django ORM users who bulk upsert, primarily on PostgreSQL.

**User story:**
> As a developer calling
> `MyModel.objects.bulk_create(objs, update_conflicts=True, update_fields=[...], unique_fields=[...])`,
> I want each object in the result to have its `pk` set (the existing row's PK if it conflicted, the new PK if it was inserted), so I can use the objects right away without re-querying.

**Current behaviour (from issue):**
```sql
INSERT INTO "my_model" (...)
VALUES (...)
    ON CONFLICT(...) DO UPDATE ...
-- no RETURNING clause
```

**Desired behaviour (supported backends):**
```sql
INSERT INTO "my_model" (...)
VALUES (...)
    ON CONFLICT(...) DO UPDATE ...
    RETURNING "my_model"."id"
```

## Tech Stack

- Django ORM (`QuerySet.bulk_create`). The exact Django version / target branch is **unknown**.
- PostgreSQL is the backend confirmed in the issue. Support on other backends is **unknown** (see Open Questions).
- Python version: **unknown**.

## Commands

All commands are **unknown**: the repository is not visible and the issue gives none.

- Build: unknown (likely none; pure Python)
- Test: unknown (Django's own test runner invocation and settings for a PostgreSQL run are not given)
- Lint: unknown
- Docs build: unknown

## Project Structure

**Unknown.** The issue links to the place where `returning_fields` is removed but does not show the file path.

Areas likely affected, by concept only (paths unknown):

- The `bulk_create` implementation in the QuerySet layer, where the decision to drop returning fields is made.
- Database backend feature flags describing whether a backend can return rows from bulk inserts and supports conflict-update.
- The `bulk_create` reference documentation, which currently says PKs are not set when conflict handling is enabled.
- Release notes for the target version.
- The existing `bulk_create` test suite.

## Code Style

Unknown beyond the conventions of the Django codebase, which is not visible here.

- Follow the existing style of the surrounding ORM code.
- Gate behaviour on backend feature flags, not on vendor-name checks.
- No snippet is provided because the source is not visible.

## Testing Strategy

- **Framework:** Django's own test suite. The runner command is unknown.
- **Level:** Integration tests against a real database. Tests needing `RETURNING` support should be skipped on backends that lack it, using the existing feature-flag skip mechanism (exact name unknown).
- **Cases to cover:**
  1. **All inserts:** with `update_conflicts=True` and no conflicts, every returned object has a non-null `pk` matching the database.
  2. **All conflicts:** with every row conflicting on `unique_fields`, every returned object has the `pk` of the existing row, and the `update_fields` were updated.
  3. **Mixed batch:** with some rows inserted and some updated, each object's `pk` matches its database row, matched by unique field value, not just by being non-null.
  4. **Order / mapping:** the PKs are assigned to the correct objects (object *i* gets the PK of the row for input *i*).
  5. **Batching:** with `batch_size` smaller than the number of objects, PKs are set correctly across all batches.
  6. **`ignore_conflicts=True` unchanged:** PKs are still not set, and the SQL has no `RETURNING`.
  7. **Unsupported backends unchanged:** no error, PKs not set. This applies to backends with conflict-update support but no `RETURNING` support.
  8. **Instance state:** the returned objects have the same `_state` (e.g. `adding`, `db`) as after a normal `bulk_create` that returns PKs. Exact expected values are to be confirmed against current behaviour.
- **Coverage:** every new branch in the decision to keep or drop returning fields is exercised by at least one test.

## Boundaries

- **Always:**
  - Keep `ignore_conflicts=True` behaviour unchanged.
  - Gate the new behaviour on backend capability flags.
  - Update the `bulk_create` documentation and release notes with the code.
  - Run the full `bulk_create` test suite on PostgreSQL and at least one backend without `RETURNING` support.
- **Ask first:**
  - Adding a new backend feature flag rather than reusing existing ones.
  - Enabling the behaviour on backends other than PostgreSQL.
  - Changing the public signature of `bulk_create()`.
  - Returning extra information, such as whether each row was inserted or updated.
- **Never:**
  - Return PKs for `ignore_conflicts=True`, since rows could be mismatched.
  - Assign PKs to objects in a way that could silently mismatch rows.
  - Remove or weaken existing `bulk_create` tests.
  - Emit `RETURNING` on a backend whose SQL grammar does not support it.

## Success Criteria

1. On PostgreSQL, the generated SQL for `bulk_create(..., update_conflicts=True, update_fields=[...], unique_fields=[...])` includes `RETURNING` for the PK and any other fields the existing mechanism returns.
2. After that call, every object in the returned list has a `pk` equal to its database row's PK, for inserted and updated rows alike, including mixed batches and multiple batches.
3. Behaviour with `ignore_conflicts=True` is unchanged: no `RETURNING` clause and no PKs set.
4. On backends without the needed support, `update_conflicts=True` works as before: no error and no PKs set.
5. The `bulk_create` docs state which flags still prevent PKs from being set, and which backends set them with `update_conflicts=True`. A release note describes the change.
6. All new and existing `bulk_create` tests pass on every supported backend.

## Open Questions

1. **Backends:** besides PostgreSQL, which backends should get this behaviour? SQLite, MariaDB, Oracle and MySQL differ in whether they support `RETURNING` and conflict-update together. Is the existing "can return rows from bulk insert" capability enough, or is a new combined flag needed?
2. **Row order:** is it guaranteed (or tested enough) on each enabled backend that `RETURNING` rows from `ON CONFLICT DO UPDATE` come back in input order? If not, should the mapping be done another way, e.g. by unique field values?
3. **No-op updates:** can any supported conflict-update form skip a conflicting row so that it returns no row? An example would be a `WHERE` on `DO UPDATE`, if one exists now or is planned. If so, how should a row-count mismatch be handled?
4. **Other returned fields:** should all fields the returning mechanism covers (not just the PK) be set on the objects in the update case? For updated rows, should they hold the post-update values?
5. **Target version and branch:** which Django version should this land in, and is it a new feature (release notes, no backport) or a bug fix?
6. **Source location:** what is the exact file and condition the issue links to, where `returning_fields` is removed? It is not visible here.
7. **Opt-in:** should the new behaviour be unconditional on supported backends, as assumed, or does it need a deprecation or opt-in path? Some callers may depend on PKs not being set.
8. **Duplicate keys in one batch:** PostgreSQL rejects an `ON CONFLICT DO UPDATE` that touches the same row twice. Is the current error behaviour acceptable and unchanged, and should it be documented?