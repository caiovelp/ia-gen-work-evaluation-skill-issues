## Summary

`django.forms.URLField().clean()` raises a raw `ValueError: Invalid IPv6 URL` for the malformed input `'////]@N.AN'`. It should raise a `ValidationError`. The exception comes from `urllib.parse.urlsplit`, which is called by the URL validator in `django/core/validators.py`. The issue was found by fuzzing.

## Steps to reproduce

1. Import Django's forms module: `from django import forms`.
2. Create a `URLField` with default arguments: `field = forms.URLField()`.
3. Call `field.clean('////]@N.AN')`.

## Observed behavior

A `ValueError: Invalid IPv6 URL` is raised from `urllib/parse.py` (`urlsplit`). It propagates out of `URLField.clean()` and is not converted to a `ValidationError`.

## Expected behavior

`URLField.clean()` should raise `django.core.exceptions.ValidationError` for this invalid URL, as it does for other invalid input. It should not leak a `ValueError`.

## Stack trace / error output

```
ValueError: Invalid IPv6 URL
Traceback (most recent call last):
  File "basic_fuzzer.py", line 22, in TestOneInput
  File "fuzzers.py", line 350, in test_forms_URLField
  File "django/forms/fields.py", line 151, in clean
  File "django/forms/fields.py", line 136, in run_validators
  File "django/core/validators.py", line 130, in __call__
  File "urllib/parse.py", line 440, in urlsplit
```

## Test case

Minimal test derived from the reproduction snippet in the report:

```python
from django import forms
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase


class URLFieldInvalidIPv6Test(SimpleTestCase):
    def test_clean_invalid_ipv6_url_raises_validation_error(self):
        f = forms.URLField()
        with self.assertRaises(ValidationError):
            f.clean('////]@N.AN')
```

## Code example

```python
forms.URLField().clean('////]@N.AN')
```

## Version and environment

- Django version: Not provided in the original report.
- Python version: Not provided in the original report.
- Operating system: Not provided in the original report.
- Context: The issue was found with a fuzzing harness (`basic_fuzzer.py`, `fuzzers.py`, `test_forms_URLField`).