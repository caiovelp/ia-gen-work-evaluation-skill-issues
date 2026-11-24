## Summary

In Django 3.0, a view function crashes with a `TypeError` when its URL pattern uses `re_path` with an optional named group. The same setup worked in Django 2.2 and earlier.

## Steps to reproduce

1. Add a URL pattern with an optional named group, `format`, to the URLconf:
   ```python
   re_path(r'^module/(?P<format>(html|json|xml))?/?$', views.modules, name='modules'),
   ```
2. Define a view that accepts `format` as an optional argument with a default value:
   ```python
   def modules(request, format='html'):
       ...
       return render(...)
   ```
3. Run the project with Django 3.0.
4. Request `/module/`, leaving out the optional `format` part.

## Observed behavior

The request fails with a `TypeError`:

```
modules() takes from 1 to 2 positional arguments but 3 were given
```

## Expected behavior

The request to `/module/` should call the view without error, with `format` falling back to its default value `'html'`. This is how it behaved up to Django 2.2.

## Stack trace / error output

```
Traceback (most recent call last):
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/exception.py", line 34, in inner
	response = get_response(request)
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/base.py", line 115, in _get_response
	response = self.process_exception_by_middleware(e, request)
 File "/l10n/venv/lib/python3.6/site-packages/django/core/handlers/base.py", line 113, in _get_response
	response = wrapped_callback(request, *callback_args, **callback_kwargs)
Exception Type: TypeError at /module/
Exception Value: modules() takes from 1 to 2 positional arguments but 3 were given
```

## Test case

This minimal test is derived from the reproduction in the report. It assumes the URLconf and view from "Code example" are active.

```python
from django.test import TestCase

class OptionalNamedGroupTests(TestCase):
    def test_optional_format_omitted(self):
        # Worked in Django 2.2; raises TypeError in Django 3.0.
        self.client.get('/module/')
```

## Code example

URLconf:
```python
urlpatterns += [
    ...
    re_path(r'^module/(?P<format>(html|json|xml))?/?$', views.modules, name='modules'),
]
```

View:
```python
def modules(request, format='html'):
    ...
    return render(...)
```

## Version and environment

- Fails in: Django 3.0
- Last known working: Django 2.2
- Python: 3.6 (from the traceback paths, e.g. `/l10n/venv/lib/python3.6/site-packages/...`)
- OS and other environment details: Not provided in the original report.