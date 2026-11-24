# Spec: Reject non-boolean values for the `__isnull` lookup

## Objective

The ORM's `__isnull` lookup currently accepts any value and treats it by truthiness (e.g. `filter(field__isnull=1)`, `filter(field__isnull="")`, `filter(field__isnull=None)`). This behavior is undocumented and untested. It also behaves inconsistently:

- In simple queries, truthy and falsy values seem to work like `True` and `False`.
- In queries that span relations, a non-boolean truthy value does **not** promote an INNER JOIN to a LEFT OUTER JOIN, as `True` does. The query can then silently return wrong results, because rows with a missing related object are dropped.

**Goal:** Only `True` and `False` should be valid right-hand-side values for `__isnull`. Any other value should raise a clear error, so users are not confused and the lookup behaves consistently.

**Users affected:** Developers writing ORM queries with `__isnull`, directly or through code that builds filters dynamically from request parameters, admin filters, etc.

### User stories / acceptance criteria

- As a developer, when I write `Model.objects.filter(field__isnull=True)` or `filter(field__isnull=False)`, it works exactly as it does today, including join promotion.
- As a developer, when I pass a non-boolean value (e.g. `1`, `0`, `"true"`, `""`, `None`, `[]`, an expression), I get an explicit error that tells me `__isnull` only accepts boolean values. I do not get silently wrong SQL.
- As a maintainer, this behavior is covered by tests, and the documentation says that `__isnull` accepts only booleans.

## Assumptions

1. The project is Django, and the lookup lives in the ORM's lookup implementation (an `IsNull` lookup class). The exact file and class location is **unknown** because it can't be seen from the issue.
2. The error is raised when the lookup is built, i.e. when `filter()`, `exclude()`, `Q(...)` and similar are evaluated. It is not deferred until SQL compilation or execution.
3. The error type is `ValueError`, which matches how other invalid lookup values are rejected. This is to be confirmed (see Open Questions).
4. Only actual `bool` instances (`True` and `False`) are accepted. Values such as `0`, `1`, `numpy.bool_`, and strings like `"True"` are rejected.
5. The check applies to every field type that supports `__isnull`, including relational fields and reverse relations. It applies across all filtering APIs: `filter`, `exclude`, `Q` objects, and `get`.
6. Existing correct behavior for `True` and `False` must not change, including INNER-to-OUTER join promotion.
7. Whether there is a deprecation period before the hard error is unspecified in the issue. This spec targets the end state (an error), and the deprecation path is listed as an open question.

## Tech Stack

- Python and Django ORM. Supported Python and Django versions: **unknown** (not stated in the issue).
- No new dependencies.

## Commands

All commands are **unknown** because they can't be seen from the issue. They need to be filled in from the repository's contributing docs, for example:

- Test: unknown (Django's test runner invocation for the relevant test apps)
- Lint: unknown
- Docs build: unknown

## Project Structure

**Unknown.** The expected areas to touch are:

- ORM lookup implementation: where `IsNull` is defined (path unknown)
- ORM query building: where join promotion for `isnull` is decided (path unknown), as a reference only
- Tests for lookups and null queries (path unknown)
- Documentation: QuerySet field lookup reference for `isnull` and release notes (path unknown)

## Code Style

Follow the existing Django code style in the repository. Specific conventions are unknown from the issue. The error message should be consistent in tone with other ORM lookup validation errors, for example: "The QuerySet value for an isnull lookup must be True or False." The exact wording still needs to be confirmed.

## Testing Strategy

- **Framework:** the project's existing test suite (Django test framework). The exact runner command is unknown.
- **Unit and integration tests** should cover:
  - `__isnull=True` and `__isnull=False` on a local nullable field still return the correct results.
  - `__isnull=True` across a relation still promotes to an OUTER JOIN and includes rows with no related object.
  - Non-boolean values raise the chosen error. Cover at least: `1`, `0`, `"true"`, `""`, `None`, and a non-empty list/object.
  - Coverage spans `filter()`, `exclude()`, and `Q()`, on both local fields and relation traversals.
- **Regression:** the full ORM and query test suites pass, so that internal callers that may pass non-bool values (e.g. admin list filters, generic relations, internal query building) are caught.
- **Docs:** the `isnull` lookup documentation states that only booleans are accepted. The release notes record the behavior change, as backwards-incompatible or as a deprecation.

## Boundaries

- **Always:**
  - Keep `True`/`False` semantics and join promotion unchanged.
  - Add tests for both the accepted and the rejected values.
  - Update the docs and release notes.
- **Ask first:**
  - Choosing a hard error vs. a deprecation warning period.
  - The exact exception type and message.
  - Changing any internal Django call site that currently passes non-bool values to `isnull`.
- **Never:**
  - Silently coerce non-boolean values with `bool()`. This is the behavior being removed.
  - Change the generated SQL for valid boolean inputs.
  - Remove or weaken existing tests.

## Success Criteria

1. `Model.objects.filter(<field>__isnull=X)` raises an explicit error for every `X` that is not `True` or `False`. The same holds for `exclude()` and `Q()`, on local fields and across relations.
2. `__isnull=True` and `__isnull=False` give the same SQL and the same results as before the change, including OUTER JOIN promotion for `True` across relations.
3. New tests cover cases 1 and 2. The existing test suite passes.
4. The `isnull` lookup documentation states that only boolean values are allowed. The release notes describe the change.
5. No internal Django code path triggers the new error during the full test suite.

## Open Questions

1. **Deprecation vs. immediate error:** Should non-boolean values first emit a deprecation warning for one or more releases, then become an error? Or should they raise immediately? Which target version applies?
2. **Exception type:** Should it be `ValueError`, `TypeError`, or `FieldError`? What exact message wording should be used?
3. **Strictness:** Should bool-like values be accepted, such as `0`/`1` and `numpy.bool_`? The assumption is no.
4. **Expressions:** Should expressions that resolve to a boolean be allowed as the right-hand side of `__isnull`, or only literal Python booleans?
5. **Internal callers:** Do any Django components pass non-bool values to `__isnull`, for example admin `list_filter` values parsed from query strings such as `"1"`/`"0"`? If so, should they convert to bool before building the lookup?
6. **Where to validate:** Should validation happen when the lookup is constructed, or during query building? This affects whether the error appears at `filter()` time or at evaluation time.
7. **Repository details:** What are the test, lint, and docs commands, the file locations, and the supported versions? None of these are visible from the issue.