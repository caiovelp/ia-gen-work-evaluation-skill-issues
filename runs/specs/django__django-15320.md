# Spec: Subquery.as_sql() produces valid SQL without manually setting `query.subquery`

## Assumptions

1. The project is Django. The affected classes are `django.db.models.Subquery` (an expression) and the `Query` object it wraps (`Subquery(...).query`). These names come from the issue. I have not seen the source files that define them.
2. The regression comes from the commit the issue links to. That commit appears to have changed `Subquery.as_sql()` to strip the first and last characters of the compiled inner SQL. The stripping assumes the inner query's SQL is already wrapped in parentheses. The issue does not name the commit, so its hash and contents are unknown.
3. The inner SQL gets parentheses only when `query.subquery = True` is set on the wrapped query. The reporter's experiment supports this: setting the flag fixes the output.
4. Normal ORM paths, such as `filter(x__in=Subquery(...))` and `annotate(x=Subquery(...))`, may already set `subquery = True` somewhere during resolution. If so, the bug only appears when `as_sql()` is called directly on an unresolved `Subquery`, as in the reproduction. This is unverified.
5. The reporter's proposed fix is to set `query.subquery = True` in the `Subquery` constructor. This spec records it as a candidate approach, not a requirement.
6. The fix must not change the SQL Django generates for subqueries that already work today.
7. The supported backends, Python versions and Django branch to target are unknown. The fix is assumed to be backend-agnostic, because the stripping happens before any backend-specific formatting.

## Objective

**Problem:** `Subquery(qs).as_sql(compiler, connection)` returns malformed SQL. It removes the first and last characters of the inner query instead of removing parentheses that are not there. Example from the issue:

- Expected: `('(SELECT "apps_app"."id", "apps_app"."name" FROM "apps_app")', ())`
- Actual: `('(ELECT "apps_app"."id", "apps_app"."name" FROM "apps_app)', ())`

**Who is affected:** Developers who compile a `Subquery` expression directly, for example in custom expressions, raw SQL composition, or debugging. Possibly also internal code paths that compile a `Subquery` without first marking its query as a subquery.

**What success looks like:** A freshly constructed `Subquery` compiles to a single, correctly parenthesized copy of the inner query's SQL. No manual `query.subquery = True` is needed, and all existing subquery usages produce the same SQL as before.

### Acceptance criteria

- AC1: For `q = Subquery(Model.objects.all())`, `q.as_sql(q.query.get_compiler(<alias>), connection)` returns SQL equal to `"(" + <inner SELECT SQL> + ")"`, with no characters of the inner SQL lost.
- AC2: AC1 holds without the caller setting `q.query.subquery` manually.
- AC3: If the caller does set `q.query.subquery = True` manually, the output is unchanged: still correct, and not double-wrapped (`((...))`).
- AC4: Params returned by `as_sql()` are unchanged by the fix and still match the inner query's params.
- AC5: `str(q.query)` for the inner query keeps its current output: unwrapped `SELECT ...`, as shown in the issue.
- AC6: Existing subquery usages produce SQL identical to before the fix. This covers `__in` lookups, annotations, `Exists`, and `OuterRef` correlated subqueries.
- AC7: Constructing a `Subquery` does not mutate the caller's original QuerySet or Query. Whether the constructor currently clones is unknown; see Open Questions.

## Tech Stack

- Python + Django ORM. Versions are unknown; the issue does not state the target branch.
- The DB backend in the reproduction is unknown. The quoting style (`"apps_app"`) suggests SQLite or PostgreSQL.

## Commands

All unknown, because the repository is not visible.

- Build: unknown (not applicable / unknown)
- Test: unknown. Django's own test runner invocation is not shown in the issue.
- Lint: unknown
- Dev: not applicable

## Project Structure

Unknown. Relevant locations to confirm:

- The module defining `Subquery`: unknown, presumably the ORM expressions module.
- The module defining `Query` and its `subquery` attribute / SQL compilation: unknown.
- The test suite location for expression / subquery tests: unknown.

## Code Style

Unknown. Follow the existing conventions of the Django codebase in the touched modules. No code snippet is available from the issue other than the reproduction:

```python
from django.db import connection
q = Subquery(App.objects.all())
q.as_sql(q.query.get_compiler('default'), connection)
# currently: ('(ELECT "apps_app"."id", "apps_app"."name" FROM "apps_app)', ())
```

## Testing Strategy

- Framework: Django's own test suite. The runner command and test locations are unknown.
- **Regression test (required):** Build a `Subquery` from a simple queryset, call `as_sql()` with a compiler and connection, and assert that the result starts with `(SELECT`, ends with `)`, and equals `"(" + str-compiled inner SQL + ")"`. This covers AC1, AC2 and AC4.
- **Idempotence test:** Repeat with `query.subquery = True` set manually and assert identical output (AC3).
- **Non-regression:** Run existing expression, subquery, `Exists`, `OuterRef` and lookup tests unchanged (AC6).
- **Isolation test:** Assert that the original queryset's query is not flagged or altered after wrapping it in `Subquery` (AC7).
- Tests should be backend-agnostic and assert structure rather than exact quoting, unless the suite already pins a backend.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue before changing behavior.
  - Keep the generated SQL for already-working subquery paths byte-identical.
  - Run the full expressions/queries test areas before considering the fix done.
- **Ask first:**
  - Changing `as_sql()` stripping logic rather than, or in addition to, setting the flag in the constructor.
  - Changing the semantics or default of `Query.subquery` globally.
  - Any change to public API signatures of `Subquery` or `Query`.
- **Never:**
  - Revert the referenced commit wholesale without understanding what it fixed.
  - Change `str(queryset.query)` output.
  - Mutate the user's original QuerySet/Query as a side effect of building a `Subquery`.

## Success Criteria

1. The issue's reproduction, run without the manual `q.query.subquery = True` line, prints `('(SELECT "apps_app"."id", "apps_app"."name" FROM "apps_app")', ())`, or the equivalent for the test model.
2. AC1–AC7 are each covered by at least one automated test, and all tests pass.
3. The existing test suite passes with no changes to expected SQL in existing tests.

## Open Questions

1. Which commit introduced the regression, and what problem was it solving? This is needed to ensure the fix doesn't reintroduce that problem.
2. Which approach is preferred? Options:
   - (a) set `query.subquery = True` in `Subquery.__init__`, as the reporter proposes;
   - (b) make `as_sql()` strip parentheses only if they are present;
   - (c) have `as_sql()` set or force the flag on a clone at compile time.
3. Does `Subquery.__init__` already clone the incoming query? If not, would setting `subquery = True` in the constructor leak into the user's original queryset?
4. Does any code path rely on `Subquery.query.subquery` being `False` after construction, for example `Exists` subclasses or pickling/`deconstruct` of expressions?
5. Which Django branch(es) should receive the fix? Is it a release blocker or a backport candidate for the version containing the regressing commit?
6. Are there other expression classes that wrap a query and use the same strip-first-and-last-character pattern, and should they be covered in the same change?
7. What are the exact test command and test file locations in the repository?