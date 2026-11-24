## Summary

In `django.contrib.sitemaps`, the sitemap index view raises `ValueError: max() arg is an empty sequence` for a sitemap whose `items()` returns no items but which defines `lastmod` as a callable. The error comes from `Sitemap.get_latest_lastmod()`.

## Steps to reproduce

1. Define a sitemap class whose `items()` returns an empty sequence.
2. On the same class, define `lastmod` as a callable that returns the last-modified value for an item.
3. Register the sitemap with the sitemap index view (`django.contrib.sitemaps.views.index`).
4. Request the sitemap index, for example `/sitemap.xml`.

## Observed behavior

The request fails with an unhandled exception:

- Exception Type: `ValueError` at `/sitemap.xml`
- Exception Value: `max() arg is an empty sequence`

The index view calls `site.get_latest_lastmod()`, which calls `max()` on an empty list because the sitemap has no items.

## Expected behavior

The sitemap index should render without raising an exception when a sitemap with a callable `lastmod` has no items.

## Stack trace / error output

```
Traceback (most recent call last):
 File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
	response = get_response(request)
 File "/usr/local/lib/python3.10/site-packages/django/core/handlers/base.py", line 197, in _get_response
	response = wrapped_callback(request, *callback_args, **callback_kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/utils/decorators.py", line 133, in _wrapped_view
	response = view_func(request, *args, **kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/views.py", line 34, in inner
	response = func(request, *args, **kwargs)
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/views.py", line 76, in index
	site_lastmod = site.get_latest_lastmod()
 File "/usr/local/lib/python3.10/site-packages/django/contrib/sitemaps/__init__.py", line 170, in get_latest_lastmod
	return max([self.lastmod(item) for item in self.items()])
Exception Type: ValueError at /sitemap.xml
Exception Value: max() arg is an empty sequence
```

## Test case

Not provided in the original report.

(Scenario from the report: a sitemap with an empty `items()` and a callable `lastmod`, requested through the sitemap index view at `/sitemap.xml`. This should not raise `ValueError`.)

## Code example

The current `Sitemap.get_latest_lastmod()` code that the report quotes as context (`django/contrib/sitemaps/__init__.py`):

```python
def get_latest_lastmod(self):
    if not hasattr(self, "lastmod"):
        return None
    if callable(self.lastmod):
        try:
            return max([self.lastmod(item) for item in self.items()])
        except TypeError:
            return None
    else:
        return self.lastmod
```

When `self.items()` is empty, the list passed to `max()` is empty. `max()` then raises `ValueError`, which the `except TypeError` clause does not catch.

## Version and environment

- Python: 3.10 (from the traceback paths `/usr/local/lib/python3.10/site-packages/...`)
- Django version: Not provided in the original report.
- Operating system and other environment details: Not provided in the original report.