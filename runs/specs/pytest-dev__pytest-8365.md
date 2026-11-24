# Spec: Robust `basetemp` directory creation when the username contains characters illegal in directory names

## Assumptions

1. The affected code is pytest's temporary-directory machinery behind the `tmpdir`, `tmpdir_factory` and `tmp_path_factory` fixtures. The issue says these derive the default `basetemp` from `getpass.getuser()`.
2. The default `basetemp` follows the pattern `<system temp dir>/pytest-of-<user>/...`. This is inferred from the traceback path `C:\Users\john_doe\AppData\Local\Temp\pytest-of-contoso\john_doe`.
3. The failure happens because the username `contoso\john_doe` contains a path separator (`\`). Windows treats it as a nested path whose parent (`pytest-of-contoso`) does not exist, so `mkdir` raises `FileNotFoundError` (WinError 3).
4. `getpass.getuser()` reads environment variables such as `LOGNAME` before asking the OS. That is why `set LOGNAME=contoso\john_doe` reproduces the bug without SSH.
5. The reported version is pytest 6.2.2, and the problem is assumed to still exist on the current development branch.
6. The fix must not change behavior for usernames that are already valid directory names.
7. When the user explicitly passes `--basetemp`, that value is used and the username is not consulted, so explicit `--basetemp` is out of scope.
8. Other characters could also be invalid in a path component on some platform: `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, control characters, and Windows-reserved names. These are assumed to be in scope as far as they break directory creation, but the minimum required case is the path separator.

## Objective

Using `tmpdir`, `tmpdir_factory`, `tmp_path_factory` or `tmp_path` must not fail just because the username returned by `getpass.getuser()` can't be used as a single directory-name component.

**Who is affected:** users whose reported username is not a valid single path component. Typical examples:
- Windows domain users logged in over OpenSSH for Windows, where the username is `DOMAIN\user`.
- Anyone whose `LOGNAME`, `USER`, `LNAME` or `USERNAME` environment variable contains such characters.

**User stories:**

- As a Windows domain user logged in via SSH, I can run tests that use `tmpdir`/`tmp_path` without a `FileNotFoundError`.
- As a user with a normal username, I see no change in the location or naming of my pytest temp directories.

## Tech Stack

- Python and pytest. The report uses Python 3.8 and pytest 6.2.2. The project's supported Python range is unknown.
- Standard library modules involved: `getpass`, `pathlib`, `tempfile` (assumed).

## Commands

Unknown. The repository is not visible, and the build, test and lint commands are not stated in the issue.

- Build: unknown
- Test: unknown (presumably pytest's own test suite; exact invocation unknown)
- Lint: unknown

Manual reproduction from the issue, run in Windows `cmd`:

```bat
echo def test_tmpdir(tmpdir):>test_tmp.py
echo   pass>>test_tmp.py
set LOGNAME=contoso\john_doe
py.test test_tmp.py
```

## Project Structure

Unknown. These locations are not visible from the issue:
- the module that computes `basetemp` and calls `getpass.getuser()`
- the corresponding test file
- the changelog location and format

## Code Style

Unknown. No code snippets are available from the repository. Follow the existing conventions of the module that implements the temp-path factories.

## Testing Strategy

- **Framework:** pytest's own test suite. The exact files and fixtures are unknown.
- **Unit level:** test the username-to-directory logic in isolation by simulating a username that contains illegal characters. For example, set the `LOGNAME`/`USER` environment variables via `monkeypatch`, or patch `getpass.getuser`.
- **Integration level:** run a test that uses `tmpdir`/`tmp_path` with a username such as `contoso\john_doe`, and assert that it passes and that the temp directory exists.
- **Platform coverage:**
  - The backslash case is Windows-specific in its failure mode.
  - A `/`-containing username exercises the analogous failure on POSIX, if that is considered in scope (see Open Questions).
  - Tests should run on whatever CI platforms the project uses (unknown).
- **Regression:** existing tmpdir tests must still pass unchanged.
- **Coverage expectations:** unknown.

## Boundaries

**Always:**
- Keep the existing directory naming unchanged for valid usernames.
- Add a regression test that reproduces the reported failure.
- Run the existing temp-dir tests before committing.
- Add a changelog entry if the project requires one (format unknown).

**Ask first:**
- Changing the `pytest-of-<user>` naming scheme beyond what is needed for invalid usernames.
- Introducing new configuration options or environment variables.
- Changing how `getpass.getuser()` failures are handled in general.
- Adding dependencies.

**Never:**
- Change behavior when `--basetemp` is explicitly provided.
- Weaken the existing security properties of the per-user temp root (ownership and permissions), whatever they currently are.
- Remove or skip existing tests.

## Success Criteria

1. With `LOGNAME=contoso\john_doe` on Windows, the reproduction above passes. There is no `FileNotFoundError`, and the `tmpdir` fixture yields an existing, writable directory.
2. `tmpdir_factory.mktemp('foobar')` and `tmp_path_factory.mktemp('foobar')` succeed under the same condition.
3. The per-user temp root is created as a single directory directly under the system temp directory. It is not a nested path derived from components of the username.
4. For a username that is a valid directory name (e.g. `john_doe`), the resulting `basetemp` path is identical to current behavior.
5. A new automated test reproduces the original failure without the fix and passes with it.
6. All existing tests in the temp-dir test suite pass.

## Open Questions

1. When the username is invalid, which behavior is preferred?
   - (a) Fall back to a fixed placeholder (e.g. `pytest-of-unknown`).
   - (b) Sanitize the username, e.g. replace illegal characters with `_` or take only the part after `\`.
   - (c) Use another derived identifier.

   Option (b) risks collisions between different users, which may matter for shared temp directories.
2. Which characters count as "illegal"? Options are:
   - only path separators
   - the full Windows-invalid set
   - a platform-dependent check
   - an empirical check, i.e. attempt `mkdir` and fall back on error
3. Should a `/` in the username on POSIX be handled as well, or is the fix limited to Windows?
4. Is the existing handling of `getpass.getuser()` raising an exception relevant, and should the new fallback share it?
5. Should pytest emit a warning when it falls back or sanitizes, so users know why their temp directory name differs?
6. Are there other places in pytest that use `getpass.getuser()` to build paths (e.g. cache directories) that should get the same treatment? This is unknown without repository access.
7. Which pytest versions or branches should receive the fix, and is a changelog entry required? If so, in what format?