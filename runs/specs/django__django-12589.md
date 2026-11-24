# Spec: Unambiguous GROUP BY for Subquery annotations that collide with joined column names

## Objective

**Problem.** Django 3.0.4 on PostgreSQL 11 builds invalid SQL in this case:

- A queryset has a `Subquery` annotation whose alias matches a column name on a joined table.
- The queryset is then grouped via `.values(<alias>).annotate(<aggregate>)`.

Django 3.0 emits `GROUP BY "status"`, using the annotation alias. Here `"status"` is also a column of the joined table `test_app_ab`. PostgreSQL rejects the query with:

```
django.db.utils.ProgrammingError: column reference "status" is ambiguous
```

Django 2.2.11 handled the same queryset correctly. It emitted the full subquery expression in the GROUP BY clause:

```
GROUP BY (SELECT U0."status" FROM "test_app_ab" U0 WHERE (U0."a_id" = ("test_app_a"."id") AND U0."b_id" = 1))
```

**Users.** Django ORM users who group by `Subquery` annotations on querysets that also join other tables. This is common after `filter()` with `Q` objects across relations, or after aggregations like `Count("c")`.

**What success looks like.** The issue's queryset runs on PostgreSQL without error. It returns the grouped result that 2.2.11 returned, so the 3.0 regression is gone. Non-colliding cases keep working.

### Reproduction (from the issue)

Models:
- `A` has `bs = ManyToManyField('B', related_name="a", through="AB")`.
- `B` is empty.
- `AB` has:
  - `a = FK(A, related_name="ab_a")`
  - `b = FK(B, related_name="ab_b")`
  - `status = IntegerField()`
- `C` has:
  - `a = FK(A, null=True, blank=True, on_delete=SET_NULL, related_name="c")`
  - `status = IntegerField()`

Query:
```python
ab_query = AB.objects.filter(a=OuterRef("pk"), b=1)
filter_conditions = Q(pk=1) | Q(ab_a__b=1)
query = A.objects.filter(filter_conditions).annotate(
    status=Subquery(ab_query.values("status")),
    c_count=Count("c"),
)
answer = query.values("status").annotate(total_count=Count("status"))
```

### Acceptance criteria

1. Evaluating `answer` on PostgreSQL raises no `ProgrammingError`.
2. The generated GROUP BY clause for `answer` does not reference the bare alias `"status"`. That alias collides with `test_app_ab.status` and `test_app_c.status`, both of which are in the FROM clause via joins. Instead, the GROUP BY must reference something that resolves unambiguously, for example the full subquery expression as in 2.2.11.
3. The result rows match what Django 2.2.11 returns for the same data.
4. Grouping by a `Subquery` annotation whose alias does **not** collide with any joined column still produces correct results. Whether it is grouped by alias or by expression is an open question.
5. Existing GROUP BY behaviour for plain field references and non-subquery annotations is unchanged. The existing test suite must pass.
6. The new behaviour is covered by a regression test that fails on the current code and passes after the change.

## Assumptions

1. The regression comes from a Django 3.0 change in how GROUP BY is compiled for annotations. Specifically, 3.0 appears to reference annotation aliases instead of repeating the expression. This is inferred from the two SQL outputs and is not confirmed in source.
2. The target fix branch is the Django 3.0.x line (a regression fix), plus the main development branch. Not confirmed.
3. The issue only demonstrates PostgreSQL 11. The fix should still be correct on all backends Django supports (SQLite, MySQL, Oracle, PostgreSQL), not just PostgreSQL.
4. `_("a")` in the model definition is `gettext_lazy` and has no bearing on the bug.
5. `c_count=Count("c")` matters only because it introduces the `test_app_c` join, which brings in a second `status` column. The bug should also reproduce with only the `ab_a__b` join.
6. Repeating the full subquery expression in GROUP BY, as 2.2.11 did, is an acceptable fix. Any equivalent unambiguous form is also acceptable.
7. The fix is internal to the ORM SQL compiler/query layer. No public API changes are expected.

