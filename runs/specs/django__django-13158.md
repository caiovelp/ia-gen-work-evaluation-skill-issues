# Spec: `QuerySet.none()` on combined querysets must return no results

## Objective

Calling `.none()` on a queryset built with `union()` returns every row the combined query would return, instead of returning no rows. For an ordinary queryset, and for one combined with the `|` operator, `.none()` correctly returns nothing.

**Observed user impact (from the issue):**
- A `forms.ModelMultipleChoiceField` uses `Publication.objects.filter(id__lt=2).union(Publication.objects.filter(id__gt=5))` as its queryset, with `required=False`.
- The form is used through a `ModelAdmin` for a model with a `ManyToManyField` to `Publication`.
- The form is submitted with no publications selected.
- Result: **all** publications matching the union are added to the M2M relation.
- Expected result, which is what the `|` version does: **no** publications are added.

**Why this matters:** The bug silently writes data. An empty selection turns into "select everything", which causes unintended changes to relations in admin forms. Any other code that uses `.none()` as a safe empty result on a combined queryset is also affected.

**Users:**
- Developers who pass combined querysets to model forms or the admin.
- Any code that calls `.none()` on a combined queryset.

**Acceptance criteria:**
1. `qs1.union(qs2).none()` returns an empty result. This holds for iteration, `len()`, `count()`, `exists()`, and `list()`.
2. The same applies to the other set-operation combinators (`intersection()`, `difference()`), assuming they share the code path (see Open Questions).
3. Submitting the issue's `ModelMultipleChoiceField` (union queryset, `required=False`) with an empty selection adds no related objects.
4. Existing behavior of `.none()` on plain querysets and on `|`-combined querysets does not change.
5. Existing behavior of non-empty `union()` / `intersection()` / `difference()` queries does not change.

## Assumptions

1. The target codebase is Django itself (ORM `QuerySet` and `forms.ModelMultipleChoiceField`). This is not a user project.
2. `ModelMultipleChoiceField.clean()` returns `self.queryset.none()` when the value is empty and the field is not required. That is how the empty-submit path reaches `.none()`. This is inferred from the symptom and has not been verified against the source.
3. The defect is in the ORM, in how `.none()` / the empty-query state interacts with combinator queries. It is not in the forms layer, and the form code needs no change.
4. `intersection()` and `difference()` go through the same combinator mechanism as `union()`, so they likely have the same defect.
5. The fix must work on all database backends Django supports for combinator queries. No backend-specific behavior is expected.
6. The `null=True` on the `ManyToManyField` in the issue has no effect on the bug.

## Tech Stack

- Python and Django. Versions are **unknown**; the issue does not give an affected version.
- Components involved: the Django ORM (`QuerySet.none()`, `union()` / combinator queries) and Django forms (`ModelMultipleChoiceField`). The admin is only the place where the bug showed up.

## Commands

**Unknown.** The issue gives no build, test, or lint commands, and the repository is not accessible. They must be confirmed from the repository's contributor or testing documentation.

```
Build: unknown
Test:  unknown (full suite and targeted test modules for queries/combinators and model forms)
Lint:  unknown
```

## Project Structure

**Unknown.** No paths are given in the issue. The work is expected to touch:
- the ORM queryset / query-compilation code that handles `.none()` and combinators (exact location unknown)
- the existing test modules for combined querysets (location unknown)
- the existing test modules for model forms / `ModelMultipleChoiceField` (location unknown)

## Code Style

Follow the existing conventions of the codebase (unknown here, not visible). The only code in the issue shows the scenario that reproduces the bug:

```python
class Publication(models.Model):
    pass

class Article(models.Model):
    publications = models.ManyToManyField(to=Publication, blank=True, null=True)

class ArticleForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(
        Publication.objects.filter(id__lt=2).union(
            Publication.objects.filter(id__gt=5)
        ),
        required=False,
    )
    class Meta:
        model = Article
        fields = ["publications"]
```

## Testing Strategy

The framework and test locations are **unknown**. Use the project's existing test framework and put new tests next to the existing tests for combined querysets and for model forms.

**Regression tests at the ORM level (primary):**
- `union(...).none()` yields no rows.
- Check the same through every evaluation path: iteration, `count()`, `exists()`.
- Repeat for `intersection(...).none()` and `difference(...).none()`, subject to backend feature support for those operations.
- Control case: `(qs1 | qs2).none()` is empty. This already passes and must keep passing.

**Regression test at the forms level (secondary):**
- A `ModelMultipleChoiceField` with a union queryset and `required=False`, cleaned with an empty value, gives an empty queryset.
- Saving such a form adds no M2M relations.

**Regression safety:**
- All existing combinator-query and model-form tests must still pass.

Coverage targets: unknown, so follow project norms.

## Boundaries

- **Always:**
  - Reproduce the bug with a failing test before changing behavior.
  - Keep `.none()` semantics consistent across plain, `|`-combined, and combinator querysets.
  - Run the full relevant test suites before committing.
- **Ask first:**
  - Changing the public behavior of combinator querysets beyond the `.none()` case.
  - Changing `ModelMultipleChoiceField` / forms code. The fix is assumed to belong in the ORM.
  - Adding backend-specific handling.
  - Adding dependencies.
- **Never:**
  - Work around the bug only in the forms layer and leave `.none()` broken.
  - Remove or weaken existing tests.
  - Change unrelated set-operation behavior.

## Success Criteria

- [ ] A test showing that `union(...).none()` returns rows fails before the change and passes after it.
- [ ] `.none()` on `intersection()` and `difference()` querysets also returns no rows, on backends that support those operations.
- [ ] `count()` and `exists()` on a `.none()`'d combined queryset return `0` and `False`.
- [ ] Cleaning a `ModelMultipleChoiceField` with an empty value and a union queryset (`required=False`) gives no objects, and saving the form adds no relations.
- [ ] `.none()` on plain and `|`-combined querysets behaves the same as before.
- [ ] All existing combinator-query and model-form tests pass.

## Open Questions

1. Which Django version(s) are affected, and which branch should the fix target?
2. Does the defect also affect `intersection()` and `difference()`, or only `union()`? The spec assumes all three.
3. What should happen when `.none()` is called on one of the *inputs* to a combinator, e.g. `qs1.none().union(qs2)`? Is that in scope or a separate issue?
4. Should further operations on a `.none()`'d combined queryset (e.g. `order_by()`, `values()`, slicing) be covered explicitly by tests?
5. Should documentation mention `.none()` on combined querysets, or is this a pure bug fix with a release note only?
6. What are the exact test, build, and lint commands and test module locations in the repository? These are currently unknown.