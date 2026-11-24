# Spec: Ordering by a relation's `_id` attname must not apply the related model's default ordering (self-referential FK)

## Objective

When a queryset is ordered by a lookup path ending in a foreign key's **attname** (for example `order_by("record__root_id")`), Django should order by the local FK column directly. It should not do either of these:

- Join to the related table.
- Expand into the related model's `Meta.ordering`.

The issue was reported on Django 2.2.10 and confirmed on 3.0.6. It shows up when the FK points to its own model (`OneModel.root → OneModel`) and that model defines `Meta.ordering = ("-id",)`.

Current behavior for `TwoModel.objects.filter(record__oneval__in=[1,2,3]).order_by("record__root_id")`:

- It adds an unnecessary `LEFT OUTER JOIN "orion_onemodel" T3 ON ("orion_onemodel"."root_id" = T3."id")`.
- It orders by `T3."id" DESC`. This is the related model's default ordering, applied instead of the requested ascending order.
- `order_by("-record__root_id")` produces `ORDER BY T3."id" ASC`. The explicit direction is combined with, and here inverts, the model's default `-id`.

Expected behavior for `order_by("record__root_id")`:

- It matches `order_by("record__root__id")` and the `annotate(root_id=F("record__root_id")).order_by("root_id")` workaround.
- It produces a single `INNER JOIN` to `orion_onemodel`.
- It orders by `ORDER BY "orion_onemodel"."root_id" ASC`, or `DESC` for the `-` prefix.

**Users:** Django ORM users who order querysets by FK attnames across relations, especially on models with self-referential FKs and a `Meta.ordering`.

### Acceptance criteria

1. `order_by("record__root_id")` orders by `"orion_onemodel"."root_id" ASC` with no extra self-join.
2. `order_by("-record__root_id")` orders by `"orion_onemodel"."root_id" DESC` with no extra self-join.
3. `order_by("record__root__id")` keeps its current correct SQL, with no regression.
4. `order_by("record__root")` keeps its documented behavior: ordering by the relation name applies the related model's default ordering. See Open Question 1.
5. The behavior is the same whether the FK targets the same model or a different model that has `Meta.ordering`.

## Assumptions

1. This is a bug in Django's ORM ordering resolution, not intended behavior. The reporter's comparison case points to this: a FK to a third model does not show the problem.
2. The root cause is in how an ordering name is resolved to a field. When the final path component is the FK attname (`root_id`), it seems to be treated as the relation itself (`root`), which triggers expansion of the related model's `Meta.ordering`. The self-referential case probably exposes this because the related model has a default ordering.
3. Ordering by the bare relation name (`record__root`) applying the related model's `Meta.ordering` is documented and intended, and must stay unchanged.
4. In the reporter's annotate example, `"zero_id"` is a transcription typo for `"root_id"` and is not a separate symptom.
5. The fix targets the current Django development branch. Backporting to 2.2.x or 3.0.x is out of scope unless maintainers request it.
6. The table prefix `orion_` comes from the reporter's app label and is not significant.

## Tech Stack

- Python and Django. The versions in the issue are 2.2.10 and 3.0.6. The target branch version is **unknown**.
- Database backend: not specified. The SQL looks backend-agnostic. Which backends the tests should run against is **unknown**.

## Commands

**Unknown.** The repository is not visible.

- Build: unknown
- Test: unknown (Django's own test runner invocation and the relevant test labels are not shown in the issue)
- Lint: unknown
- Dev: N/A

## Project Structure

**Unknown.** The repository is not visible. Areas likely involved, all unconfirmed:

- ORM SQL compilation and ordering resolution: path unknown
- Existing ordering tests that use self-referential FKs and models with `Meta.ordering`: path unknown

## Code Style

Unknown. Follow the existing conventions of the Django codebase. No snippet is available.

The test models from the issue are the minimal reproduction:

```python
class OneModel(models.Model):
    class Meta:
        ordering = ("-id",)
    id = models.BigAutoField(primary_key=True)
    root = models.ForeignKey("OneModel", on_delete=models.CASCADE, null=True)
    oneval = models.BigIntegerField(null=True)

class TwoModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    record = models.ForeignKey(OneModel, on_delete=models.CASCADE)
    twoval = models.BigIntegerField(null=True)
```

## Testing Strategy

- Framework: Django's own test suite. The exact runner command is unknown.
- Level: ORM and query tests. Two kinds of assertions are needed:
  - Assertions on generated SQL: no extra join, correct `ORDER BY` column and direction.
  - Assertions on result ordering against real data, so the fix is checked against behavior and not only SQL text.
- Required cases:
  - Self-referential FK, ascending: `order_by("record__root_id")`.
  - Self-referential FK, descending: `order_by("-record__root_id")`.
  - Equivalence with `order_by("record__root__id")`.
  - Regression guard: `order_by("record__root")` still applies `OneModel.Meta.ordering`.
  - Non-self-referential FK to a model with `Meta.ordering`, ordered by its attname: unchanged or correct.
- Coverage expectations: unknown.

## Boundaries

- **Always:**
  - Add regression tests reproducing the issue's querysets.
  - Run the existing ordering and query test suites.
  - Keep ordering by relation name (`record__root`) unchanged.
- **Ask first:**
  - Any change to the documented semantics of ordering by a relation name.
  - Any change that alters generated SQL for queries not involving FK attnames.
  - Backports to older release branches.
- **Never:**
  - Change `Meta.ordering` semantics globally.
  - Remove or weaken existing ordering tests.
  - Special-case only self-referential FKs if the root cause is attname-versus-name resolution in general.

## Success Criteria

- For the issue's models and data, `order_by("record__root_id")` returns rows sorted ascending by `OneModel.root_id`. The generated SQL contains exactly one join to `orion_onemodel` and `ORDER BY "orion_onemodel"."root_id" ASC`.
- `order_by("-record__root_id")` returns rows sorted descending by `root_id`, with `ORDER BY "orion_onemodel"."root_id" DESC` and no extra join.
- `order_by("record__root_id")` and `order_by("record__root__id")` produce equivalent SQL.
- `order_by("record__root")` still orders according to `OneModel.Meta.ordering` (`-id` on the joined row).
- The existing test suite passes.

## Open Questions

1. Should `order_by("record__root")` (relation name) keep applying the related model's `Meta.ordering`? The reporter notes it yields the same SQL as `record__root_id`. We assume yes, because this is documented behavior, but maintainers should confirm that only the attname path should change.
2. Is the double-join for the relation-name case (`record__root`) on a self-referential FK also considered a bug? Or is it the expected cost of applying the related model's default ordering?
3. When ordering by a relation name, should an explicit `-` prefix combine with the related model's default direction (`-` on `-id` giving `ASC`)? This should be confirmed as intended so it is not "fixed" by accident.
4. Which Django branches should receive the fix: main only, or backports to 3.0.x and 3.1.x?
5. What are the exact test locations and runner commands in the repository? Both are unknown.
6. Can the reporter confirm that `"zero_id"` in the annotate example is a typo for `"root_id"`?