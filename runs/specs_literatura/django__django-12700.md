## Summary

`django.views.debug.SafeExceptionReporterFilter.get_safe_settings()` (and `django.views.debug.get_safe_settings()` on Django 3.0 and below) returns some sensitive values without cleansing them. `cleanse_setting()` only cleanses `dict`s. Other iterables, such as lists, are returned as-is. Sensitive keys such as `secret` and `token` inside dictionaries nested in lists are therefore exposed. The reporter posted this publicly after checking with the rest of the Django security team.

## Steps to reproduce

1. Add the following setting to `settings.py`:
   ```python
   MY_SETTING = {
       "foo": "value",
       "secret": "value",
       "token": "value",
       "something": [
           {"foo": "value"},
           {"secret": "value"},
           {"token": "value"},
       ],
       "else": [
           [
               {"foo": "value"},
               {"secret": "value"},
               {"token": "value"},
           ],
           [
               {"foo": "value"},
               {"secret": "value"},
               {"token": "value"},
           ],
       ]
   }
   ```
2. Open a Django shell.
3. On Django 3.1 and up, run:
   ```python
   >>> from django.views.debug import SafeExceptionReporterFilter
   >>> import pprint
   >>> pprint.pprint(SafeExceptionReporterFilter().get_safe_settings()["MY_SETTING"])
   ```
   On Django 3.0 and below, run:
   ```python
   >>> import pprint
   >>> from django.views.debug import get_safe_settings
   >>> pprint.pprint(get_safe_settings()["MY_SETTING"])
   ```
4. Check the values of the `secret` and `token` keys in the output.

## Observed behavior

Top-level `secret` and `token` keys are cleansed. The same keys inside dictionaries nested in lists (`something`) and in lists of lists (`else`) are returned unmodified. The output is the same on Django 3.0 and below and on Django 3.1 and up:

```
{'else': [[{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
          [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}]],
 'foo': 'value',
 'secret': '********************',
 'something': [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
 'token': '********************'}
```

## Expected behavior

The values of sensitive keys (`secret`, `token`) should be replaced with `'********************'` at every nesting level. This includes dictionaries contained in lists and in lists of lists, the same way the top-level keys are cleansed. Non-sensitive keys (`foo`) should remain `'value'`.

## Stack trace / error output

Not provided in the original report. This issue produces no error. The problem is uncleansed output.

## Test case

Minimal test derived from the reproduction in the report (Django 3.1+ API):

```python
import pprint
from django.views.debug import SafeExceptionReporterFilter

# With MY_SETTING defined in settings.py as shown in "Steps to reproduce":
safe = SafeExceptionReporterFilter().get_safe_settings()["MY_SETTING"]
pprint.pprint(safe)

# Currently fails: nested sensitive values are not cleansed
assert safe["something"][1]["secret"] == '********************'
assert safe["something"][2]["token"] == '********************'
assert safe["else"][0][1]["secret"] == '********************'
assert safe["else"][1][2]["token"] == '********************'
```

## Code example

The setting that triggers the issue:

```python
MY_SETTING = {
    "foo": "value",
    "secret": "value",
    "token": "value",
    "something": [
        {"foo": "value"},
        {"secret": "value"},
        {"token": "value"},
    ],
    "else": [
        [
            {"foo": "value"},
            {"secret": "value"},
            {"token": "value"},
        ],
        [
            {"foo": "value"},
            {"secret": "value"},
            {"token": "value"},
        ],
    ]
}
```

The behavior comes from `cleanse_setting()` in `django.views.debug`. That function only handles `dict` values and returns other iterable types as-is.

## Version and environment

- Affected: Django 3.0 and below (`django.views.debug.get_safe_settings()`)
- Affected: Django 3.1 and up (`django.views.debug.SafeExceptionReporterFilter.get_safe_settings()`)
- Python version, OS and other environment details: Not provided in the original report.