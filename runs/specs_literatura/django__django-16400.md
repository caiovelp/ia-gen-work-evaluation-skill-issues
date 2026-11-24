## Summary

The `migrate` management command does not respect the database parameter when adding Permissions. When `migrate` is invoked with a database parameter, the migration itself succeeds. However, a DB read request runs after the migration, and that read does not use the specified database. Instead it calls the configured DB router (`db_for_read`).

The reporter expects every DB call made in the context of the `migrate` command to use the specified database. They found the problem while using a thread-local variable and a custom DB router to select the active DB in a multi-tenant service.

## Steps to reproduce

1. Add the custom middleware (`TenantSubdomainMiddleware`) and custom DB router (`TenantDatabaseRouter`) shown in the Code example section, in a module such as `utils/tenant_db_router.py`.
2. Configure `settings.py`:
   - Add `"utils.tenant_db_router.TenantSubdomainMiddleware"` to `MIDDLEWARE`.
   - Set `TENANT_MAP = {"localhost": "default", "tenant_1": "default"}`.
   - Set `DATABASE_ROUTERS = ["utils.tenant_db_router.TenantDatabaseRouter"]`.
3. Run any DB migration using the `migrate` management command with the database parameter specified.
4. Watch the console output.

## Observed behavior

- The migration runs successfully.
- A DB read request then runs after the migration (according to the title, while adding Permissions). It does not respect the database parameter and goes through the DB router.
- `read {}` is printed by the router's `db_for_read` method, followed by an exception message. No thread-local subdomain is set outside a request, so the router's `_default_db()` raises `InvalidTenantException`.

## Expected behavior

When a database is passed as a parameter to `migrate`, all DB calls made by the command should use that database. The router's `db_for_read` / `db_for_write` should not be called, because the database was already specified.

## Stack trace / error output

The only output described is:

```
read {}
```

This is printed before an exception message. The full exception message and stack trace are not provided in the original report.

## Test case

Not provided in the original report.

## Code example

```python
from threading import local
from django.conf import settings

local_state = local()

class InvalidTenantException(Exception):
    pass

class TenantSubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ## Get Subdomain
        host = request.get_host().split(":")[0]
        local_state.subdomain = (
            # We assume single level of subdomain : app.service.com
            # HOST_IP : used to for local dev.
            host if host in settings.HOST_IP else host.split(".")[0]
        )
        response = self.get_response(request)
        return response

class TenantDatabaseRouter:
    def _default_db(self):
        subdomain = getattr(local_state, "subdomain", None)
        if subdomain is not None and subdomain in settings.TENANT_MAP:
            db_name = settings.TENANT_MAP[local_state.subdomain]
            return db_name
        else:
            raise InvalidTenantException()

    def db_for_read(self, model, **hints):
        print("read", hints)
        return self._default_db()

    def db_for_write(self, model, **hints):
        print("write", hints)
        return self._default_db()

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None
```

```python
## settings.py
MIDDLEWARE = [
    "utils.tenant_db_router.TenantSubdomainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    ...
]
TENANT_MAP = {"localhost": "default", "tenant_1": "default"}
DATABASE_ROUTERS = ["utils.tenant_db_router.TenantDatabaseRouter"]
```

## Version and environment

Not provided in the original report. The only context given is a multi-tenant service that uses a thread-local variable and a custom DB router to select the active database.