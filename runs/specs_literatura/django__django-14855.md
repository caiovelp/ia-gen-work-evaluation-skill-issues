## Summary

In a custom Admin Site, the link that `get_admin_url` (in `django.contrib.admin.helpers`) generates for a ForeignKey field listed in `readonly_fields` points to `/admin/...` instead of the custom site's URL prefix (e.g. `/custom-admin/...`).

## Steps to reproduce

1. Define a model that contains a ForeignKey field.
2. Create a custom Admin Site, mounted for example at `/custom-admin/`.
3. Register the model with the custom Admin Site using a `ModelAdmin` that lists the ForeignKey field in `readonly_fields`.
4. Open an instance of the model in the custom Admin Site, either to view or to edit it.
5. Look at the URL of the link rendered for the read-only ForeignKey field.

## Observed behavior

The link for the read-only ForeignKey field points to the default admin site (`/admin/...`).

## Expected behavior

The link should point to the custom Admin Site in use (`/custom-admin/...`). Other parts of the admin already do this by passing the `current_app` keyword parameter to identify the current Admin Site. The reporter cites `django.contrib.admin.options.ModelAdmin.response_add` as one example.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

The reporter identifies this line in `get_admin_url` in `django.contrib.admin.helpers` as the apparent cause. The call to `reverse()` does not pass `current_app`:

```python
url = reverse(url_name, args=[quote(remote_obj.pk)])
```

## Version and environment

Not provided in the original report.