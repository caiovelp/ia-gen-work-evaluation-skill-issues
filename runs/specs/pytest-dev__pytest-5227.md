# Spec: Improve the Default Logging Format

## Assumptions

1. The project is a Python tool or library that defines a module-level constant `DEFAULT_LOG_FORMAT`. The issue does not name the project or the file. It reads like the logging/log-capture plugin of a test runner such as pytest's `logging` plugin, but this is **unconfirmed**.
2. `DEFAULT_LOG_FORMAT` is a standard library `logging` `%`-style format string. It applies only when the user has not set a format explicitly, for example through a CLI option or config key.
3. The format is used wherever logs are shown by default: captured log reports, live/CLI logging, log file output, or any subset of these. Which outputs use it is **unknown**.
4. Users who set their own format are unaffected. Only the default output changes.
5. `%(name)s` means the logger name, which is usually the module's `__name__`, as the issue's examples show (`django.db.backends`, `multipart.multipart`).
6. The format the issue proposes is the starting candidate, not a final decision:
   `"%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"`
7. Adding the relative path or substituting `$VIRTUAL_ENV` (the parenthetical idea in the issue) is **out of scope** unless approved. It is listed under Open Questions.
8. A related default date format constant, if one exists, is not changed.

## Objective

**What:** Change the default log line format so each line shows the **logger name** (`%(name)s`) along with the filename and line number. Today only the base filename appears.

**Why:** The base filename alone is often ambiguous. Many packages have a `utils.py`. With the logger name, the reader can tell which package or module emitted a record (e.g. `django.db.backends`) without guessing. Putting the level first and using the compact `name:file:line` form also makes lines easier to scan and grep.

**Users:** Developers who read log output produced by the tool under its default settings.

**Current output:**
```
utils.py                   114 DEBUG    (0.000) SELECT ... args=(2,)
multipart.py               604 DEBUG    Calling on_field_start with no data
```

**Proposed output:**
```
DEBUG    django.db.backends:utils.py:114 (0.000) SELECT ... args=(2,)
DEBUG    multipart.multipart:multipart.py:604 Calling on_field_start with no data
```

**User stories:**
- As a developer reading logs, I can see which logger or module produced each line, so I can tell apart same-named files from different packages.
- As a developer who has configured a custom log format, my output is unchanged.

## Tech Stack

- Python, standard library `logging` (format string attributes `levelname`, `name`, `filename`, `lineno`, `message`).
- Project name, supported Python versions and other dependencies: **unknown**.

## Commands

All **unknown**. The issue does not include them.

```
Build: unknown
Test:  unknown
Lint:  unknown
Dev:   unknown
```

## Project Structure

**Unknown.** The only known artifact is the constant `DEFAULT_LOG_FORMAT`. The module that defines it, the test location, and the docs location are not given in the issue. Expected touch points to locate:

- The module defining `DEFAULT_LOG_FORMAT` → unknown path
- Tests asserting on default log output → unknown path
- User docs that quote or describe the default format → unknown path
- Changelog or release notes → unknown path or convention

## Code Style

Unknown beyond the existing constant. Keep the existing style of a single module-level string constant:

```python
DEFAULT_LOG_FORMAT = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"  # current
```

Follow the project's existing conventions for naming, formatting and changelog entries. These are not visible in the issue.

## Testing Strategy

The framework and locations are **unknown**. Required coverage:

- **Unit:** the default format renders a record with logger name, filename and line number in the agreed layout. Use a fixed logger name, file and line so the expected string is exact.
- **Regression:** existing tests that assert on the old default layout (e.g. the padded `filename lineno LEVEL` columns) are found and updated on purpose. They must not be deleted.
- **Override:** when a user-supplied format is set, output does not use the new default.
- **Docs check:** any documentation example showing default output matches the new format.

## Boundaries

- **Always:**
  - Change only the *default*. User-configured formats must keep working exactly as before.
  - Update tests and docs that reference the old default in the same change.
  - Add a changelog entry that flags the visible output change.
- **Ask first:**
  - Choosing a final format that differs from the one proposed in the issue (field order, separators, padding).
  - Adding the path, relative path or `$VIRTUAL_ENV` substitution (needs a custom formatter or filter, not just a format string).
  - Changing any related default, such as the date format or the format for a specific output channel.
  - Giving live/CLI output a different default from captured or file output.
- **Never:**
  - Remove or weaken existing tests without approval.
  - Change the meaning of user-facing configuration options.
  - Add new dependencies for this change.

## Success Criteria

1. With no user log format configured, a record from logger `django.db.backends` at `utils.py` line 114, level DEBUG, message `X` renders as:
   `DEBUG    django.db.backends:utils.py:114 X`
   This assumes the issue's proposed format is approved. Otherwise it uses the approved format.
2. The level name is left-aligned and padded to 8 characters (`%(levelname)-8s`), so messages line up for standard level names.
3. Every default log line contains the logger name.
4. When a user sets a custom log format, rendered output is byte-for-byte identical to the output before the change.
5. All existing tests pass, with only deliberate updates to tests that asserted the old default.
6. Docs and changelog describe the new default and how to get the old format back. The old format string is quoted so users can restore it.

## Open Questions

1. **Which project and file?** Where is `DEFAULT_LOG_FORMAT` defined, and which outputs use it (captured reports, live/CLI logs, log files)? Should all of them change?
2. **Final format:** Is `"%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"` approved as is? Alternatives include keeping the level after the location, or dropping `filename` when it duplicates the last part of `name`.
3. **Redundancy:** When `name` already ends with the module name (e.g. `multipart.multipart:multipart.py`), is the repetition acceptable?
4. **Path information:** Is the relative or full path wanted? If so, where in the line, and should prefixes like `$VIRTUAL_ENV` or site-packages be abbreviated? This needs a custom formatter. Is it in scope now or a follow-up?
5. **Root logger:** Records from the root logger render as `root:file.py:N`. Is that acceptable?
6. **Compatibility:** Is changing default output considered breaking for users or tools that parse it? Does it need a deprecation period, a major-version release, or only a changelog note?
7. **Alignment:** The old format padded the filename (`-25s`) for column alignment. Is losing column alignment for the location field acceptable?
8. **Commands, project layout and test locations:** all unknown and need to be provided.