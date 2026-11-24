# Spec: Accept trailing path separators in the `startapp` target directory

## Objective

`django-admin startapp <name> <directory>` fails when `<directory>` ends with a path separator. Bash tab-completion adds a trailing slash to directory names, so this input is common:

```
$ django-admin startapp name directory/
CommandError: '' is not a valid app directory. Please make sure the directory is a valid identifier.
```

**Root cause (from the issue):** `django/core/management/templates.py`, line 77, validates `os.path.basename(target)`. For a path ending in a separator, `basename()` returns `''`, so validation rejects an empty name.

```python
self.validate_name(os.path.basename(target), 'directory')
```

**Users:** Developers who run `django-admin startapp` or `manage.py startapp` with an explicit target directory, especially those using shell tab-completion.

**Success means:** A trailing separator on the target directory is ignored when the directory name is validated. `directory/` behaves exactly like `directory`.

The issue suggests stripping trailing separators before calling `basename()`. That is a candidate approach, not a settled decision. The exact fix is out of scope for this spec.

## Assumptions

1. The bug is confined to the directory-name validation step. Later handling of `target` (for example, resolving it to an absolute path and checking that it exists) already tolerates trailing separators. This has not been verified.
2. The validation at line 77 applies only to `startapp` targets. `startproject` targets are not validated this way, but the shared code path should be checked.
3. Behaviour for valid inputs without a trailing separator must not change.
4. Multiple trailing separators (`directory//`) should be handled the same way as a single one.
5. On Windows, both `os.sep` (`\`) and `os.altsep` (`/`) may appear as trailing separators. Both should be tolerated, so the issue's `rstrip(os.sep)` alone may not be enough.
6. The line number (77) and code excerpt come from the issue. The current codebase may differ.
7. Django's existing admin-script test suite is the right place for the regression test. Its exact location is unknown.

## Tech Stack

- Python, Django core management commands (`django.core.management.templates`, the `TemplateCommand` used by `startapp`/`startproject`)
- Supported Python and Django versions: unknown

## Commands

- Build: not applicable / unknown
- Test: unknown (Django's test-runner invocation is not shown in the issue)
- Lint: unknown
- Reproduce: `django-admin startapp name directory/`, where `directory/` is an existing directory

## Project Structure

- `django/core/management/templates.py` → template-based command logic, the location of the bug (from the issue)
- Test location for admin scripts / `startapp`: unknown
- Release notes / docs location: unknown

## Code Style

- Follow existing Django core code conventions in `templates.py`. No snippet beyond the issue's excerpt is available.
- Prefer standard-library path handling (`os.path` or the equivalent already used in the module) over ad-hoc string manipulation where practical.

## Testing Strategy

- Add a regression test for `startapp` with a target directory ending in a separator. It should assert that the command succeeds and creates the app files in that directory.
- Keep or confirm existing tests:
  - A target with no trailing separator still works.
  - A genuinely invalid directory name, such as one that is not a Python identifier, still raises the same `CommandError`.
- Use whatever framework and location Django's existing admin-script tests use (unknown).
- If feasible, cover Windows-style separators, or document them as untested.

## Boundaries

**Always:**
- Keep the fix minimal and local to target-name validation.
- Preserve the existing error message and behaviour for invalid names.
- Add a regression test.

**Ask first:**
- Changing behaviour of `startproject` or other `TemplateCommand` users.
- Normalising the target path globally rather than only for validation.
- Adding release notes or docs entries, and choosing which release.

**Never:**
- Weaken or remove identifier validation for directory names.
- Change public command signatures or options.
- Remove or alter existing tests without approval.

## Success Criteria

- [ ] `startapp name directory/` succeeds and generates the app into `directory`, provided `directory` exists and is otherwise valid.
- [ ] `startapp name directory//` (multiple trailing separators) succeeds the same way.
- [ ] `startapp name directory` (no trailing separator) behaves exactly as before.
- [ ] An invalid directory name, with or without a trailing separator, still raises `CommandError` with the existing message, naming the real directory name rather than `''`.
- [ ] A regression test fails before the fix and passes after it.
- [ ] The full existing admin-script / management test suite passes.

## Open Questions

1. Should both `os.sep` and `os.altsep` be stripped on Windows, or only `os.sep` as the issue proposes?
2. What should happen when the target is a filesystem root (`/`, `C:\`)? After stripping, its basename is empty. Should it keep failing with the current error, or get a clearer message?
3. How should targets like `.` or `..` (and `./`) be treated? `basename` returns `.`/`..`, which fails identifier validation. Is that existing behaviour in scope?
4. Should the fix also normalise the target used for file generation, or touch validation only?
5. Does this fix need a release note, and should it be backported to any maintained release branch?
6. What are the exact test command and test file location for `startapp` tests in this repository?