# Spec: `KeyTransformIsNull` with `isnull=True` must not match JSON `null` on SQLite and Oracle

## Objective

Make `__isnull=True` on a JSONField key transform behave the same on every supported database backend.

`isnull=True` should match only rows where the key is **absent**. A row where the key is present with the JSON value `null` must not match.

**Current behavior (from the issue):**

| Backend | `key__isnull=False` | `key__isnull=True` |
|---|---|---|
| MariaDB | Correct (borrows `HasKey` logic) | Correct |
| MySQL | Correct | Correct |
| PostgreSQL | Correct | Correct |
| SQLite | Correct | **Wrong**: also matches rows where the key holds JSON `null` |
| Oracle | Correct | **Wrong**: also matches rows where the key holds JSON `null` |

**Users affected:** Developers who filter `JSONField` data with `filter(<field>__<key>__isnull=True)` on SQLite or Oracle. They currently get extra rows, so results differ from the other backends.

**Acceptance criteria:**
- On every backend, `filter(value__<key>__isnull=True)` returns exactly the rows that do not contain `<key>`.
- Rows where `<key>` is present with JSON `null` are excluded from that result.
- `isnull=False` behavior is unchanged on all backends. It still mirrors `HasKey`.

## Assumptions

1. The fix belongs in the `KeyTransformIsNull` lookup, or in backend-specific SQL compilation it delegates to, for SQLite and Oracle. The issue names the lookup but not its file path, so the exact location is unknown.
2. The `isnull=True` path for MariaDB, MySQL and PostgreSQL is correct and must not change.
3. "Does not have the key" means the key is absent at that path in the JSON document. This includes rows where the whole field is SQL `NULL`, which the existing expected result `self.objs[:4] + self.objs[5:]` implies.
4. In the `test_isnull_key` fixture data, `self.objs[4]` is the only object that has key `j`, and `j` holds JSON `null`. This is inferred from the expected result in the issue and not verified against the fixture.
5. Natural fix direction: express `isnull=True` as the negation of the `HasKey` condition on SQLite and Oracle. This is a direction to evaluate, not a decision.
6. No database schema, migration or public API change is needed. This is a query-generation bug fix only.

## Tech Stack

- Django ORM, `JSONField` and its key transform and lookup classes (`KeyTransform`, `KeyTransformIsNull`, `HasKey`). Versions are unknown.
- Affected backends: SQLite and Oracle. Regression coverage is also needed on MariaDB, MySQL and PostgreSQL.
- Database and library versions: unknown.

## Commands

- Build: unknown (not given in the issue).
- Test: unknown. Target the test `tests.model_fields.test_jsonfield.TestQuerying.test_isnull_key` with the project's test runner. The exact runner invocation and settings for each backend are not given.
- Lint: unknown.
- Running the tests against Oracle, MySQL, MariaDB and PostgreSQL: unknown. This needs a database settings module for each backend, which is not described.

## Project Structure

Known from the issue:
- `tests/model_fields/test_jsonfield.py`. This contains `TestQuerying.test_isnull_key`, the `NullableJSONModel` queries and the `self.objs` fixture.

Unknown:
- The source file that defines `KeyTransformIsNull` and `HasKey`.
- Any backend-specific operations or feature modules involved.

## Code Style

Follow the existing conventions in the JSONField lookup module and in `test_jsonfield.py`. No style snippet beyond the test change in the issue is available.

The test change specified by the issue is to replace this:

```python
self.assertSequenceEqual(
    NullableJSONModel.objects.filter(value__a__isnull=True),
    self.objs[:3] + self.objs[5:],
)
```

with this:

```python
self.assertSequenceEqual(
    NullableJSONModel.objects.filter(value__j__isnull=True),
    self.objs[:4] + self.objs[5:],
)
```

## Testing Strategy

- **Framework:** Django's own test suite. It uses `TestCase`-style tests in `tests/model_fields/test_jsonfield.py`.
- **Regression test:** Update the first assertion in `TestQuerying.test_isnull_key` as shown above.
  - It must **fail** on SQLite and Oracle before the fix, because `self.objs[4]` is wrongly included.
  - It must **pass** on all backends after the fix.
- **Why the old test missed the bug:** key `a` never holds JSON `null`. Key `j` does.
- **Keep the existing assertions:** Retain or extend the other assertions in `test_isnull_key`, including the `isnull=False` ones, so that `isnull=False` behavior provably does not change.
- **Optional:** Add an assertion that keeps the original `value__a__isnull=True` check, so coverage for a key whose value is not `null` is not lost. This is decided in Open Questions.
- **Backend coverage:** Run the test on SQLite (required) and on Oracle, MySQL, MariaDB and PostgreSQL wherever available.

## Boundaries

**Always:**
- Keep `isnull=False` semantics identical to `HasKey`.
- Run the JSONField test module on SQLite before considering the fix done.
- Add a regression assertion that uses a key whose value is JSON `null`.

**Ask first:**
- Changing behavior or generated SQL for MariaDB, MySQL or PostgreSQL.
- Changing the shared fixture data in `test_jsonfield.py`.
- Adding release notes or documentation changes.

**Never:**
- Change the documented semantics of `isnull=False`.
- Delete or weaken existing JSONField tests to make the new assertion pass.
- Introduce schema or migration changes.

## Success Criteria

1. `NullableJSONModel.objects.filter(value__j__isnull=True)` returns `self.objs[:4] + self.objs[5:]` on SQLite and Oracle, and on all other backends.
2. A row whose key is present with JSON `null` is never returned by `key__isnull=True` on any backend.
3. All existing `isnull=False` assertions in `test_isnull_key` still pass on all backends.
4. The rest of `tests/model_fields/test_jsonfield.py` passes on SQLite with no new failures.
5. The generated SQL for MariaDB, MySQL and PostgreSQL is unchanged, or any change is justified and approved.

## Open Questions

1. Where do `KeyTransformIsNull` and `HasKey` live, and is the SQLite/Oracle behavior implemented through backend-specific methods such as `as_sqlite` and `as_oracle`?
2. Should the test **replace** the `value__a__isnull=True` assertion as the issue says, or **add** the `value__j` assertion next to it to keep both cases covered?
3. Should nested key paths (for example `value__d__0__isnull=True`) also get a JSON-`null` regression check? Does the bug affect them too?
4. Can the fix be verified on Oracle, or is SQLite-only verification acceptable, with Oracle covered by CI?
5. Does this behavior change need a release note? It is a fix, but some users may have relied on the old SQLite/Oracle results.
6. Which test runner command and backend settings should be used? The issue does not specify them.