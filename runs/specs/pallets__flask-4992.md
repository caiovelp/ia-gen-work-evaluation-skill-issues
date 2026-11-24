# Spec: File Mode Parameter for `flask.Config.from_file()`

## Objective

Let `flask.Config.from_file()` open the config file in **binary mode** as well as text mode. Loaders that need a binary file object, such as Python 3.11's `tomllib.load`, can then be passed directly:

```python
app.config.from_file("config.toml", tomllib.load, mode="b")   # API shape from the issue; name not final
```

**Problem today:** `from_file()` always opens the file in text mode. With `tomllib.load` this fails:

```
TypeError: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`
```

The current workaround means opening the file yourself and repeating the root-path joining that `from_file()` already does:

```python
with open(os.path.join(app.config.root_path, "config.toml"), "rb") as file:
    app.config.from_mapping(tomllib.load(file))
```

**Users:** Flask application developers who load config from files. This mainly means TOML users on Python 3.11+, plus any loader that expects bytes.

**User stories**
- As a Flask developer, I can load a TOML config file in one call to `from_file()` using `tomllib.load`.
- As an existing user of `from_file()` with `json.load` or other text loaders, my code keeps working with no changes.

## Assumptions

1. Scope is limited to `flask.Config.from_file()`. No other `Config.from_*` methods change.
2. The new parameter is **optional and keyword-usable**. Its default keeps the current text-mode behaviour, so the change is fully backward compatible.
3. Path handling stays the same in both modes:
   - relative paths are joined with `Config.root_path`
   - the existing `silent` handling of missing files applies
4. Behaviour after loading stays the same in both modes. The loader's returned mapping goes through `from_mapping()`, so the existing key filtering still applies.
5. Flask will **not** depend on `tomllib` or any TOML library. The caller supplies the loader. `tomllib` appears only in docs and examples.
6. Text-mode encoding behaviour stays exactly as it is today. I can't see the current code, so whether an explicit encoding is passed is **unknown**.
7. In binary mode, no encoding argument is passed to `open()`, since that would raise an error.
8. The new parameter is documented in the method docstring with a "changed in version" note. The exact version number is **unknown**.
9. A changelog entry is expected, following the project's usual practice.

## Tech Stack

- Python, the Flask library itself.
- Supported Python versions: **unknown**. This matters because `tomllib` exists only on 3.11+.
- No new runtime dependencies.

## Commands

All **unknown**, since the repository is not visible. Fill these in from the project's contributor docs or CI config.

```
Install (dev): unknown
Test:          unknown (likely pytest; unconfirmed)
Lint/format:   unknown
Type check:    unknown
Docs build:    unknown
```

## Project Structure

**Unknown.** The repository is not visible. Relevant locations to identify:

| What | Location |
|---|---|
| The module defining `flask.Config` / `from_file()` | unknown |
| Existing tests for `Config.from_file()` and their fixture/static config files | unknown |
| Config documentation page(s) showing `from_file()` examples | unknown |
| Changelog file | unknown |

## Code Style

**Unknown.** Follow the conventions already used in the `Config` class:
- type annotations
- docstring format, including "versionchanged" style notes
- parameter naming

This spec does not include a code snippet, because none is visible.

## Testing Strategy

- **Framework:** unknown (pytest presumed; confirm against the repo).
- **Unit tests for `Config.from_file()`:**
  - Default call with a text loader (e.g. `json.load`) behaves exactly as before. This is the regression check.
  - Binary-mode call with a loader that requires bytes loads the expected keys into config.
    - On Python 3.11+, `tomllib.load` with a TOML fixture file.
    - The test must be skipped on Pythons without `tomllib`, or must use a version-independent bytes-asserting loader. See Open Questions.
  - Binary mode with a missing file and `silent=True` returns `False` and does not raise.
  - Binary mode with a missing file and `silent=False` raises the same error type and message format as text mode.
  - Only valid keys are loaded in binary mode, following the existing `from_mapping()` filtering.
  - Invalid values for the new parameter: expected behaviour depends on how the API-shape question below is resolved.
- **Docs:** if a docs build exists, the updated docstring and examples render without warnings.
- **Coverage:** every code path added for the new parameter is exercised.

## Boundaries

- **Always:**
  - keep the default behaviour identical to today's
  - add tests for both modes
  - update the docstring, the config docs example and the changelog
  - run the full test suite before committing
- **Ask first:**
  - choosing the final parameter name and type (see Open Questions)
  - adding TOML as a documented or recommended config format in the narrative docs
  - any change to text-mode encoding
  - changing the behaviour of other `Config.from_*` methods
- **Never:**
  - add `tomllib`, `tomli` or any TOML package as a Flask dependency
  - change the existing signature in a way that breaks positional callers
  - remove or weaken existing `from_file()` tests

## Success Criteria

1. `app.config.from_file("config.toml", tomllib.load, <binary-mode argument>)` loads the TOML file's uppercase keys into `app.config` on Python 3.11+, with no `TypeError`.
2. Every existing call form of `from_file()` (path, load function, `silent`) behaves identically with no new argument given. The existing tests pass unchanged.
3. Relative paths resolve against `root_path` in binary mode, just as in text mode.
4. `silent=True` handling of missing files works the same in binary mode.
5. The method docstring documents the new parameter, its default, and a TOML example, with a version-change note.
6. A changelog entry describes the addition.
7. New tests cover the binary-mode path and pass on all supported Python versions. Version-specific tests are skipped where `tomllib` is unavailable.

## Open Questions

1. **API shape.** The issue proposes `mode="b"`. Which form is preferred?
   - (a) `mode: str = "t"` accepting `"t"`/`"b"`, as proposed
   - (b) a boolean such as `text: bool = True`
   - (c) a full `open()` mode string like `"rb"`

   A boolean (b) rules out invalid values. A string (a/c) is closer to `open()`, but needs validation and raises the question of what to do with values like `"w"` or `"rb+"`.
2. **Invalid values.** If a string is chosen, should invalid modes raise `ValueError` right away, or be passed through to `open()`?
3. **Keyword-only?** Should the new parameter be keyword-only to avoid positional ambiguity with `silent`?
4. **Supported Python versions.** If 3.11+ is not the floor, how should tests and doc examples handle `tomllib`'s absence? Options are to skip, or to mention the `tomli` backport in the docs only.
5. **Text-mode encoding.** Does `from_file()` currently pass an explicit `encoding`? Should that be in scope for this change?
6. **Docs scope.** Should the narrative config docs gain a TOML example section, or only the docstring?
7. **Target release.** What version number goes in the "changed in version" note and the changelog?