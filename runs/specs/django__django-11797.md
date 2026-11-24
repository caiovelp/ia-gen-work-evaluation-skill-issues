# Spec: Preserve the inner query's GROUP BY when a grouped/aggregated queryset is used as a filter value

## Assumptions

1. This is a bug in the Django ORM. The affected framework is Django, and the example uses `django.contrib.auth.models.User`.
2. The defect is version-independent at the level of this spec. The issue does not state a Django version or database backend, so both are **unknown**.
3. The issue implies the cause: when a queryset is passed as the right-hand side of a lookup such as `filter(id=<queryset>)`, Django rewrites or recomputes the inner query's grouping. This causes the explicit `GROUP BY "email"` (created by `.values('email').annotate(...)`) to be replaced by a grouping on the selected column (`U0."id"`). This is a hypothesis and has not been verified against source code.
4. The SELECT list of the subquery is also wrong. It renders `SELECT U0."id"`, but the user selected `values('m')`, so it should be `MAX(U0."id")`. This spec treats it as part of the same defect. See Open Questions.
5. The issue only demonstrates the `exact` lookup (`id=`). Other lookups that accept a queryset as RHS (`__in`, `__lt`, `__gt`, etc.) may share the code path. They are treated as in scope for verification.
6. The fix must not change SQL for subqueries that have no explicit grouping or aggregation.
7. Repository paths, commands, and code locations are not visible from the issue and are marked **unknown**.

## Objective

When a queryset that groups via `.values(<field>).annotate(<aggregate>).values(<alias>)` is used as a filter value in an outer queryset, the generated subquery must keep the inner query's original GROUP BY clause and selected expression.

**User:** Django developers who compose aggregated querysets as subquery filter values.

**Current behavior (from the issue):**

```python
a = User.objects.filter(email__isnull=True).values('email').annotate(m=Max('id')).values('m')
b = User.objects.filter(id=a[:1])
```

This produces:

```sql
... WHERE "auth_user"."id" = (SELECT U0."id" FROM "auth_user" U0
     WHERE U0."email" IS NULL GROUP BY U0."id" LIMIT 1)
```

**Expected behavior:**

```sql
... WHERE "auth_user"."id" = (SELECT MAX(U0."id") AS "m" FROM "auth_user" U0
     WHERE U0."email" IS NULL GROUP BY U0."email" LIMIT 1)
```

The exact alias rendering in the subquery is not significant. The grouping column and the selected aggregate are.

The standalone queries `a.query` and `a[:1].query` are already correct and must remain unchanged.

## Tech Stack

- Django ORM (Python). Version: **unknown**.
- Database backend: **unknown**. The issue shows SQLite/PostgreSQL-style quoting. The bug is in SQL compilation, so it is presumably backend-independent.

## Commands

- Build: **unknown** (not shown in issue)
- Test: **unknown** (Django's test runner invocation is not given in the issue)
- Lint: **unknown**

## Project Structure

**Unknown.** The issue references no files. Likely areas (unverified): the lookup RHS processing and the query/subquery compilation in the ORM.

## Code Style

**Unknown.** Follow the existing conventions of the repository. No snippet is available from the issue.

## Testing Strategy

- **Level:** ORM-level regression tests that build querysets and assert on generated SQL and/or query results. Tests should also run against the database to confirm correct rows are returned, not only correct SQL text.
- **Core regression case:** the exact example from the issue. Assert that the subquery's GROUP BY references `email`, not `id`, and that it selects `MAX(id)`.
- **Behavioral check:** use data where grouping by `email` and grouping by `id` would yield different results. The outer query must return the row matching the max `id` of the first `email` group.
- **Neighboring cases** (to guard scope):
  - The same pattern with `__in` instead of exact match.
  - The same pattern without slicing (`[:1]`), where applicable to the lookup.
  - A subquery without any aggregation or values. Its SQL must be unchanged.
  - A subquery with `.values('<field>')` and no annotation. It must keep its current behavior.
- **Framework, test locations, coverage requirements:** **unknown**.

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue's example.
  - Run the existing ORM/query test suites before considering the change done.
  - Keep `a.query` and `a[:1].query` output unchanged.
- **Ask first:**
  - Changing the public behavior of how a queryset RHS without explicit `values()` is coerced to `pk`.
  - Changing behavior for lookups other than `exact`.
  - Any change that alters generated SQL for non-grouped subqueries.
- **Never:**
  - Special-case `auth.User` or the `email` field.
  - Remove or weaken existing tests to make the change pass.
  - Mutate the user's original queryset `a` as a side effect of using it in `b`.

## Success Criteria

1. `User.objects.filter(id=a[:1])` (issue example) generates a subquery with `GROUP BY U0."email"` and **not** `GROUP BY U0."id"`.
2. The same subquery selects the aggregate `MAX(U0."id")`, not the bare column `U0."id"`.
3. Executing `b` returns the correct rows on a dataset where the two groupings would differ.
4. `print(a.query)` and `print(a[:1].query)` produce the same SQL as before the change.
5. Evaluating `b` does not mutate `a`. Re-printing `a.query` after building and evaluating `b` gives identical SQL.
6. All pre-existing tests in the ORM test suites pass.
7. Querysets used as filter values without grouping or aggregation generate the same SQL as before.

## Open Questions

1. Which Django version(s) and database backend(s) are affected, and should the fix be backported?
2. Is the wrong SELECT column (`U0."id"` instead of `MAX(U0."id")`) considered part of this bug? Or is replacing the select with the outer lookup's target column intended behavior, with only the GROUP BY being wrong?
3. Does the same defect occur with `__in` and other comparison lookups? Should they be fixed in the same change or tracked separately?
4. Should the behavior differ when the inner queryset is not sliced (`a` vs `a[:1]`)?
5. What are the exact test commands and test module locations for ORM regression tests in this repository?
6. Is there an existing ticket or regression commit this relates to? For example, did this work correctly in an earlier version, which would make it a regression?