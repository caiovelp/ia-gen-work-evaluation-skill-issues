# Spec: StatReloader Must Track Changes to `manage.py` (Regression in Django 2.2)

## Objective

**What:** Restore the Django 2.1.x behavior where editing the entry-point script (`manage.py`) while `python manage.py runserver` is running triggers an automatic reload.

**Why:** This is a regression. In Django 2.1.8 and earlier, editing `manage.py` triggered a reload. In Django 2.2.1 it does not. The reporter observed in the `django.utils.autoreload` log lines that `manage.py` never appears among the watched files. Developers who edit `manage.py`, for example to change `DJANGO_SETTINGS_MODULE` or add startup logic, get a silently stale server.

**Who:** Developers running the development server with `runserver` and the autoreloader enabled, using `StatReloader`.

**User story:**
> As a developer running `python manage.py runserver`, when I save a change to `manage.py`, the dev server reloads so the change takes effect, as it did in Django 2.1.

**Acceptance criteria:**
1. When `runserver` is started via `python manage.py runserver`, the file `manage.py` is included in the set of files watched by `StatReloader`.
2. Modifying `manage.py`, for example adding `print('sth')` inside `main()`, causes the autoreloader to detect a change and restart the server process.
3. Files that are already watched in 2.2.1 are still watched.

## Tech Stack

- Python. The reporter used 3.6.2. The full supported Python range for the affected branch is **unknown**.
- Django 2.2.1 is affected. Django 2.1.8 is the last known-good version.
- Component: `django.utils.autoreload`, specifically `StatReloader`.
- Reporter's platform: OSX 10.11, pip 19.1.1.

## Commands

The repository is not visible, so all commands are **unknown**.

- Build: unknown
- Test (autoreload test suite): unknown
- Lint: unknown
- Manual reproduction:
  ```
  pip install Django==2.2.1
  python manage.py runserver
  # then edit manage.py, e.g. add print('sth') inside main()
  ```

## Project Structure

Only the module named in the issue is known. File paths in the repository are **unknown**.

- `django.utils.autoreload` is the module that decides which files are watched and contains `StatReloader`.
- Location of the autoreload tests: unknown.
- Location of release notes / changelog for 2.2.x: unknown.

## Code Style

The repository was not inspected, so no code snippet is included. Follow the existing Django conventions found in `django.utils.autoreload` and its tests. Those conventions are unknown here.

## Testing Strategy

- **Framework:** Django's own test suite. The runner command is unknown.
- **Regression test (required):** a unit test showing that the entry-point script used to launch the process (the `__main__` module run as a file, e.g. `manage.py`) is included in the set of files the autoreloader watches. The test must fail on the current 2.2.1 behavior and pass after the fix.
- **Non-regression:** the existing autoreload tests must keep passing. Normally imported modules, extra watched files, and similar cases must still be tracked.
- **Edge cases to cover, where behavior is defined (see Open Questions):**
  - `__main__` has no file. Examples: an interactive session, or `python -c`. This must not crash the reloader.
  - Launched via `python -m django runserver` / `django-admin runserver` rather than `manage.py`.
- **Manual check:** follow the reproduction steps above on the fixed version and confirm that the server reloads.

## Boundaries

- **Always:**
  - Add a regression test that reproduces the issue before changing behavior.
  - Keep the change scoped to which files the autoreloader watches.
  - Run the full autoreload test suite.
- **Ask first:**
  - Changing the public API or signatures in `django.utils.autoreload`.
  - Changing behavior of `WatchmanReloader` beyond what is shared with `StatReloader`.
  - Backporting decisions, i.e. which branches receive the fix.
- **Never:**
  - Remove or weaken existing autoreload tests.
  - Add new dependencies.
  - Introduce behavior that crashes when `__main__` lacks a file path.

## Success Criteria

1. With `python manage.py runserver` running under `StatReloader`, editing and saving `manage.py` triggers a server reload.
2. `manage.py` (the script file of the `__main__` module) appears in the autoreloader's watched file set.
3. The new regression test fails before the fix and passes after it.
4. All existing autoreload tests pass.
5. No error occurs when the process's `__main__` module has no associated file.

## Assumptions

1. **Probable cause (hypothesis, not verified against the code):** the Django 2.2 autoreloader builds its watched-file list from loaded modules in a way that skips the `__main__` module when a script is run directly. Such a module may lack the module metadata the new code relies on. Version 2.1 included it.
2. The regression is specific to the file-watching list. It is not about change detection itself, since edits to other project files still reload.
3. The fix should also benefit `WatchmanReloader` if both reloaders share the watched-file collection. The issue mentions only `StatReloader`.
4. The issue is not OS-specific, even though it was reported on OSX 10.11.
5. The target is the 2.2.x branch and the main development branch.

## Open Questions

1. Should the fix apply to both `StatReloader` and `WatchmanReloader`, or does only `StatReloader` need it?
2. When launched via `django-admin runserver` or `python -m django runserver`, should the entry-point script also be watched? Or only a user-owned script like `manage.py`?
3. Which branches should receive the fix: a 2.2.x backport, main only, or both?
4. Is a release note entry required for the 2.2.x patch release?
5. What are the exact test, lint, and build commands, and where do the autoreload tests live?