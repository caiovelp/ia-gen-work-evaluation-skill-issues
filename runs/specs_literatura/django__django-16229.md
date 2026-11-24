## Summary
In the Django admin, when an inline form contains an `ArrayField` with a callable default (`default=list`), validation is bypassed on the second submission. If the inline fails validation and the form is resubmitted without changes, no error is shown, the inline is dismissed, and the `ArrayField` value is lost. The reporter suspects the hidden input that holds the field's initial value. The original title is "ModelForm fields with callable defaults don't correctly propagate default values."

## Steps to reproduce
1. Define the models and admin configuration shown in **Code example**. The inline form's `clean()` always raises a `ValidationError`.
2. Go to `/admin/my_app/thing/add/`.
3. Type anything into the `plop` field of the inline.
4. Submit the form.
5. Submit the form again without changing anything.

## Observed behavior
- After the first submission (step 4), the inline shows a validation error, as expected.
- After the second submission (step 5), no errors are shown. The inline is dismissed (validation is bypassed) and `plop` becomes empty.

The rendered form contains a hidden input that holds the initial value of `plop`:
```html
<input type="hidden" name="initial-relatedmodel_set-0-plop" value="test" id="initial-relatedmodel_set-0-id_relatedmodel_set-0-plop">
```

## Expected behavior
The second submission should behave like the first. The inline should still fail validation and show the error, and the value entered in `plop` should be kept. Submitting again without changes should not bypass validation or dismiss the inline.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report. A minimal scenario based on the reproduction:
1. Using the models and admin from **Code example**, POST the `Thing` add form in the admin with a value in the inline's `plop` field. Expect a validation error on the inline.
2. POST the form again without changes, including the hidden `initial-relatedmodel_set-0-plop` field as rendered in the response to step 1.
3. Assert that the inline still reports the validation error and that `plop` keeps its submitted value.

## Code example
```python
# models.py
class Thing(models.Model):
    pass

class RelatedModel(models.Model):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    plop = ArrayField(
        models.CharField(max_length=42),
        default=list,
    )
```

```python
# admin.py
class RelatedModelForm(forms.ModelForm):
    def clean(self):
        raise ValidationError("whatever")

class RelatedModelInline(admin.TabularInline):
    form = RelatedModelForm
    model = RelatedModel
    extra = 1

@admin.register(Thing)
class ThingAdmin(admin.ModelAdmin):
    inlines = [
        RelatedModelInline
    ]
```

## Version and environment
Not provided in the original report. The report uses `ArrayField` (a PostgreSQL-specific field) in a Django admin inline (`TabularInline`), but gives no Django, Python, database, or browser versions.