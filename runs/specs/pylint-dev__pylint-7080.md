# Spec: `--recursive=y` must honor `ignore-paths`

## Objective

With `--recursive=y`, pylint lints files that match the `ignore-paths` patterns in the user's configuration. In the reported case, generated files under `src/gen/` are linted even though `ignore-paths` contains `^src/gen/.*$`.

**User:** A pylint user who runs `pylint --recursive=y <dir>` and configures `ignore-paths` in `pyproject.toml` (`[tool.pylint.MASTER]`) to exclude generated or vendored code.

**Why it matters:** Generated code floods the output with unactionable messages. In the report this pushed the score to -158.32/10. It also makes `ignore-paths` unusable together with recursive discovery.

**Observed (pylint 2.14.1, astroid 2.11.5, Python 3.9.6, Windows 10.0.19044):**
- `pylint --recursive=y src/` reports messages for `src\gen\about.py`, `src\gen\design.py`, `src\gen\resources_rc.py`, `src\gen\settings.py` and `src\gen\update_checker.py`.
- The reported paths use Windows separators (`src\gen\...`). The configured pattern uses forward slashes (`^src/gen/.*$`).
- `R0401 cyclic-import` messages are attached to `src\gen\update_checker.py:1:0`. The cycles listed involve non-generated modules such as `AutoSplit`, `error_messages` and `region_selection`. This placement may be a side effect: the ignored file is the last module linted.

**Expected:** No file whose path matches an `ignore-paths` pattern is linted or reported when discovery is recursive.

**User stories:**
- As a user, when I run `pylint --recursive=y src/` with `ignore-paths = ["^src/gen/.*$"]`, files under `src/gen/` produce no messages.
- As a Windows user, a forward-slash `ignore-paths` pattern excludes the same files it would exclude on POSIX. This assumes the project confirms that is the intended contract (see Open Questions).

## Tech Stack

- Python. The reporter uses 3.9.6. The supported range for the fix is unknown.
- pylint 2.14.1 as reported. The target branch or version for the fix is unknown.
- astroid 2.11.5 as reported.
- Configuration source: `pyproject.toml`, `[tool.pylint.MASTER]` section.

## Commands

The project's own commands are unknown because the repository is not visible.

```
Reproduce (from issue): pylint --recursive=y src/
Build:  unknown
Test:   unknown
Lint:   unknown
```

## Project Structure

Unknown. The repository is not visible.

- Location of recursive file discovery: unknown
- Location of `ignore-paths` matching: unknown
- Location of tests for file discovery or ignore options: unknown
- Location of functional or regression test fixtures: unknown

Reporter's layout, from the issue output:
```
src/
  region_selection.py      → linted, expected
  ... other app modules    → linted, expected
  gen/                     → auto-generated, should be ignored
    about.py
    design.py
    resources_rc.py
    settings.py
    update_checker.py
```

## Code Style

Unknown. Follow the existing conventions in the pylint codebase. No snippet is available from the issue.

## Testing Strategy

The test framework and test locations are unknown. Required coverage:

- **Regression test, recursive mode:** create a directory tree with an ignored subdirectory. Configure `ignore-paths` with a pattern for it. Run with `--recursive=y` on the parent directory. Assert that no module from the ignored subdirectory is linted or reported.
- **Separator handling:** the test must pass when discovered paths use OS-native separators. If CI does not run on Windows, the test should exercise the separator case in some other way, for example by simulating backslash paths. The mechanism is unknown.
- **Non-recursive parity:** the same `ignore-paths` configuration gives the same set of linted files whether the directory is passed with or without `--recursive=y`. This holds only if the non-recursive behavior is confirmed correct today.
- **No over-ignoring:** files outside the ignored pattern are still linted. In the report, `src/region_selection.py` must still produce `R0914`.
- **Config source:** at least one test loads `ignore-paths` from a `pyproject.toml` `[tool.pylint.MASTER]` section, as in the report.
- **Existing tests:** the existing `ignore`, `ignore-patterns` and `ignore-paths` tests must keep passing.

## Boundaries

- **Always:**
  - Reproduce the bug with a failing test before changing behavior.
  - Keep `ignore-paths` semantics identical between recursive and non-recursive modes.
  - Run the full existing test suite before committing.
- **Ask first:**
  - Changing the documented contract of `ignore-paths`, such as normalizing separators before matching, or which path form (relative or absolute) patterns match against.
  - Changing how `ignore` and `ignore-patterns` behave in recursive mode.
  - Changing which file `cyclic-import` messages are attached to.
  - Adding dependencies.
- **Never:**
  - Silently change the matching semantics of existing user patterns without a changelog or documentation entry.
  - Remove or weaken existing ignore-related tests.
  - Fix this only for Windows or only for POSIX if the root cause is shared.

## Success Criteria

1. With `ignore-paths = ["^src/gen/.*$"]` and `pylint --recursive=y src/`, no message is reported for any file under `src/gen/` on POSIX or on Windows.
2. Files under `src/gen/` are not parsed or linted at all. Suppressing their output is not enough.
3. Files outside `src/gen/` are still linted and reported as before.
4. Recursive and non-recursive runs over equivalent inputs apply `ignore-paths` identically.
5. A regression test covering criteria 1–3 fails before the fix and passes after it.
6. No existing tests regress.
7. If the fix changes how patterns are matched (separator normalization, relative vs. absolute paths), the documentation for `ignore-paths` states the behavior explicitly.

## Assumptions

1. The bug is in pylint's handling of `ignore-paths` during recursive discovery. The user's configuration is valid and being read. Other options from the same section are not shown, so this is not confirmed.
2. A likely contributor is that recursive discovery yields OS-native paths (`src\gen\about.py` on Windows) that are matched against forward-slash regexes. This is inferred only from the separators in the output. It is not verified, and recursive mode may skip `ignore-paths` entirely regardless of OS.
3. The expected behavior is that ignored files are never linted. Filtering their output afterwards would not meet this.
4. `ignore-paths` already behaves correctly without `--recursive=y`. The issue does not state this.
5. The `cyclic-import` messages attached to `src\gen\update_checker.py` will move or disappear once the generated files are no longer linted. They are a symptom, not a separate bug in scope here.
6. The `MASTER` section name in `pyproject.toml` is a supported way to set this option in 2.14.1.

## Open Questions

1. Does the bug reproduce on POSIX, or only on Windows? This tells us whether the root cause is separator handling or recursive mode skipping `ignore-paths` altogether.
2. Does `pylint src/gen/about.py` or `pylint src/` without `--recursive=y` honor the same `ignore-paths` on the reporter's machine?
3. What is the intended contract for `ignore-paths` patterns on Windows?
   - Should users write forward slashes, backslashes, or should pylint normalize?
   - Should patterns match relative paths (relative to what: the CWD, or the argument?) or absolute paths?
4. Are `ignore` and `ignore-patterns` also ignored in recursive mode? Should they be fixed in the same change or tracked separately?
5. Should ignored directories be pruned during traversal, so their contents are never visited? Or should files be filtered after discovery? This affects performance on large generated trees.
6. Is attaching project-wide `cyclic-import` messages to the last linted module intended? Does it need its own issue?
7. Which pylint branch or version should receive the fix? Is a backport to 2.14.x expected?
8. Does CI run on Windows, so the separator case can be tested natively?