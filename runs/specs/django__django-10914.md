# Spec: Default `FILE_UPLOAD_PERMISSIONS` to `0o644`

## Objective

Files saved through `FileSystemStorage` currently get inconsistent permissions when `FILE_UPLOAD_PERMISSIONS` is not set. The result depends on which temporary upload class handled the data:

| Upload path (default `FILE_UPLOAD_HANDLERS`) | Typical size | Resulting permissions (reported) |
|---|---|---|
| In-memory uploaded file (reporter calls it `MemoryUploadedFile`) | Small | Derived from process umask (e.g. `0o644`) |
| `TemporaryUploadedFile` (`tempfile.NamedTemporaryFile` + `os.rename`) | Large | `0o600` on some systems (CentOS 7.4.1708, Python 3.6.5) |

Python's `tempfile` creates files as `0o600` for security reasons. Renaming the file keeps that mode, so a file's permissions depend on its upload size. Nothing in the File Uploads documentation warns about this.

**Goal:** Uploaded files get predictable, consistent permissions by default, whatever their size and whichever upload handler was used.

**Users affected:**
- Django developers and operators who deploy file uploads.
- Downstream consumers of uploaded files, such as web servers serving media and other processes or users that need to read those files.

**Requested changes (from the issue title and description):**
1. Change the default value of the `FILE_UPLOAD_PERMISSIONS` setting to `0o644`.
2. Document the permission behavior. The docs should warn that permissions can differ between in-memory and temporary-file uploads when no explicit permission is configured, or explain the new default, or both.

## Assumptions

1. The setting is `FILE_UPLOAD_PERMISSIONS`, plural, as written in the description. "FILE_UPLOAD_PERMISSION" in the title is a typo.
2. The current default of `FILE_UPLOAD_PERMISSIONS` is "unset" (`None`), meaning Django does not `chmod` saved files. The issue implies this but does not state it.
3. When `FILE_UPLOAD_PERMISSIONS` is set, `FileSystemStorage` applies it to every saved file, so both upload paths end up with the same mode. Changing the default is therefore enough to give consistent behavior.
4. Users who explicitly set `FILE_UPLOAD_PERMISSIONS`, including to `None`, keep their configured behavior. Explicitly setting `None` still restores the old "no chmod" behavior.
5. The change is in scope only for `FileSystemStorage` and the setting's default. Third-party storage backends and `FILE_UPLOAD_DIRECTORY_PERMISSIONS` are out of scope.
6. This is a behavior change in a default setting, so it requires a release note and documentation updates (setting reference and File Uploads page), not only a code change.
7. `0o644` is acceptable as a default from a security standpoint: world-readable, owner-writable, consistent with typical umask `022` results for in-memory uploads.

## Tech Stack

- Python and Django. The supported versions and target release for this change are **unknown**.
- Python standard library modules `tempfile` and `os`, as referenced in the issue.

## Commands

All unknown; repository not visible.
- Build: unknown
- Test: unknown (Django's test runner invocation not provided)
- Lint: unknown
- Docs build: unknown

## Project Structure

Unknown; repository not visible. Areas expected to be touched, by concept rather than verified path:
- Global default settings definition: location of the `FILE_UPLOAD_PERMISSIONS` default
- `FileSystemStorage` implementation
- Settings reference documentation for `FILE_UPLOAD_PERMISSIONS`
- File Uploads topic documentation
- Release notes for the target version
- Tests for file storage / file uploads

## Code Style

Unknown. Follow the existing conventions of the Django codebase. Use octal literals in the `0o644` form, as written in the issue.

## Testing Strategy

The framework and test locations are unknown; use the project's existing test suite for file storage and uploads. Required coverage:

- **Default value:** With no user override, the setting's default equals `0o644`.
- **Large upload path:** A file large enough to use `TemporaryUploadedFile`, saved via `FileSystemStorage` with default settings, ends up with mode `0o644`.
- **Small upload path:** A small in-memory upload saved with default settings ends up with mode `0o644`.
- **Override:** An explicit `FILE_UPLOAD_PERMISSIONS` value, such as `0o640`, is applied instead of the default.
- **Opt-out:** Explicitly setting `FILE_UPLOAD_PERMISSIONS = None` restores the previous behavior, i.e. no chmod is applied.
- **Platform caveat:** Permission assertions are POSIX-specific. Tests should follow whatever skip conventions exist for Windows. Those conventions are unknown.

## Boundaries

- **Always:**
  - Keep explicit user configuration authoritative.
  - Update the settings reference, the File Uploads docs, and the release notes together with the default change.
  - Add tests covering both upload paths.
- **Ask first:**
  - Changing `FILE_UPLOAD_DIRECTORY_PERMISSIONS` defaults.
  - Altering the `chmod` mechanism in `FileSystemStorage`.
  - Backporting to maintenance releases.
  - Adding a deprecation period instead of a direct default change.
- **Never:**
  - Change permissions of files created outside the upload/storage save path.
  - Weaken security of temporary files while they are still temporary, i.e. before the move.
  - Silently ignore an explicit `None` setting.

## Success Criteria

1. With default settings, a file saved by `FileSystemStorage` has mode `0o644`. This holds for both in-memory and temporary-file uploads, on systems where `tempfile` creates `0o600` files.
2. Upload size no longer affects final file permissions under default settings.
3. Explicit `FILE_UPLOAD_PERMISSIONS` values, including `None`, behave as before.
4. The settings reference shows the new default `0o644`. It also explains that `None` leaves permissions platform-dependent, potentially `0o600` for large uploads.
5. The File Uploads documentation covers permission behavior, including the in-memory vs. temporary-file inconsistency when permissions are unset.
6. The release notes call out the default change as a backwards-incompatible or behavior change.
7. New and existing tests pass.

## Open Questions

1. Should this land as a direct default change in the next feature release, or go through a deprecation/warning period first?
2. Is a documentation-only fix wanted for currently supported releases, i.e. the warning the reporter originally asked for, in addition to the default change?
3. Is `0o644` the agreed value, or should something more restrictive be considered (e.g. `0o640`) for multi-user hosts?
4. Should `FILE_UPLOAD_DIRECTORY_PERMISSIONS` get a matching non-`None` default for consistency, or stay out of scope?
5. How should the new default interact with the process umask? Is the mode applied exactly via chmod, regardless of umask?
6. What are the expected behavior and test handling on Windows, where POSIX modes are largely not meaningful?
7. Are there existing GitHub reports or prior tickets to reference? The reporter mentions GitHub reports but gives no links.
8. What are the target Django version, supported Python versions, and the exact test, lint, and docs commands for this repository?