## Summary

Migration `auth.0011_update_proxy_permissions` fails with an `IntegrityError` (duplicate key in `auth_permission`) when running `python manage.py migrate` after upgrading a project to Django 2.2. According to the report title, the failure affects models that were recreated as a proxy. The migration appears to try to re-create entries that already exist in the `auth_permission` table.

## Steps to reproduce

1. Start with an existing project on Django 2.0.13 or Django 2.1.8. The project has proxy models; according to the title, these are models that were recreated as a proxy.
2. Upgrade the project to Django 2.2.
3. Run `python manage.py migrate`.
4. The error occurs while `auth.0011_update_proxy_permissions` is being applied.

The report does not give the exact model definitions or the migration history needed to reproduce this.

## Observed behavior

- Applying `auth.0011_update_proxy_permissions` fails with `django.db.utils.IntegrityError`, a duplicate key violation on the unique constraint over `(content_type_id, codename)` in `auth_permission`.
- The migration appears to be re-creating permission entries that already exist.
- The reporter first suspected a recently renamed model. They deleted that model's entries from `auth_permission`, but the same error still occurred for other proxy models.
- The error occurred when upgrading from 2.0.13 and also when upgrading from 2.1.8.
- Recreating the virtual environment from scratch had no effect.

## Expected behavior

`auth.0011_update_proxy_permissions` should apply without error on an existing database whose `auth_permission` table already contains entries for proxy models, including models recreated as a proxy. It should not try to insert permissions that already exist.

## Stack trace / error output

```
django.db.utils.IntegrityError: duplicate key value violates unique constraint "idx_18141_auth_permission_content_type_id_01ab375a_uniq" DETAIL: Key (co.ntent_type_id, codename)=(12, add_agency) already exists.
```

The error is quoted as given in the original report, including "co.ntent_type_id". The reporter says the full stack trace is available at an external link, but it is not included in the report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

- Target version: Django 2.2
- Upgraded from: Django 2.0.13 and Django 2.1.8 (tried separately; both fail)
- Database backend, Python version, OS: Not provided in the original report.
- Also discussed on the django-users mailing list, where the reporter was asked to file this ticket.