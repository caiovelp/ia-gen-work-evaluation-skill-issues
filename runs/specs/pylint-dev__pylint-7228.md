# Spec: Graceful handling of unsupported regex syntax (`\p{Han}`) in pylint regex options

## Objective

**Problem.** A pylint regex option such as `function-rgx` set in `.pylintrc` to a pattern containing `\p{Han}` crashes pylint during configuration parsing. The user sees an uncaught `re.error: bad escape \p at position 1` traceback and no linting happens.

**Root cause, from the traceback:**
- argparse calls `re.compile` as the option's `type` function: `type_func(arg_string)` resolves to `re.py compile`.
- This happens inside `pylint/config/arguments_manager.py::_parse_configuration_file`.
- Python's standard-library `re` module does not support Unicode property escapes (`\p{...}`), so compilation fails.
- The exception is not caught, so it escapes as a raw traceback.

**Who is affected.**
- Users who write naming-convention regexes in config files or on the command line using syntax that Python's `re` does not support.
- In this report, the user wants function names that may contain Han (CJK) characters.

**What success looks like.** Pylint never crashes with a raw Python traceback because a user-supplied regex in configuration is invalid. Exactly which outcome replaces the crash is still open (see Open Questions):

- **Option A — Clear error.** Pylint exits with a concise, user-facing message. The message names the offending option, the bad pattern, and the underlying regex error. It is shown instead of a traceback, and the process exits with a non-zero status.
- **Option B — Support `\p{...}`.** Pylint accepts the pattern, compiling it with an engine that supports Unicode properties (e.g. the third-party `regex` package). It then lints using it.

Either option must also tell users how to get the behavior they want. Han characters can already be matched with a stdlib-compatible pattern, for example `[\u4e00-\u9fff]`. Under Option A, this belongs in the error output or the documentation.

**User stories**
- As a user with an invalid regex in `.pylintrc`, I get a readable error that tells me which option and pattern are wrong, not an internal traceback.
- As a user writing naming conventions for non-ASCII identifiers, I can find out how to express the character class I need.

## Assumptions

1. The crash is not limited to `function-rgx`. It applies to every option whose argparse `type` is `re.compile`, or which otherwise compiles user regexes during config parsing. Examples: other `*-rgx` options, `ignore-patterns`, and possibly `good-names-rgxs` / `bad-names-rgxs`, which may use a different, comma-separated regex type.
2. The same failure occurs whether the pattern comes from `.pylintrc`, `setup.cfg`, `pyproject.toml`, or the command line. All of them go through the same argparse parsing path.
3. The reported version is 2.14.4. The regression appeared with the argparse-based config system introduced in 2.14. Earlier optparse-based versions may have behaved differently; this has not been verified.
4. The minimum fix in scope is Option A, a clear error. Option B adds a dependency and changes regex semantics, so it is treated as "Ask first".
5. Python 3.9 is the reporter's environment, but the fix must work on all Python versions pylint supports. The supported range is unknown from the issue.

## Tech Stack

- Python. The supported range is unknown; the reporter uses 3.9.13.
- pylint 2.14.4 and astroid 2.11.7, as reported.
- Config parsing uses stdlib `argparse`, with `re.compile` as an option type, as the traceback shows.
- Other dependencies and their versions are unknown.

## Commands

All commands below are unknown and not visible in the issue. They must be confirmed from the repository.

| Purpose | Command |
|---|---|
| Build | Unknown |
| Test | Unknown (likely pytest-based; unverified) |
| Lint | Unknown |
| Reproduce | Run `pylint` in a directory containing a `.pylintrc` with `function-rgx=[\p{Han}a-z_][\p{Han}a-z0-9_]{2,30}$` (from the issue) |

## Project Structure

Only these paths are known, from the traceback:

```
pylint/__init__.py                       → run_pylint entry point
pylint/lint/run.py                       → Run.__init__ calls _config_initialization
pylint/config/config_initialization.py   → _config_initialization calls linter._parse_configuration_file
pylint/config/arguments_manager.py       → _parse_configuration_file calls argparse parse_known_args
```

- Where option definitions and their `type` callables live is unknown.
- The test directory layout is unknown.
- The location of documentation for the regex options is unknown.

## Code Style

Unknown. No project code beyond the traceback paths is visible. Follow the existing conventions in `pylint/config/` once they have been inspected.

## Testing Strategy

The framework and test locations are unknown. The required test cases are:

- **Regression test:** a config file containing `function-rgx=[\p{Han}a-z_][\p{Han}a-z0-9_]{2,30}$` does not produce an uncaught `re.error`.
- **Behavior test:**
  - Under Option A, assert that the process exits non-zero.
  - Assert that the output contains the option name, the pattern, and the regex error text.
  - Assert that the output contains no Python traceback.
- **Coverage across sources:** the same invalid pattern passed on the command line (e.g. `--function-rgx=...`) behaves the same way.
- **Coverage across option types:** at least one other regex-typed option, and the comma-separated regex-list option if one exists, behaves the same way.
- **Non-regression:** valid regexes still compile and apply. This includes non-ASCII ranges such as `[\u4e00-\u9fff]`.

## Boundaries

**Always**
- Keep valid regex options behaving exactly as before.
- Name the offending option and pattern in any error.
- Add regression tests for the reported pattern.

**Ask first**
- Adding a dependency on the third-party `regex` package (Option B).
- Changing regex semantics or flags for existing options.
- Changing the exit code convention for configuration errors.

**Never**
- Silently ignore an invalid regex and fall back to the default without telling the user.
- Swallow the error so that linting proceeds with a different pattern than the user configured.
- Remove or weaken existing config-parsing tests.

## Success Criteria

1. Running `pylint` with the issue's `.pylintrc` does not print a Python traceback.
2. Under Option A, pylint prints a single, clear error naming `function-rgx`, the pattern, and `bad escape \p at position 1` (or an equivalent), then exits non-zero.
3. Under Option B, pylint runs and applies the pattern, so a function named with Han characters satisfies `function-rgx`.
4. The behavior is identical for config-file and command-line sources and for every regex-typed option.
5. Existing tests pass, and the new regression tests pass.

## Open Questions

1. **Which outcome do maintainers want?**
   - (A) A clean error message for invalid regexes, or
   - (B) real support for `\p{...}` through the `regex` package?

   The reporter's "expected: not throw error" could mean either one.
2. If Option A is chosen, should the message suggest a stdlib-compatible alternative, such as `[\u4e00-\u9fff]`? Or should that guidance live only in the documentation?
3. What exit code and output stream (stderr or stdout) should configuration errors use? Is there an existing convention for invalid option values?
4. Which options use regex types? Is there a central type, such as a regex or regex-list transformer, where the fix can be applied once?
5. Did pre-2.14 (optparse-based) pylint handle invalid regexes more gracefully? If so, is this a regression that should be backported?
6. What test, lint, and build commands does the project use, and what Python versions does it support?