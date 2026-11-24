# Spec: Preserve "-pk" Descending Direction in Inherited Model Ordering

## Objective

When a parent model declares `Meta.ordering = ["-pk"]`, a multi-table-inherited child model's default queryset must order by the parent's primary key **descending**. It currently orders ascending, which drops the `-` direction prefix.

**Observed behavior (from the issue):**

```python
from django.db import models

class Parent(models.Model):
    class Meta:
        ordering = ["-pk"]

class Child(Parent):
    pass
```

```
>>> print(Child.objects.all().query)
SELECT "myapp_parent"."id", "myapp_child"."parent_ptr_id" FROM "myapp_child" INNER JOIN "myapp_parent" ON ("myapp_child"."parent_ptr_id" = "myapp_parent"."id") ORDER BY "myapp_parent"."id" ASC
```

**Expected behavior:** `... ORDER BY "myapp_parent"."id" DESC`

**Users affected:** Django developers who use multi-table inheritance and rely on an inherited `Meta.ordering` that contains `"-pk"`, or possibly any descending term.

**User story:** As a developer, when I declare `ordering = ["-pk"]` on a parent model, I expect `Child.objects.all()` to return rows newest-first by primary key, the same as `Parent.objects.all()` does.

## Assumptions

1. The project is the Django framework itself. The bug is in the ORM's SQL compilation of ordering, not in user code.
2. "Inherited" means multi-table (concrete) inheritance. `Child` has an implicit `parent_ptr` OneToOneField to `Parent`, and it inherits `Meta.ordering` because it does not define its own `Meta`.
3. `Child` inherits `ordering` from `Parent` unchanged. The defect is that the direction is lost when `pk` resolves through the parent link to `parent_ptr` and then to `Parent.id`. The defect does not occur at inheritance time.
4. The defect likely shows up when an ordering term on a relation or pk resolves to a related model whose default ordering is then expanded, and the original descending direction is not passed through. This is a hypothesis to verify, not a confirmed root cause.
5. Expected SQL is `ORDER BY "<parent_table>"."id" DESC`. No extra or duplicate ordering columns should appear.
6. All supported database backends are affected the same way, because ordering is compiled in backend-agnostic ORM code.
7. The fix targets the Django development branch. The issue does not state a Django version.

## Tech Stack

- Language: Python (version unknown, whatever the target Django branch supports)
- Framework: Django ORM (version or branch unknown)
- Database backends: SQLite is shown in the example's quoting style; all backends should be covered
- Dependencies: no new dependencies expected

## Commands

The exact commands for this repository are **unknown**. The repository is not visible.

- Build: unknown (likely not applicable for a pure-Python change)
- Test: unknown. Likely Django's own test runner under `tests/`, but the exact invocation is unverified.
- Lint: unknown
- Dev: not applicable

## Project Structure

Unknown. The repository is not visible. To confirm:

- Where the ORM ordering resolution and SQL compilation code lives
- Where the existing tests live for model inheritance and for `Meta.ordering` and `order_by`

## Code Style

Unknown beyond the issue snippet. Follow the existing Django project conventions: PEP 8 and the project's established linting and formatting configuration. Exact tools are unknown.

## Testing Strategy

- **Level:** Regression tests that inspect the generated query and the ordering of actual results.
- **Required test cases:**
  1. `Child.objects.all()` with `Parent.Meta.ordering = ["-pk"]` produces descending order by the parent's pk.
     - Assert the result order with at least 3 rows created in a known pk sequence.
     - Optionally assert that `DESC` appears in the compiled SQL.
  2. A control case: `Parent.objects.all()` with the same ordering is still descending (no regression).
  3. An ascending `["pk"]` inherited ordering still produces ascending order.
  4. Possibly related variants, to confirm scope:
     - `["-id"]` on the parent
     - Explicit `Child.objects.order_by("-pk")`
     - `Child.objects.order_by("-parent_ptr")`
     - A grandchild in a multi-level inheritance chain
     - A descending inherited ordering on a non-pk field
- **Location:** unknown. Likely the existing model-inheritance or ordering test modules; to be confirmed.
- **Coverage:** every new branch in the changed ordering-resolution logic must be exercised by at least one test.
- The full existing ORM test suite (ordering, inheritance, queries) must pass unchanged.

## Boundaries

- **Always:**
  - Add a failing regression test that reproduces the issue before changing behavior.
  - Run the existing ordering, inheritance and queries test suites.
  - Keep the fix minimal and backend-agnostic.
- **Ask first:**
  - Changing public behavior of explicit `order_by()` with relation fields, beyond restoring the correct direction.
  - Changing how `Meta.ordering` is inherited.
  - Adding release notes or docs changes.
  - Touching backend-specific compilers.
- **Never:**
  - Modify or delete existing tests to make them pass.
  - Special-case the literal string `"-pk"` as a workaround instead of fixing direction propagation.
  - Introduce new dependencies.

## Success Criteria

- [ ] With `Parent.Meta.ordering = ["-pk"]`, `str(Child.objects.all().query)` contains `ORDER BY "<parent_table>"."id" DESC`.
- [ ] With 3+ `Child` rows, iterating `Child.objects.all()` yields them in descending pk order.
- [ ] `Parent.objects.all()` ordering is unchanged (descending).
- [ ] Inherited ascending ordering (`["pk"]`) still yields ascending order.
- [ ] Any variants confirmed in scope (see Open Questions) produce the correct direction.
- [ ] No duplicate or extra `ORDER BY` terms are introduced.
- [ ] The existing test suite passes on all backends covered by CI.

## Open Questions

1. Which Django version or branch is affected and should receive the fix? Is a backport expected?
2. Does the bug also occur with these forms?
   - `["-id"]` or another descending field on the parent
   - Explicit `Child.objects.order_by("-pk")` without `Meta.ordering`
   - `order_by("-parent_ptr")`

   This determines whether the scope is "inherited Meta.ordering" or "descending ordering through any relation/pk resolution."
3. Does it reproduce with multi-level inheritance, for example a grandchild of `Parent`?
4. Should `Child` explicitly defining `class Meta(Parent.Meta)` be covered as well?
5. Is a release note required for this fix?
6. What are the exact test commands, and which test modules should hold the regression tests?