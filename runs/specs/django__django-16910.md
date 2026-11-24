# Spec: Fix `QuerySet.only()` combined with `select_related()` on a reverse OneToOneField relation

## Objective

Since Django 4.2, combining `select_related()` with `only()` on a reverse `OneToOneField` relation ignores the field restriction for the related model. Every column of the related model is selected, which is a regression from Django 4.1.9.

**Users:** Django developers who use `only()` to limit selected columns across a reverse one-to-one relation, usually for performance.

**Reproduction (from the issue):**

```python
class Main(models.Model):
    main_field_1 = models.CharField(blank=True, max_length=45)
    main_field_2 = models.CharField(blank=True, max_length=45)
    main_field_3 = models.CharField(blank=True, max_length=45)

class Secondary(models.Model):
    main = models.OneToOneField(Main, primary_key=True, related_name='secondary', on_delete=models.CASCADE)
    secondary_field_1 = models.CharField(blank=True, max_length=45)
    secondary_field_2 = models.CharField(blank=True, max_length=45)
    secondary_field_3 = models.CharField(blank=True, max_length=45)

Main.objects.select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')
```

**Observed on 4.2.1:** The SELECT clause includes `bugtest_secondary.secondary_field_2` and `bugtest_secondary.secondary_field_3`.

**Expected (4.1.9 behavior):**

```sql
SELECT "bugtest_main"."id", "bugtest_main"."main_field_1",
       "bugtest_secondary"."main_id", "bugtest_secondary"."secondary_field_1"
FROM "bugtest_main"
LEFT OUTER JOIN "bugtest_secondary" ON ("bugtest_main"."id" = "bugtest_secondary"."main_id")
```

**User stories:**
- As a developer, when I call `only()` with a path through a reverse one-to-one relation used in `select_related()`, only the listed related fields plus the related model's primary key are selected.
- As a developer, the deferred fields on the related instance still load lazily when I access them, as with any deferred field.

## Tech Stack

- Django ORM (the regression appears in 4.2.x and is absent in 4.1.9)
- Python version: unknown (whatever the target Django branch supports)
- Database backends: the issue shows SQLite/PostgreSQL-style quoting. The fix must not depend on the backend.

## Commands

The issue does not show any commands, so all of these are **unknown**:

- Test: unknown (Django's own test runner invocation is not shown)
- Lint/format: unknown
- Build: not applicable / unknown

## Project Structure

**Unknown.** No repository access is available.

- Location of the ORM compiler or query code that handles `only()` and `select_related()`: unknown.
- Location of tests for `defer`/`only` and `select_related` on one-to-one relations: unknown.

## Code Style

Follow the existing Django codebase conventions (not visible here). The only code available is the reproduction above.

## Testing Strategy

- **Regression test:** Using models equivalent to `Main`/`Secondary`, assert that `select_related('secondary').only('main_field_1', 'secondary__secondary_field_1')` does all of the following:
  - The generated SQL selects only the `Main` pk, `main_field_1`, the `Secondary` pk (`main_id`), and `secondary_field_1`.
  - `secondary_field_2` and `secondary_field_3` are deferred on the fetched `Secondary` instance, e.g. via `get_deferred_fields()`.
  - Accessing `main.secondary.secondary_field_1` triggers no extra query.
  - Accessing a deferred field such as `secondary_field_2` triggers a single extra query and returns the correct value.
- **Neighboring cases** that must keep working:
  - Forward `OneToOneField` with `select_related` + `only`
  - Forward `ForeignKey` with `select_related` + `only`
  - Reverse one-to-one with `defer()` instead of `only()`
  - Reverse one-to-one where `only()` names no related fields. Expected behavior is unknown; see Open Questions.
  - Multi-level paths, e.g. reverse O2O followed by a forward FK
  - `only()` chained with `select_related()` in either order
- **Test level:** ORM/query tests that inspect the emitted SQL or count queries, run against the standard test database.
- **Coverage expectations:** unknown.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep behavior backend-agnostic.
  - Preserve the related model's primary key in the SELECT clause.
- **Ask first:**
  - Changing public `QuerySet` API semantics.
  - Changing behavior for cases that are not reverse one-to-one relations.
  - Backporting decisions.
  - Adding release notes.
- **Never:**
  - Remove or weaken existing `defer`/`only`/`select_related` tests.
  - Fix this by disabling `select_related` for reverse relations.
  - Alter the generated SQL for unrelated query shapes.

## Success Criteria

1. The reproduction query produces exactly the column set shown in the 4.1.9 SQL above, ignoring column order and alias naming, which may follow existing conventions.
2. The fetched `Secondary` instances treat the unlisted fields as deferred and lazy-load them correctly when accessed.
3. All existing tests for `defer`, `only`, and `select_related` pass.
4. The new regression test covers reverse `OneToOneField` + `select_related` + `only`.

## Assumptions

1. The bug lives in Django core ORM code, not in a third-party package.
2. This is a regression introduced between 4.1.9 and 4.2, likely from a refactor of how deferred/only field masks are computed for related models. This is an assumption, not verified.
3. The `Secondary` primary key (`main_id`) must always be selected when the relation is selected, matching the 4.1.9 output.
4. The fix targets the main development branch, and may be backported to 4.2.x as a regression fix.
5. Forward relations are not affected. The issue only reports the reverse direction.

## Open Questions

1. Is the bug limited to `OneToOneField` declared with `primary_key=True`, or does it also occur with a non-pk reverse `OneToOneField`?
2. Does the same issue affect `defer()` on reverse one-to-one relations, or only `only()`?
3. When `only()` names fields on `Main` but none on `secondary`, while `select_related('secondary')` is used, what should be selected for `Secondary`: all fields, or only its pk? What did 4.1 do?
4. Are multi-table inheritance parent-to-child links, which are implicit reverse one-to-one relations, affected and in scope?
5. Should the fix be backported to the 4.2 stable branch, and does it need a release note?
6. What are the exact test commands and the test module locations in the repository? These are currently unknown.