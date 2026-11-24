## Summary
Add support for the `SCRIPT_NAME` WSGI parameter in `STATIC_URL` and `MEDIA_URL`.

## Description
The `{% static '...' %}` template tag builds URLs by appending the path to `STATIC_URL`. When a Django application is served under a sub-path through the `SCRIPT_NAME` WSGI parameter, the tag does not prepend the `SCRIPT_NAME` prefix, so the generated static URLs are wrong.

The same issue affects the storage backends: `FileSystemStorage` and `StaticFilesStorage` also ignore `SCRIPT_NAME`. As a result, URLs based on both `STATIC_URL` and `MEDIA_URL` are affected.

## Product version
Not provided in the original request.

## Rationale
- Applications deployed under a sub-path get incorrect URLs for static and media files.
- The current workaround is to prepend `SCRIPT_NAME` to `STATIC_URL` in `settings.py`. This does not work when `SCRIPT_NAME` is dynamic, for example when it is only known at request time.
- The author acknowledges the change may require many modifications but considers it worth the effort.

## Use case or scenario
1. A Django application is deployed behind a WSGI server under a sub-path, with the prefix supplied through the `SCRIPT_NAME` WSGI parameter.
2. A template uses `{% static '...' %}`, or the application builds file URLs through `FileSystemStorage` or `StaticFilesStorage`.
3. **Expected:** the generated URL includes the `SCRIPT_NAME` prefix.
4. **Actual:** the URL contains only `STATIC_URL` (or `MEDIA_URL`) plus the path, without the prefix.

## Possible solution
The original request suggests updating the `render` method of both the default Django `static` tag and the `django.contrib.staticfiles` `static` tag. The URL would be adjusted using `request.META['SCRIPT_NAME']` before it is returned or stored in the context:

```python
def render(self, context):
    url = self.url(context)
    # Updating url here with request.META['SCRIPT_NAME']
    if self.varname is None:
        return url
    context[self.varname] = url
    return ''
```

The request also notes that `FileSystemStorage` and `StaticFilesStorage` would need similar changes to respect `SCRIPT_NAME`. It does not describe those changes in detail.