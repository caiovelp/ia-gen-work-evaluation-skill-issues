## Summary

Accessing or rendering a formset's `empty_form` raises a `KeyError` when `empty_permitted` is passed in `form_kwargs`. This happens with both `form_kwargs={'empty_permitted': True}` and `form_kwargs={'empty_permitted': False}`.

## Steps to reproduce

1. Define a model `MyModel` with a field `a_field`.
2. Create a model formset with `modelformset_factory(MyModel, fields=['a_field'])`.
3. Instantiate the formset with `queryset=MyModel.objects.none()` and `form_kwargs={'empty_permitted': True}`. The same failure occurs with `{'empty_permitted': False}`.
4. Pass the formset to a template that renders `{{ formset.empty_form }}`.
5. Request the view (for example, `GET /test`).

## Observed behavior

A `KeyError` is raised when the template renders `formset.empty_form`.

## Expected behavior

`empty_permitted` should be ignored for `formset.empty_form`, and the template should render without error. `empty_form` is not meant to receive data and is never validated, so `empty_permitted` has no meaning for it.

## Stack trace / error output

Not provided in the original report. The report only states that a `KeyError` occurs.

## Test case

This minimal test is derived from the reproduction snippet in the report. It assumes the reporter's model `MyModel` with field `a_field`.

```python
from django.forms import modelformset_factory
from django.test import TestCase

from .models import MyModel


class EmptyFormEmptyPermittedTests(TestCase):
    def test_empty_form_with_empty_permitted_in_form_kwargs(self):
        ff = modelformset_factory(MyModel, fields=['a_field'])
        for value in (True, False):
            with self.subTest(empty_permitted=value):
                formset = ff(
                    queryset=MyModel.objects.none(),
                    form_kwargs={'empty_permitted': value},
                )
                # Currently raises KeyError; expected to succeed.
                str(formset.empty_form)
```

## Code example

This is the reporter's original code. The `modelformset_factory` import (`from django.forms import modelformset_factory`) was not shown in the original snippet.

```python
# views.py
from django.shortcuts import render
from .models import MyModel

def test_view(request):
    context = {}
    ff = modelformset_factory(MyModel, fields=['a_field'])
    context['formset'] = ff(
        queryset=MyModel.objects.none(),
        form_kwargs={'empty_permitted': True}  # or form_kwargs={'empty_permitted': False}
    )
    return render(request, 'my_app/my_model_formset.html', context)
```

```python
# urls.py
from django.urls import path, include
from .views import test_view

urlpatterns = [
    path('test', test_view)
]
```

```django
{# my_model_formset.html #}
{% extends "my_app/base.html" %}
{% block content %}
<form id="my-form" method="post">
  {% csrf_token %}
  {{ formset }}
  <input type="submit" value="Save">
</form>
{{ formset.empty_form }}
{% endblock %}
```

## Version and environment

Not provided in the original report.