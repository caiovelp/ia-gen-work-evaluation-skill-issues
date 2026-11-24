# Spec: Raise an error when `distinct()` is called on a combined (union) QuerySet

## Objective

Calling `.distinct()` (with or without field names) on a QuerySet built with `.union()` currently has no effect. The ORM ignores it without any error. The user in the issue expected `distinct('name')` after `union()` to deduplicate by `name`. Instead they got all rows, and nothing told them the call was ignored.

The issue title sets the intended behaviour: **the ORM must raise an error instead of silently ignoring `distinct()` on a union queryset.** The issue body also suggests an alternative: wrap the union in a subquery (`SELECT DISTINCT ON (name) * FROM (... UNION ...)`). That alternative is a feature request and is **out of scope** here (see Open Questions).

**User:** A developer using the ORM who combines querysets and then chains `.distinct()`.

**User story:** As a developer, when I call `.distinct()` on a combined queryset, I get a clear error at call time. I should not get silently incorrect (non-deduplicated) results.

### Reproduction (from the issue)

```python
qs = Sample.objects.filter(user=self.user)
qs1 = qs.filter(name='Dub').annotate(rank=Value(0, IntegerField()))
qs2 = qs.filter(name='Sam1').annotate(rank=Value(1, IntegerField()))
qs = qs1.union(qs2)
qs = qs.order_by('name').distinct('name')  # silently ignored today
self.assertEqual(qs.count(), 2)            # fails today
```

Expected after this change: the `.distinct('name')` call raises an error. It must not return a queryset whose results ignore it.

## Assumptions

1. The project is Django. This is inferred from the `QuerySet`, `annotate`, `union`, `Value`, `IntegerField` and `distinct('field')` API in the issue.
2. The codebase already has a way to reject unsupported operations after combinators such as `union()`. It may raise an error type like `NotSupportedError` with a message of the form "Calling QuerySet.<method>() after union() is not supported." This is unverified because the repository is not visible. If the mechanism exists, `distinct()` should reuse it so the error type and wording match.
3. The behaviour applies to every combinator that produces a "combined" queryset (`union()`, `intersection()`, `difference()`), not only `union()`. The error message should name the combinator actually used.
4. Both forms are in scope: plain `distinct()` and `distinct(*fields)` (the `DISTINCT ON` form, PostgreSQL only).
5. The error is raised when `.distinct()` is called, not later when the query is evaluated.
6. Methods that are already allowed on combined querysets are unaffected. This includes `order_by()`, slicing, `count()`, `values()` and `values_list()`.
7. `union(..., all=False)` already deduplicates whole rows via SQL `UNION`. Users needing whole-row distinctness are served by that, so raising does not take away a working use case.

## Tech Stack

- Python / Django ORM. Exact versions: **unknown**.
- Database relevant to the report: PostgreSQL (`DISTINCT ON`). The fix itself is expected to be backend-agnostic.

## Commands

Not visible in the issue. All **unknown**:

- Build: unknown
- Test: unknown (e.g. the project's test runner targeting the queryset-combinator test module)
- Lint: unknown
- Dev: N/A

## Project Structure

Not visible in the issue. **Unknown**. The following are expected but unverified:

- QuerySet API implementation (where `distinct()` and `union()` are defined): unknown path
- Tests for combined/union querysets: unknown path
- Release notes / documentation for QuerySet combinators: unknown path

## Code Style

Unknown. Follow the existing conventions in the QuerySet module. Reuse the existing helper or pattern used by other methods that are disallowed after combinators (if one exists, per Assumption 2). Do not introduce a new ad-hoc check.

## Testing Strategy

- **Level:** Unit/integration tests in the existing test suite for queryset combinators (location unknown).
- **Cases to cover:**
  - `qs1.union(qs2).distinct()` raises the "not supported" error.
  - `qs1.union(qs2).distinct('name')` raises the same error. This case may need to run only on backends supporting `DISTINCT ON`, or be backend-independent if the check fires before backend dispatch.
  - The same checks apply for `intersection()` and `difference()`, subject to backend support for those combinators.
  - The error message names the combinator used (e.g. `union`).
  - Regression: existing allowed operations on combined querysets still work.
- **Coverage expectation:** unknown. At minimum, every new code path is exercised.

## Boundaries

- **Always:** Reuse the existing combinator-guard mechanism and error type. Add regression tests for the reported scenario. Run the full combinator test module before committing.
- **Ask first:** Implementing the subquery-wrapping behaviour (`SELECT DISTINCT ON ... FROM (... UNION ...)`) instead of raising. Changing behaviour for combinators other than `union()` if maintainers want a narrower change. Any change to the public error type or message format. Documentation or release-note wording.
- **Never:** Silently ignore `distinct()` on combined querysets. Change behaviour of `distinct()` on non-combined querysets. Alter SQL generation for existing supported combinator operations.

## Success Criteria

1. Calling `.distinct()` on a queryset produced by `union()` raises an error immediately. The error type is the one already used for unsupported post-combinator operations, if one exists.
2. Calling `.distinct(*fields)` on such a queryset raises the same error.
3. The error message identifies both the method (`distinct`) and the combinator (e.g. `union`). Example shape: "Calling QuerySet.distinct() after union() is not supported."
4. Criteria 1–3 also hold for `intersection()` and `difference()` (pending Open Question 2).
5. `.distinct()` on ordinary (non-combined) querysets behaves exactly as before.
6. All existing combinator tests continue to pass.
7. Documentation, or release notes if the project requires them, mention that `distinct()` is not supported on combined querysets (pending Open Question 4).

## Open Questions

1. **Raise vs. support:** The title says "should raise". The body expects a wrapped subquery with `DISTINCT ON`. Is raising the confirmed resolution, with subquery wrapping deferred to a separate feature request?
2. Should the guard apply to all combinators (`union`, `intersection`, `difference`) or only `union`?
3. Should plain `distinct()` with no fields also raise, or only `distinct(*fields)`?
4. Does this change need a release note or documentation update? It turns silently ignored code into an error, which is a behaviour change for existing users.
5. What are the repository's test commands, file locations, and the name of the existing guard helper and error type (if any)?
6. Does the reporter's `count()` expectation (2) imply any additional `count()` behaviour that should be addressed, or is raising on `distinct()` sufficient?