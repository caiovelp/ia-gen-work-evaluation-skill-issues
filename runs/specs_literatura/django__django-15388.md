## Summary

The Django development server (`manage.py runserver`) stops auto-reloading on file changes when `BASE_DIR` is added to `TEMPLATES[0]['DIRS']` in `settings.py`. This affects edits to any file, not just `settings.py`. Removing `BASE_DIR` from `DIRS` and restarting the server manually brings auto-reloading back.

## Steps to reproduce

1. Install or upgrade Django:
   ```
   $ pip install -U django
   ```
2. Create a new project:
   ```
   $ django-admin startproject <name>
   ```
3. Open the generated `settings.py`. Copy the `BASE_DIR` variable (line 16) and paste it into the empty `DIRS` list in the `TEMPLATES` setting (line 57).
4. Start the development server:
   ```
   $ ./manage.py runserver
   ```
5. In your IDE, save any file in the project.
6. The development server does not restart.

To confirm the cause:

7. In `settings.py`, remove `BASE_DIR` from the `TEMPLATES` `DIRS` list.
8. Stop the development server with Ctrl-C. This is needed because it no longer restarts on its own.
9. Start the development server again with `./manage.py runserver`.
10. Save `settings.py` again.
11. The development server detects the change and restarts.

## Observed behavior

With `BASE_DIR` in `TEMPLATES[0]['DIRS']`, the development server does not detect file changes and does not restart. This happens no matter which file is edited, not only `settings.py`. The server has to be stopped and started by hand.

## Expected behavior

The development server should detect file changes and restart automatically, whether or not `BASE_DIR` is listed in `TEMPLATES[0]['DIRS']`.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report. A minimal manual check based on the steps above:

1. In a fresh project, set `TEMPLATES[0]['DIRS']` to contain `BASE_DIR`.
2. Run `./manage.py runserver`.
3. Save any project file.
4. Check whether the server restarts. It should restart, but in the reported bug it does not.

## Code example

The only change from the default `startproject` `settings.py` is adding `BASE_DIR` to the empty `DIRS` list:

```python
TEMPLATES = [
    {
        # ...
        'DIRS': [BASE_DIR],
        # ...
    },
]
```

## Version and environment

- Django: the latest release installed via `pip install -U django` at the time of the report. No exact version number was given.
- Project: newly created with `django-admin startproject`.
- Python version, OS, and IDE: Not provided in the original report.