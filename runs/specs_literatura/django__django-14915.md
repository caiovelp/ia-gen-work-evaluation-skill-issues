## Summary

After upgrading from Django 3.0 to Django 3.1, the `value` passed to a select widget's `create_option()` is a `ModelChoiceIteratorValue` object. This object is not hashable, so using it as a dict key lookup (`value in some_dict`) raises `TypeError: unhashable type: 'ModelChoiceIteratorValue'`. The same code worked in Django 3.0. Membership checks against a list still work.

## Steps to reproduce

1. Use Django 3.1. The code worked before migrating from Django 3.0.
2. Create a custom select widget that overrides `create_option()` to add custom `data-*` attributes to options.
3. In the override, define `self.show_fields` as a dict keyed by option value, for example `{1: ['first_name', 'last_name']}`.
4. Inside `create_option()`, check whether the option `value` is a key of that dict (`if value in self.show_fields:`).
5. Use the widget so that its options are rendered, for example with a model choice field.

## Observed behavior

Rendering fails with:

```
{TypeError}unhashable type: 'ModelChoiceIteratorValue'
```

The `value in self.show_fields` check (a dict lookup) raises this error. The equivalent check against a list (`value in allowed_values`, where `allowed_values = [1, 2]`) does not raise.

## Expected behavior

As in Django 3.0, `value` can be used in a dict lookup (`value in self.show_fields`) without raising. The custom `data-fields` attribute should be added to the matching options.

## Stack trace / error output

```
{TypeError}unhashable type: 'ModelChoiceIteratorValue'
```

No full stack trace was provided in the original report.

## Test case

Not provided in the original report. A minimal test case could be built from the steps above: render a select widget for model choices whose `create_option()` checks `value in {1: ['first_name', 'last_name']}`. The test should assert that no `TypeError` is raised and that the option for value `1` receives the `data-fields` attribute.

## Code example

Failing (dict lookup):

```python
def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
    context = super().create_option(name, value, label, selected, index, subindex, attrs)
    if not value:
        return context
    if value in self.show_fields:  # This is a dict {1: ['first_name', 'last_name']}
        context['attrs']['data-fields'] = json.dumps(self.show_fields[value])
```

Working (list membership):

```python
def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
    context = super().create_option(name, value, label, selected, index, subindex, attrs)
    if not value:
        return context
    if value in allowed_values:  # This is an array [1, 2]
        ...
```

## Version and environment

- Django 3.1 (fails)
- Django 3.0 (worked; this is the version the reporter migrated from)
- Python version, OS, and database: Not provided in the original report.