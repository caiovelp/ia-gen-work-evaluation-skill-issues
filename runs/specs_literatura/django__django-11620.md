## Summary

When `DEBUG = True`, raising `Http404` inside a custom path converter's `to_python` method does not produce Django's technical 404 response. Instead, a plain-text server error message is returned, which does not help identify the problem.

The reporter understands that `to_python` is meant to raise `ValueError` to tell the URL resolver "this path does not match, try the next one". However, raising `Http404` felt intuitive, and the resulting error message gave no hint about what went wrong.

## Steps to reproduce

1. Set `DEBUG = True` in the project settings.
2. Define a custom path converter whose `to_python` method raises `Http404`, instead of `ValueError`, for a given value.
3. Register the converter and use it in a URL pattern.
4. Request a URL that matches that pattern with a value that causes `to_python` to raise `Http404`.

## Observed behavior

The response is plain text containing only:

```
A server error occurred. Please contact the administrator.
```

No technical 404 page or other helpful debug information is shown.

## Expected behavior

With `DEBUG = True`, raising `Http404` in a path converter's `to_python` should result in a technical response that explains what happened, rather than a generic server error.

The reporter argues that raising `Http404` should be a valid way for a converter to tell the resolver: "this is the right path, but the parameter value does not match anything, so stop resolving and let the handler return the 404 page." With `DEBUG = True`, that 404 page should include a helpful error message instead of the default "Django tried these URL patterns" output.

This would be useful, for example, for a path converter that uses `get_object_or_404`.

## Stack trace / error output

Not provided in the original report. The only output given is the plain-text response:

```
A server error occurred. Please contact the administrator.
```

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report. The only known setting is `DEBUG = True`.