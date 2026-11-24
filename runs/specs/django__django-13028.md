# Spec: Query filtering must not misread a model field named `filterable`

## Objective

**Problem.** In Django 3.0.7, filtering a queryset by a model instance raises `django.db.utils.NotSupportedError` when that instance's model has an attribute named `filterable` whose value is falsy. The traceback shows the error comes from `Query.check_filterable(value)`, called from `Query.build_filter` in `django/db/models/sql/query.py`.

The likely cause is that `check_filterable` reads a `filterable` attribute on the right-hand-side (RHS) value. That attribute is meant to flag query expressions that are not allowed in `WHERE`. A model instance with a user-defined `filterable` field (for example `BooleanField(default=False)`) is wrongly treated as a non-filterable expression.

**Reproduction (from the issue):**

```python
class ProductMetaDataType(models.Model):
    label = models.CharField(max_length=255, unique=True)
    filterable = models.BooleanField(default=False)

class ProductMetaData(models.Model):
    value = models.TextField()
    metadata_type = models.ForeignKey(ProductMetaDataType, on_delete=models.CASCADE)

ProductMetaData.objects.filter(value="Dark Vador", metadata_type=some_type_with_filterable_False)
# -> NotSupportedError: ProductMetaDataType is disallowed in the filter clause.
```

Renaming the field (e.g. to `filterable_test`) works around the problem. The reporter asks for a fix or documentation.

**Users.** Django developers whose models have a field or attribute named `filterable`. This is a plausible domain name, as in the "filterable metadata types" example.

**Desired outcome.** A user-defined attribute or field called `filterable` on a model instance (or any other plain RHS value) must not change whether that value can be used in a filter. The `NotSupportedError` guard must still work for genuine query expressions that declare `filterable = False`, such as window expressions.

## Assumptions

1. The bug is in Django core's ORM, not in the reporter's app. The traceback points to `django/db/models/sql/query.py` `check_filterable`.
2. The `filterable` attribute check is meant to apply only to query expressions (objects in the ORM expression API, e.g. those with `resolve_expression`). It is not meant for arbitrary Python values or model instances.
3. Existing behaviour for expressions with `filterable = False` (e.g. `Window`) must be preserved, including the error message format.
4. The fix should target the supported branch where the issue was reported (3.0.x) and the main development branch. Exact backport policy is unknown.
5. A code fix is preferred over only documenting the limitation, because the field name `filterable` is reasonable and the failure is surprising.
6. The same misinterpretation may affect other places where `check_filterable` is applied to RHS values, such as values nested inside expressions or lookups. All such paths are in scope.
7. Truthy values of a user `filterable` field must also be ignored. A model instance's filterability should not depend on its data.

## Tech Stack

- Python (3.8 in the reporter's environment)
- Django 3.0.7, which is where the issue was reported; the target branches are unknown
- Database backend: unknown. The bug appears backend-independent because it happens while the query is built, before SQL runs.

## Commands

All unknown. The repository is not visible.

- Build: unknown
- Test: unknown (Django's test runner invocation is not given in the issue)
- Lint: unknown

## Project Structure

Known from the traceback:

- `django/db/models/sql/query.py`: `Query.check_filterable`, `Query.build_filter`, `Query._add_q`, `Query.add_q`
- `django/db/models/query.py`: `QuerySet.filter`, `QuerySet._filter_or_exclude`
- `django/db/utils.py` (module path implied by `django.db.utils.NotSupportedError`)

Unknown: the location of the relevant regression tests (the test module and models for query/expression filtering) and the location of the docs.

## Code Style

Follow the existing Django conventions in the files touched. The repository is not visible, so no style snippet is given here.

## Testing Strategy

- Framework: Django's own test suite. The exact runner command and module are unknown.
- Required regression tests:
  - Filtering by a FK with a model instance whose model has `filterable = BooleanField(default=False)` and the instance value `False`. It must not raise and must return the matching rows.
  - The same with the instance value `True`.
  - Filtering on the `filterable` field itself (e.g. `ProductMetaDataType.objects.filter(filterable=False)`). It must behave like any other boolean field.
  - Existing tests asserting `NotSupportedError` for non-filterable expressions (e.g. a `Window` expression in `filter()`) must still pass unchanged.
- Level: ORM integration tests against the test database. A unit test on `check_filterable` is optional.

## Boundaries

- **Always:** Keep the `NotSupportedError` guard for real non-filterable expressions. Add regression tests that reproduce the issue's scenario. Run the existing query/expression test suites.
- **Ask first:** Renaming the expression-level `filterable` attribute or changing its public or documented semantics. Changing the error message. Backporting to stable branches. Adding release notes.
- **Never:** Remove the filterability check outright. Tell users to rename their fields as the only resolution. Change behaviour for expressions that legitimately declare `filterable = False`.

## Success Criteria

1. `ProductMetaData.objects.filter(value="Dark Vador", metadata_type=instance)` succeeds and returns the correct rows when `instance.filterable` is `False`.
2. Same as (1) when `instance.filterable` is `True`.
3. Filtering on a model field named `filterable` (`filter(filterable=False)` / `filter(filterable=True)`) works normally.
4. Using a query expression with `filterable = False` (e.g. a window function) in `filter()` still raises `NotSupportedError` with the existing message.
5. New regression tests cover criteria 1–3, and all existing tests pass.

## Open Questions

1. Should the fix restrict the `filterable` check to objects that are query expressions (e.g. those with `resolve_expression`)? Or should there be a stricter, Django-private marker so that user attributes can never collide?
2. Which branches should get the fix (3.0.x stable, 3.1, main)? Does this count as a regression from an earlier release, which would affect backport eligibility?
3. Are there other call sites (e.g. `exclude()`, `Q` objects, values inside `F`/`Value` wrappers, iterables in `__in` lookups) where RHS values go through the same check and need explicit tests?
4. Is a documentation note still wanted alongside the code fix, e.g. in the release notes, or a note about the expression `filterable` attribute in the expressions API docs?
5. What is the exact test runner command and target test module in the repository? This is unknown from the issue.