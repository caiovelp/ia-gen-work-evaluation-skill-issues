# Spec: Dev server autoreload stops working when a project-root path is in `TEMPLATES[0]['DIRS']`

## Objective

**Problem.** In a freshly generated Django project, adding `BASE_DIR` to `TEMPLATES[0]['DIRS']` in `settings.py` stops `manage.py runserver` from restarting on file changes. This happens for edits to **any** file, not only `settings.py`. Removing `BASE_DIR` from `DIRS` and restarting the server manually brings autoreload back.

**Who is affected.** Developers who run `manage.py runserver` and list a template directory that contains Python source. The project root is the most common case.

**What success looks like.** The dev server's code autoreload keeps working no matter which directories are listed in template `DIRS`, including directories that contain Python source files such as the project root.

**User story.**
- As a developer, when I put `BASE_DIR` (or any ancestor of my source files) in `TEMPLATES[0]['DIRS']` and save a Python file, the dev server restarts. It behaves the same as when `DIRS` is empty.

**Reported reproduction (from the issue).**
1. `pip install -U django`
2. `django-admin startproject <name>`
3. In `settings.py`, set `TEMPLATES[0]['DIRS'] = [BASE_DIR]`.
4. Run `./manage.py runserver`.
5. Save any file. The server does **not** restart.
6. Remove `BASE_DIR` from `DIRS`, restart the server manually, and save `settings.py`. The server restarts as expected.

## Assumptions

1. The Django version is the latest release at the time of the report. `pip install -U django` was used, and the exact version is not stated.
2. The default `StatReloader` or `WatchmanReloader` behaviour is affected, and the user has not customized the reloader.
3. The behaviour is deterministic and not specific to an IDE, OS or filesystem. The reporter used an IDE save; the OS is not stated.
4. Template-directory watching in the autoreloader is the likely mechanism. This is unverified because the code is not visible here. The template-change handling may claim changes to files under template dirs, including `.py` files, and suppress the full process restart. Under that hypothesis, any template dir that contains Python source shows the bug, not only `BASE_DIR`.
5. The expected behaviour is:
   - Changes to Python source files always trigger a full restart, even if they sit inside a template directory.
   - Template-change handling, such as resetting template loaders without a restart, still applies to actual template files.
6. The fix belongs in Django itself. Telling users not to put `BASE_DIR` in `DIRS` is not the resolution, because it is a valid and documented-style configuration.
7. Template `DIRS` entries may be `pathlib.Path` objects (as with `BASE_DIR` from `startproject`) or strings. Both must be handled.

## Tech Stack

- Python and Django. The exact versions are **unknown** (see Open Questions).
- Components in scope:
  - Django's development-server autoreloader
  - The template engine configuration (`TEMPLATES` / `DIRS`)
  - Any template-change hooks that the autoreloader consults
- Exact module paths: **unknown**, because they are not visible in the issue.

## Commands

All commands are **unknown** and must be confirmed against the repository:
- Build: unknown (likely none for a pure-Python change)
- Test: unknown (Django's test runner invocation for the relevant test modules)
- Lint: unknown
- Manual repro: `django-admin startproject <name>` then `./manage.py runserver`. These are taken from the issue.

## Project Structure

**Unknown.** These still need to be located in the repository:
- The autoreloader implementation
- The template autoreload / change-detection integration
- Their existing test modules

## Code Style

**Unknown.** Follow existing Django conventions in the files touched. No snippet is available from the issue.

## Testing Strategy

**Regression test (required).** With a template backend whose `DIRS` contains a directory holding a `.py` file, a change to that `.py` file must not be treated as handled by the template-change logic. It must result in a full reload.

**Preserve existing behaviour:**
- A change to a non-Python file inside a template dir, such as an `.html` template, is still handled as a template change (for example, a loader reset) as it is today.
- A change to a `.py` file outside any template dir still triggers a reload.

**Edge cases to cover:**
- `DIRS` given as `pathlib.Path` and as `str`.
- A template dir that is an ancestor of the project's source tree (the `BASE_DIR` case).
- An empty `DIRS`, where behaviour must be unchanged.
- Multiple template backends and app-directory template loaders, if they participate in the same watching mechanism.

**Test levels.** Unit tests on the change-detection logic are the primary level. A manual runserver repro serves as the final check.

**Coverage expectation.** Unknown, so follow project norms.

## Boundaries

**Always:**
- Add a regression test that fails before the fix and passes after it.
- Keep template-only change handling working for template files.
- Run the existing autoreload and template test suites.

**Ask first:**
- Changing which files or globs the autoreloader watches in general.
- Changing any public settings or the documented behaviour of template autoreloading.
- Adding dependencies.

**Never:**
- "Fix" the issue by documenting that `BASE_DIR` must not be in `DIRS`.
- Disable template-change detection entirely.
- Remove or weaken existing autoreload tests.

## Success Criteria

1. With `TEMPLATES[0]['DIRS'] = [BASE_DIR]` in a `startproject` project, saving any `.py` file under `BASE_DIR` causes `runserver` to restart. This includes `settings.py`, which must restart on every save.
2. With the same config, editing a template file inside a template dir still behaves as template changes do today, with no regression.
3. With an empty `DIRS`, autoreload behaviour is identical to before.
4. The regression test reproduces the bug on the unfixed code and passes on the fixed code.
5. The existing autoreload and template test suites pass.

## Open Questions

1. **Version.** Which Django version(s) exhibit this? Is it a regression introduced by template-directory watching, and which release branches should get the fix?
2. **Reloader scope.** Does it reproduce with both `StatReloader` and `WatchmanReloader`?
3. **Other file types.** Should only `.py` files be excluded from template-change handling? Or should it be restricted to known template files, or to files actually resolvable by a template loader? What about other non-template files under a template dir, such as `.txt`, `.json` or static files?
4. **Watching itself.** Is it acceptable that listing `BASE_DIR` in `DIRS` makes the reloader watch the whole project tree for template changes? Watching a large tree could be a performance concern, and it may be worth a separate issue.
5. **Locations.** Where do the autoreloader, the template-change hook and their tests live in the repository? Paths and commands are unknown.
6. **Release notes.** Should the fix include a release note or documentation clarification?