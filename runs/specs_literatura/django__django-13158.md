## Summary

On a `ModelMultipleChoiceField` whose queryset is built with `union()`, submitting the form with no selection adds **all** objects in the queryset to the many-to-many relation. The same field built with the `|` (OR) operator adds no objects, which is the expected result. The title suggests the cause is that `QuerySet.none()` on a combined (`union()`) query returns all results instead of none. The reporter found this on Stack Overflow and is "not 100% sure it's a bug".

## Steps to reproduce

1. Define the models, form and admin from the **Code example** section. Use the `|` (OR) version of the queryset first.
2. Create `Publication` objects so that some match `id < 2` or `id > 5`.
3. In the admin, open an `Article` and submit the form with no publications selected.
4. Note that no publications are added to the article. This is correct.
5. Change the `publications` field's queryset to the `union()` version shown in the **Code example** section.
6. Open the form again. Only the matching publications are listed, which is correct.
7. Submit the form with no publications selected.
8. Note that every publication matched by the queryset has been added to the article.

## Observed behavior

- With `union()`, the form lists the correct choices.
- Submitting the form with nothing selected adds **all** objects matched by the union queryset to `Article.publications`.

## Expected behavior

Submitting the form with nothing selected should add **no** publications. This is what happens with the `|` (OR) queryset. Following the title, calling `.none()` on a combined (`union()`) queryset should return no results.

## Stack trace / error output

Not provided in the original report. No error is raised; the wrong data is saved silently.

## Test case

Not provided in the original report. A minimal check based on the report's reproduction:

1. Create `Publication` objects, some with `id < 2` and some with `id > 5`.
2. Create an `Article`.
3. Bind `ArticleForm` (union version) to that article with `publications` left empty.
4. Validate and save the form.
5. Assert that `article.publications` is empty.
   - **Expected:** empty, the same as the OR version.
   - **Observed per the report:** contains all publications matched by the union queryset.

## Code example

Setup that works correctly, using the `|` operator:

```python
class Publication(models.Model):
    pass

class Article(models.Model):
    publications = models.ManyToManyField(to=Publication, blank=True, null=True)

class ArticleForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(
        Publication.objects.filter(id__lt=2) | Publication.objects.filter(id__gt=5),
        required=False,
    )

    class Meta:
        model = Article
        fields = ["publications"]

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
```

Field definition that triggers the bug, using `union()`:

```python
publications = forms.ModelMultipleChoiceField(
    Publication.objects.filter(id__lt=2).union(
        Publication.objects.filter(id__gt=5)
    ),
    required=False,
)
```

## Version and environment

Not provided in the original report.