# Spec: StatReloader resilience to "ValueError: embedded null byte" during path resolution

## Objective

When running `manage.py runserver` with the auto-reloader (`StatReloader`), the development server very intermittently crashes with `ValueError: embedded null byte`. The traceback shows the error raised from `pathlib.Path.resolve()` → `os.readlink()`, called from `iter_modules_and_files` in `django/utils/autoreload.py` (line 132 in the reporter's version: `results.add(path.resolve().absolute())`).

The reporter cannot reproduce it on demand. They suspect a non-deterministic filesystem condition, possibly a Samba mountpoint under `/Users` that is not yet connected. They note that `pathlib` was not used in this code path before Django 2.2, so this is a regression in user-visible behavior.

**Users:** Developers running the Django development server with auto-reload enabled.

**What we're building:** A change in behavior so that a single module path that cannot be resolved (here, because of `ValueError: embedded null byte`) does not crash the reloader loop. The reloader keeps watching all other files.

**Success looks like:** The dev server never terminates because one watched path raises `ValueError` during resolution. All other watched files still trigger reloads as before.

### Acceptance criteria / user stories

- As a developer, when one module's path raises `ValueError` ("embedded null byte") during resolution, the reloader skips that path and keeps running.
- As a developer, every other module and extra file that resolves correctly is still watched and still triggers reloads.
- As a maintainer, existing handling of missing files (paths that do not exist) is unchanged.

## Assumptions

1. The fix targets Django's `django/utils/autoreload.py`, specifically the path-resolution step in `iter_modules_and_files`. This is the only file and function named in the traceback.
2. The root cause is an environment or OS condition outside Django's control. Candidates include a transient null byte returned by `os.readlink` on a network mount, or a CPython/pathlib quirk on Python 3.6 / OS X 10.11. Django should tolerate it, not diagnose it.
3. Skipping a path that cannot be resolved is acceptable. It is a single path, and the error comes from a symlink lookup on a parent directory (`/Users`) rather than from a user source file. Losing the ability to watch that path is better than crashing.
4. The scope does **not** include replacing `pathlib` with `os.path` across the autoreloader. The reporter raised this, citing performance, but it is a separate change with a different objective.
5. The skip is silent, or at most logged at debug level. A crash is not acceptable.
6. Other code in the reloader that calls `resolve()` (for example on directories or extra files) may be exposed to the same error. Whether to cover those sites is an open question. The baseline scope is the call site in the traceback.
7. The supported Python versions are those supported by the targeted Django branch. These are unknown from the issue. The report itself uses Python 3.6.2.

## Tech Stack

- Python (the reporter uses 3.6.2 via pyenv). The supported range for the target branch is unknown.
- Django 2.2+. The exact target branch or version is unknown.
- Standard library: `pathlib`, `os`.
- Platform in the report: macOS (OS X 10.11). The issue does not say whether the error occurs on other platforms.

## Commands

All commands are unknown because the repository is not visible. To be filled in:

- Test (full suite): unknown
- Test (autoreload tests only): unknown
- Lint: unknown
- Reproduction (manual): `python manage.py runserver` with auto-reload enabled. This is not deterministically reproducible.

## Project Structure

Known from the traceback:

- `django/utils/autoreload.py` → reloader implementation (`iter_all_python_module_files`, `iter_modules_and_files`, `StatReloader.snapshot_files`, `watched_files`, `run_loop`, `tick`)
- `django/core/management/commands/runserver.py` → invokes `autoreload.run_with_reloader`

Unknown:

- Location of the existing autoreload tests.

## Code Style

The issue contains no style example. Follow the existing conventions in `django/utils/autoreload.py`, which are not visible here. The change should be minimal and local to the resolution step, consistent with how the module already handles paths that cannot be resolved, such as missing files.

## Testing Strategy

- **Framework / location:** Use Django's existing test framework and the existing autoreload test module. The exact path and runner command are unknown.
- **Unit test (required):** Simulate `Path.resolve()` raising `ValueError("embedded null byte")` for one module path, for example via mocking. Assert all three of the following:
  - `iter_modules_and_files` does not raise.
  - The offending path is excluded from the results.
  - Other paths are still included.
- **Regression:** The existing tests for missing or nonexistent module files must still pass.
- **Manual:** None feasible, because the bug is not reproducible on demand. The mocked unit test is the primary verification.
- **Coverage:** Every new branch (the skip path) must be covered by a test.

## Boundaries

- **Always:**
  - Keep the change scoped to path-resolution error handling.
  - Add a regression test that simulates the `ValueError`.
  - Run the autoreload test suite before submitting.
- **Ask first:**
  - Extending the same handling to other `resolve()` call sites in the reloader.
  - Adding logging or warnings for skipped paths.
  - Catching exception types broader than `ValueError`.
  - Backporting to older release branches.
- **Never:**
  - Replace `pathlib` with `os.path` throughout the module as part of this fix.
  - Swallow exceptions so broadly that real bugs are hidden, for example a bare `except`.
  - Change reloader behavior for paths that resolve correctly.
  - Remove or weaken existing tests.

## Success Criteria

1. When `Path.resolve()` raises `ValueError` for any one module path, `iter_modules_and_files` completes without raising and returns all other resolvable paths.
2. `StatReloader`'s loop (`run_loop` → `tick` → `snapshot_files`) continues across ticks when such an error occurs.
3. The new unit test reproduces the original failure on unpatched code and passes after the fix.
4. All existing autoreload tests pass unchanged.
5. No change in watched-file results for environments where the error does not occur.

## Open Questions

1. **Root cause:** Should we investigate further, for example the Samba mount hypothesis or a CPython pathlib/readlink bug on 3.6 or macOS? Or is tolerating the error the agreed resolution?
2. **Scope of handling:** Should only the `iter_modules_and_files` call site be protected, or every `resolve()` call in the autoreloader (watched directories, extra files, `sys.path` entries)?
3. **Visibility:** Should skipped paths be logged? If so, at what level?
4. **Exception breadth:** Should we catch only `ValueError`, or also related `OSError` variants that a disconnected network mount could raise?
5. **pathlib performance:** The reporter claims `pathlib` is slow and should be removed. Should this be tracked as a separate issue?
6. **Target branches:** Which Django versions should receive the fix (main only, or backports to 2.2.x)?
7. **Commands:** What are the exact test, lint, and runner commands and the test file locations in the repository? These are unknown from the issue.
8. **Platform:** Has this been observed outside macOS or on Python versions newer than 3.6.2?