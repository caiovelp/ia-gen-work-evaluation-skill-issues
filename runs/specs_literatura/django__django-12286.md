## Summary

Django raises the system check error `translation.E004` when `LANGUAGE_CODE` is set to a sublanguage (e.g. `de-at`) that Django does not ship, even though its base language (`de`) is available. According to the Django documentation, Django should fall back to the base language in this case, so the check should not fail.

## Steps to reproduce

1. Use Django 3.0.2.
2. In `settings.py`, set:
   ```python
   LANGUAGE_CODE = "de-at"
   ```
3. Run the project so that system checks execute.
4. Observe the `translation.E004` error.
5. For comparison, change the setting to:
   ```python
   LANGUAGE_CODE = "es-ar"
   ```
   `es-ar` is one of the translations Django provides out of the box.
6. Run the project again. No error is raised.

## Observed behavior

With `LANGUAGE_CODE = "de-at"`, the system check fails with `translation.E004`. It reports that `LANGUAGE_CODE` is not in the `LANGUAGES` setting. This happens even though the base language `de` is available.

With `LANGUAGE_CODE = "es-ar"`, Django works fine.

## Expected behavior

The Django documentation says:

> If a base language is available but the sublanguage specified is not, Django uses the base language. For example, if a user specifies de-at (Austrian German) but Django only has de available, Django uses de.

So `LANGUAGE_CODE = "de-at"` should pass the system checks without raising `translation.E004`, because the base language `de` is available.

## Stack trace / error output

```
SystemCheckError: System check identified some issues:
ERRORS:
?: (translation.E004) You have provided a value for the LANGUAGE_CODE setting that is not in the LANGUAGES setting.
```

## Test case

Not provided in the original report.

The report implies a minimal check:
- With `LANGUAGE_CODE = "de-at"` and the default `LANGUAGES`, the translation system checks should return no `translation.E004` error.
- With `LANGUAGE_CODE = "es-ar"`, the checks pass, as they already do.

## Code example

```python
# settings.py: triggers translation.E004
LANGUAGE_CODE = "de-at"
```

```python
# settings.py: works fine
LANGUAGE_CODE = "es-ar"
```

## Version and environment

- Django 3.0.2
- Python version, OS and other environment details: Not provided in the original report.