## Tech Stack

- Django (affected: 3.0.4; working reference: 2.2.11)
- Python: version unknown
- Database in the report: PostgreSQL 11, via `django.db.backends.postgresql`
- Driver (e.g. psycopg2) version: unknown

## Commands

Unknown. The issue gives no commands. To be confirmed:

- Test runner invocation: unknown
- Database settings for running tests against PostgreSQL: unknown
- Lint/format commands: unknown

## Project Structure

Unknown. The issue references no source files. The relevant ORM modules (query construction / SQL compiler) and the test app/location for the regression test must be identified from the repository.

## Code Style

Unknown. Follow the existing Django project conventions found in the repository. No snippets are provided in the issue beyond the reproduction above.

## Testing Strategy

**Regression test.**
- Encode the issue's model shape: a through model with a field whose name collides with an annotation alias, plus a nullable FK model with the same field name.
- Encode the issue's queryset: a `Subquery` annotation, then `.values(alias).annotate(Count(alias))`, with joins present.
- Assert that evaluation succeeds and that the aggregated results are correct.

**Backend coverage.**
- The test must pass on PostgreSQL, where the ambiguity error occurs.
- It must also pass on the other supported backends, which may resolve aliases differently.

**SQL-shape assertion (optional).**
- Possibly assert that the GROUP BY does not use a bare colliding alias.
- Prefer behavioural assertions over brittle SQL string matching. See Open Questions.

**Non-regression tests.**
- Group by a `Subquery` annotation without collisions.
- Group by regular fields and by non-subquery annotations.
- Run the full existing aggregation/expressions/annotations test suites.

Exact test framework invocation and file locations: unknown.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue.
  - Run the existing ORM test suites, on PostgreSQL at minimum.
  - Keep generated SQL valid on all supported backends.
- **Ask first:**
  - Changing GROUP BY semantics for cases beyond colliding `Subquery` aliases (e.g. switching all annotations back to expression-based grouping).
  - Any backend-specific branching.
  - Changing public API or documented behaviour.
  - Adding release notes for the 3.0.x branch.
- **Never:**
  - Remove or weaken existing tests to make the suite pass.
  - Fix only by special-casing the field name `status`.
  - Introduce a fix that only works on PostgreSQL while breaking other backends.

## Success Criteria

- The issue's exact queryset executes on PostgreSQL 11 without `column reference "status" is ambiguous`.
- Its results match Django 2.2.11's results for the same fixture data.
- A new regression test fails before the fix and passes after it, on PostgreSQL and the other backends in CI.
- All pre-existing tests pass.
- No change in generated SQL or results for GROUP BY queries that don't involve alias/column name collisions, unless explicitly approved (see Open Questions).

## Open Questions

1. **Scope of the fix.** Should the compiler (a) always group by the full expression for `Subquery` annotations, (b) group by the expression only when the alias collides with a column name of any table in the FROM clause, or (c) restore 2.2 behaviour for all annotations? Option (b) preserves the 3.0 optimisation but requires collision detection.
2. **Which versions get the fix?** Is this treated as a 3.0.x regression backport, or only on the main branch?
3. Does the problem also affect other expression types used as annotations with colliding aliases (e.g. `Func`, `Case`, `ExpressionWrapper`), or only `Subquery`? Should those be in scope?
4. Does the ambiguity also reproduce on SQLite, MySQL, or Oracle, or is it PostgreSQL-specific? This decides whether the test needs backend-specific expectations.
5. Is asserting on generated SQL text acceptable in tests, or should tests be purely behavioural?
6. Where should the regression models and tests live (existing test app vs. new models)? Unknown without repository access.
7. Is a minimal reproduction without `c_count=Count("c")` sufficient for the test, or should the test mirror the issue exactly?
8. Are there performance concerns with repeating subquery expressions in GROUP BY? Should that be evaluated?