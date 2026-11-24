## Summary
Show the domain/subdomain of each route in the output of `flask routes`.

## Description
The `flask routes` command lists all registered routes, but it does not show which subdomain each route belongs to. When blueprints are registered on different subdomains, routes with the same rule look identical in the output.

**Example setup**

- Default server name: `SERVER_NAME: 'test.local'`
- Domains (subdomains):
  - `test.test.local`
  - `admin.test.local`
  - `test.local`
- Blueprint registration:
  ```python
  app.register_blueprint(admin_blueprint,url_prefix='',subdomain='admin')
  app.register_blueprint(test_subdomain_blueprint,url_prefix='',subdomain='test')
  ```

**Current output**

```
$ flask routes
 * Tip: There are .env or .flaskenv files present. Do "pip install python-dotenv" to use them.
Endpoint                                                 Methods    Rule
-------------------------------------------------------  ---------  ------------------------------------------------
admin_blueprint.home                                      GET        /home
test_subdomain_blueprint.home                             GET        /home
static                                                    GET        /static/<path:filename>
...
```

Both `admin_blueprint.home` and `test_subdomain_blueprint.home` appear with the rule `/home`. Nothing in the output shows that one is served on `admin.test.local` and the other on `test.test.local`.

## Product version
Not provided in the original request.

## Rationale
To find out which route belongs to which subdomain, the user currently has to look up the application configuration (the blueprint registrations and `SERVER_NAME`). Showing the domain in the `flask routes` output would make this clear.

## Use case or scenario
A developer's application uses `SERVER_NAME = 'test.local'` and registers blueprints on the `admin` and `test` subdomains. Some routes in different blueprints share the same rule, such as `/home`. The developer runs `flask routes` to inspect the URL map and wants to see right away which domain serves each route, without cross-checking the configuration.

## Possible solution
The original request suggests two options:

1. **Add a `Domain` column to `flask routes`.** The requested output looks like this:

   ```
   $ flask routes
    * Tip: There are .env or .flaskenv files present. Do "pip install python-dotenv" to use them.
   Domain                Endpoint                                             Methods    Rule
   -----------------   ----------------------------------------------------  ----------  ------------------------------------------------
   admin.test.local     admin_blueprint.home                                  GET        /home
   test.test.local      test_subdomain_blueprint.home                         GET        /home
   test.local           static                                                GET        /static/<path:filename>
   ...
   ```

2. **If `flask routes` cannot be changed**, add a method or document which existing Flask method(s) can be used to get this domain-per-route information programmatically.