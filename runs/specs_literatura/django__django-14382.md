## Summary

Running `django-admin startapp` with a trailing slash on the target directory name (e.g. `directory/`) fails with a `CommandError` saying `''` is not a valid app directory. Bash tab-completion adds trailing slashes to directory names automatically, so this is easy to hit.

## Steps to reproduce

1. In a shell, type `django-admin startapp name directory`, using Bash tab-completion to complete the directory name. Tab-completion appends a trailing slash.
2. Run the resulting command:
   ```bash
   django-admin startapp name directory/
   ```

## Observed behavior

The command fails with a `CommandError`. The directory name in the error message is an empty string (`''`) instead of `directory`.

The reporter traces the error to line 77 of `django/core/management/templates.py`. That line calls `os.path.basename()` on the target path without accounting for a trailing slash. For a path ending in a separator, `basename()` returns an empty string, and validation then rejects it.

## Expected behavior

`django-admin startapp name directory/` should behave the same as `django-admin startapp name directory`. The trailing slash should not cause the directory name to be rejected.

## Stack trace / error output

```
CommandError: '' is not a valid app directory. Please make sure the directory is a valid identifier.
```

Full stack trace: Not provided in the original report.

## Test case

Minimal reproduction derived from the report:

1. Run `django-admin startapp name directory/`, with a trailing slash on the target directory.
2. Check that no `CommandError: '' is not a valid app directory...` is raised.
3. Check that the result matches running the same command without the trailing slash.

## Code example

The line identified in the report (line 77 of `django/core/management/templates.py`):

```python
self.validate_name(os.path.basename(target), 'directory')
```

## Version and environment

- Django version: Not provided in the original report.
- Shell: Bash, where tab-completion appends trailing slashes to directory names.
- OS / Python version: Not provided in the original report.