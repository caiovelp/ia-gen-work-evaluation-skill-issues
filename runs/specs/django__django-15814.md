# Spec: Fix `QuerySet.only()` after `select_related()` crashing on proxy-model relations

## Objective

Fix a crash in the Django ORM. It happens when a queryset follows a relation to a **proxy model** with `select_related()` and then limits the loaded fields on that related model with `only()`.

**Reported reproduction (Django 4.0.5, Python 3.10, Windows 10):**

```python
class CustomModel(models.Model):
    name = models.CharField(max_length=16)

class ProxyCustomModel(CustomModel):
    class Meta:
        proxy = True

class AnotherModel(models.Model):
    custom = models.ForeignKey(
        ProxyCustomModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

list(AnotherModel.objects.select_related("custom").only("custom__name").all())
```

**Observed:** `ValueError: 'id' is not in list`. It is raised from `RelatedPopulator.__init__` in `django/db/models/query.py` at `self.pk_idx = self.init_list.index(self.model_cls._meta.pk.attname)`. The related model's primary key is missing from the selected columns.

**Expected:**
- The query runs without error.
- Each `AnotherModel` instance has `custom` populated as a `ProxyCustomModel` instance.
- `custom.name` is loaded.
- Other fields of the related model stay deferred.
- The related model's primary key is always included.

**Reporter's hint:** in `django/db/models/sql/query.py`, around line 745 (in 4.0.5), the code reads `opts = cur_model._meta`. Changing it to `opts = cur_model._meta.concrete_model._meta` makes the query work. This points to the deferred-loading / field-mask logic, which resolves field names against the proxy's options instead of the concrete model's. As a result, the mask for the related model does not include its pk.

**Users:** Django developers who optimise queries with `select_related()` and `only()`/`defer()` over relations that point at proxy models.

**Success looks like:** proxy-targeted relations behave exactly like concrete-targeted relations under `only()`/`defer()` combined with `select_related()`.

## Assumptions

1. The bug is in Django core ORM code. It is not in user code, and the reporter's model definitions are valid.
2. The root cause is the field-mask computation for deferred loading in `django/db/models/sql/query.py`. It uses a proxy model's `_meta` where the concrete model's `_meta` is needed. The reporter's line number refers to 4.0.5, and the current location on the target branch may differ.
3. The correct behaviour is to treat a proxy model as its concrete model for column selection, while still instantiating the proxy class for the related object.
4. The fix should target the main development branch, with possible backport per Django's backport policy. This depends on whether the issue is a regression; see Open Questions.
5. The bug is not specific to the database backend or the OS.
6. `defer()` is likely affected through the same code path, and the fix should cover it.

## Tech Stack

- Python; Django ORM (`django/db/models/query.py`, `django/db/models/sql/query.py`)
- Reported on Django 4.0.5 / Python 3.10. The supported Python versions on the target branch are **unknown**.

## Commands

The exact commands are **unknown** because the repository was not inspected. They are presumably Django's standard test runner from the `tests/` directory, for example `./runtests.py <app_label>`, but the exact invocation, settings, and flags have not been verified.

- Build: unknown / not applicable
- Test: unknown (likely Django's `tests/runtests.py`; to be confirmed)
- Lint: unknown (Django uses flake8/black/isort; configuration not verified)
- Dev: not applicable

## Project Structure

Known from the traceback and the issue:

```
django/db/models/query.py       → QuerySet, RelatedPopulator, get_related_populators (where the error surfaces)
django/db/models/sql/query.py   → SQL Query construction, including deferred-field mask logic (suspected root cause)
```

The location of the regression tests is **unknown**. Candidate test apps covering proxy models, `select_related`, and `defer`/`only` are expected to exist under `tests/`, but their names are not verified.

## Code Style

Follow existing Django code style in the touched modules. The only code shown in the issue is the reporter's one-line change:

```python
# current (reported, line ~745 in 4.0.5)
opts = cur_model._meta
# reporter's suggestion
opts = cur_model._meta.concrete_model._meta
```

Prefer the smallest change that resolves the concrete model consistently. Avoid broad refactors of the deferred-loading machinery.

## Testing Strategy

- **Level:** ORM regression tests run against the test database. No mocking.
- **Required regression test:** with models equivalent to the reproduction (concrete model, proxy subclass, FK pointing at the proxy), `select_related("<fk>").only("<fk>__<field>")` must:
  - evaluate without error;
  - return related instances of the proxy class;
  - have the requested field loaded and the others deferred.
- **Additional cases to cover:**
  - The same query with `defer()` instead of `only()`.
  - A reverse or nested relation through a proxy, if supported by the same code path.
  - A proxy of a proxy, if feasible.
  - Asserting the deferred field set via `get_deferred_fields()`, and/or the number of queries, so that columns are not silently over-fetched.
- **Non-regression:** the existing test suites for proxy models, `select_related`, and deferred loading must pass unchanged.
- Coverage targets: unknown; follow project norms.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after.
  - Run the related existing test suites.
  - Keep the related object's class as the proxy class.
  - Keep the change minimal and local to the mask/opts resolution.
- **Ask first:**
  - Changing public `QuerySet` API behaviour.
  - Refactoring deferred-loading internals beyond the faulty lookup.
  - Altering `RelatedPopulator` to tolerate a missing pk instead of fixing the mask.
  - Adding release notes or backport targets.
- **Never:**
  - Mask the error, for example by catching `ValueError`.
  - Always select all columns, which would defeat `only()`.
  - Change the semantics of proxy models.
  - Modify unrelated tests.

## Success Criteria

1. `AnotherModel.objects.select_related("custom").only("custom__name")` evaluates without raising.
2. Returned `custom` objects are `ProxyCustomModel` instances with correct `pk` and `name`. Fields not listed in `only()` remain deferred.
3. The equivalent `defer()` query over a proxy-targeted relation also works correctly.
4. Generated SQL selects the related pk and the requested fields, and not the deferred columns.
5. A new regression test reproduces the original crash without the fix and passes with it.
6. Existing ORM tests for proxies, `select_related`, and deferred loading pass.

## Open Questions

1. Which branch or versions should the fix target? Is this a regression from an earlier Django release, which affects backport eligibility?
2. Does the bug still reproduce on the current main branch? The code at the reported line may have been restructured since 4.0.5.
3. Are other places in the deferred-loading or `select_related` code also using proxy `_meta` where the concrete `_meta` is required, so that they should be fixed together?
4. Should a proxy of a proxy and multi-table inheritance combined with a proxy be covered in this fix, or tracked separately?
5. In which existing test app(s) should the regression test live, and can existing proxy models there be reused instead of adding new ones?
6. What are the exact test, lint, and formatting commands for the target branch?
7. Is a release note required for this fix?