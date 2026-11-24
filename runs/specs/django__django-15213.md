# Spec: ExpressionWrapper with negated empty `pk__in` Q (`~Q(pk__in=[])`) produces invalid SQL

## Objective

Make `ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField())` compile to valid SQL that evaluates to **true** for every row. It is used in `QuerySet.annotate()`.

**Background (from the issue):**

The non-negated form already works:

```python
queryset.annotate(
    foo=ExpressionWrapper(Q(pk__in=[]), output_field=BooleanField())
).values("foo").query
# SELECT 0 AS "foo" FROM "table"
```

The negated form produces invalid SQL. The selected expression is missing:

```python
queryset.annotate(
    foo=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField())
).values("foo").query
# SELECT  AS "foo" FROM "table"
```

**Who is affected:** Developers who build or reduce Q objects programmatically (see ticket #32554) and wrap the result in `ExpressionWrapper` for annotation. Reduction can legitimately produce an always-false condition, and its negation, an always-true condition.

**User story:** As a developer who annotates a queryset with a wrapped boolean Q expression, I want logically constant conditions to compile to valid constant SQL. Then my query runs no matter how my Q objects reduce.

**Semantics:**
- `Q(pk__in=[])` matches nothing, so it is always false.
- `~Q(pk__in=[])` matches everything, so it is always true.

## Assumptions

1. The project is Django (ORM). The issue does not state the version. The fix targets the current development branch.
2. The empty SQL comes from how the compiler handles a condition that "matches everything". An empty `__in` raises an empty-result signal, and negation turns it into a match-all condition with an empty SQL string. When that condition is inlined as a select expression through `ExpressionWrapper`, nothing is emitted. *This is a hypothesis about the cause, not something the issue confirms.*
3. The expected SQL for the negated case mirrors the working case: a constant true literal, such as `1`, or `TRUE` on backends that support boolean literals. Exact rendering per backend is acceptable as long as it is valid and evaluates to true.
4. The issue was shown with one backend, not stated. The fix should be backend-agnostic.
5. The non-negated behavior (`SELECT 0 AS "foo"`) is correct and must not change.
6. Fixing the annotate/select path is in scope. The same expression used elsewhere (filter, order_by, Case/When) is in scope only where it shares the same code path. See Open Questions.

## Tech Stack

- Python and Django ORM. Exact versions are **unknown**.
- Database backend(s): **unknown**. The issue output looks SQLite/PostgreSQL-style quoting.

## Commands

All **unknown**. The repository is not visible.

- Build: unknown
- Test: unknown (Django's own test runner invocation is not given in the issue)
- Lint: unknown

## Project Structure

**Unknown**. The repository is not visible. The relevant areas are presumably the ORM expression and SQL compilation layers and the expressions/annotations test suites. Exact paths are to be confirmed.

## Code Style

**Unknown** beyond following the existing project conventions. The only code visible is the reproduction in the issue (above).

## Testing Strategy

- Add regression test(s) in the existing expression/annotation test suite. The location is unknown.
- Test levels:
  - **SQL compilation:** the negated case produces a non-empty select expression for the annotation.
  - **Query execution:** evaluating the annotated queryset against the database returns `True` for every row of `~Q(pk__in=[])`. It returns `False` for every row of `Q(pk__in=[])`.
- Keep existing tests for the non-negated case passing.
- Run the tests on all backends the project's CI covers, if available. The details are unknown.

## Boundaries

- **Always:**
  - Add regression tests reproducing the exact issue examples.
  - Keep `Q(pk__in=[])` behavior unchanged.
  - Keep the fix backend-agnostic.
- **Ask first:**
  - Changing how empty/match-all conditions are represented globally, such as in WHERE-clause compilation.
  - Changing the public behavior of `filter()` or `exclude()` with empty `__in`.
  - Changing the SQL emitted for already-working cases.
- **Never:**
  - Raise errors for this now-valid usage instead of compiling it.
  - Special-case only `pk` when the problem applies to any field lookup with an empty `__in`.
  - Remove or weaken existing tests.

## Success Criteria

1. `str(qs.annotate(foo=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField())).values("foo").query)` contains a non-empty constant expression before `AS "foo"`, such as `1` or `TRUE`, and is valid SQL.
2. Executing that queryset returns `foo == True` for every row.
3. `Q(pk__in=[])` still compiles to the false constant (e.g. `SELECT 0 AS "foo"`), and executing it returns `foo == False` for every row.
4. The same holds for an empty `__in` on a non-pk field, e.g. `~Q(name__in=[])`.
5. The existing test suite passes with no changes to unrelated expected SQL.

## Open Questions

1. Which Django version(s) and database backend(s) were used to reproduce? Should the fix be backported?
2. What SQL literal is preferred for the always-true case on each backend (`1` vs `TRUE`)? Should it match the existing false rendering (`0`)?
3. Should the fix also cover other contexts where a match-all condition is used as an expression? Examples are `Case(When(~Q(pk__in=[]), ...))`, `order_by()`, `alias()`, and nested negations such as `~~Q(pk__in=[])`.
4. Should compound reductions also be covered, such as `~Q(pk__in=[]) & Q(...)` and `~Q(pk__in=[]) | Q(...)`, or only the bare negation from the issue?
5. Is ticket #32554 already resolved? Does its fix interact with this one?