# Spec: Clean exit on unrecognized command-line option (no traceback)

## Objective

Running `pylint` with an unrecognized option (for example `pylint -Q`) currently does two things:

1. It reports the problem as a lint message: `Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)`.
2. It lets the internal exception `pylint.config.exceptions._UnrecognizedOptionError` escape to the user, which prints a Python traceback.

We want to keep (1) and remove (2). Instead of the traceback, pylint should exit cleanly with a short usage hint, similar to other CLI tools such as mypy:

```
usage: mypy [-h] [-v] [-V] [more options; see below] ...
mypy: error: unrecognized arguments: -Q
```

**Users:** anyone running `pylint` from a shell, CI, or wrapper script who mistypes or passes an unsupported option.

**Why it matters:**
- A traceback looks like pylint crashed.
- It hides the actionable message.
- It exposes private internals such as `_UnrecognizedOptionError`.

### Observed behavior (from the issue)

- Command: `pylint -Q`
- Version: `pylint 2.14.0-dev0`, `astroid 2.11.3`, Python 3.10.0b2.
- The exception is raised at `pylint/config/config_initialization.py` line 85 inside `_config_initialization`.
- It propagates up through `pylint/lint/run.py` (`Run.__init__`, line 135) and `pylint/__init__.py` (`run_pylint`, line 24) to the console entry point.

### User stories / acceptance criteria

- **Typo feedback:** As a user who passes an unknown option, I see which option was not recognized and a usage hint. I do not see a Python traceback.
- **Message preserved:** The existing `E0015 unrecognized-option` message is still emitted, so existing output and tooling are not lost.
- **Scripting:** As a CI or script author, I get a non-zero exit status when an unknown option is passed. A wrapper can detect it without parsing a traceback.

## Assumptions

1. The fix is scoped to the **command-line** path, which is what the issue reports. Unrecognized options coming from a **configuration file** may share the same exception path. Whether they get the same treatment is an open question; the default assumption is that their current behavior should not regress.
2. The `E0015 unrecognized-option` line should stay in the output. The reporter explicitly calls it "handy".
3. "Usage tip" means a short usage/help line plus an error line naming the bad option, in the style of argparse. It does not mean the full `--help` output.
4. The process must still exit with a non-zero status. A silent success would be worse than the traceback.
5. The behavior applies to every entry point that goes through `_config_initialization`, not only the `pylint` console script. Programmatic `pylint.lint.Run(...)` is one such path, so other pylint-family entry points may be affected too. This is unconfirmed.
6. No change to which options count as recognized. Only the reporting and exit behavior changes.
7. Target branch is the 2.14 development line (`2.14.0-dev0`).

## Tech Stack

- Python. The issue shows 3.10.0b2; the minimum supported version is **unknown**.
- pylint `2.14.0-dev0`, astroid `2.11.3`.
- The argument parsing library is **unknown** from the issue. The mypy example is argparse-style, but pylint's internal parser is not shown.

## Commands

All commands below are **unknown** because they are not given in the issue. They must be confirmed from the repository.

```
Reproduce:  pylint -Q          # from the issue
Build:      unknown
Test:       unknown
Lint:       unknown
Dev:        unknown
```

## Project Structure

These files are known from the traceback:

```
pylint/__init__.py                       → run_pylint() console entry point
pylint/lint/run.py                       → Run.__init__, calls _config_initialization
pylint/config/config_initialization.py   → _config_initialization, raises _UnrecognizedOptionError
pylint/config/exceptions.py              → _UnrecognizedOptionError (inferred from module path pylint.config.exceptions)
```

These locations are **unknown**:
- The test directory layout.
- Changelog or "what's new" doc locations.

## Code Style

The repository's style conventions are **unknown**. Follow the existing style of the files listed above. No code snippet is provided, to avoid inventing code.

## Testing Strategy

The test framework, test file locations, and coverage expectations are **unknown**. The required test cases are:

- **Unknown short option:** Running pylint with `-Q` does not raise or print a traceback. Instead:
  - The output contains the E0015 message.
  - The output contains a usage/error hint.
  - The exit status is non-zero.
- **Unknown long option:** The same checks hold for an unknown long option, e.g. `--some-unknown-option`.
- **Mixed options:** When valid options are combined with an unknown one, it still exits cleanly with no traceback.
- **Regression for valid invocations:** Valid invocations are unaffected in both output and exit codes.
- **Config file, if in scope:** An unrecognized option in a config file behaves as decided in Open Questions.

Test level: CLI and integration-level tests that invoke `Run`/`run_pylint` and capture stdout/stderr and the exit code.

## Boundaries

- **Always:**
  - Keep the E0015 message.
  - Exit non-zero on unknown options.
  - Add regression tests.
  - Follow existing conventions in the touched files.
- **Ask first:**
  - Changing the exit-code value or exit-code semantics.
  - Changing behavior for config-file unrecognized options.
  - Altering or removing `_UnrecognizedOptionError` itself.
  - Changing public API behavior of `pylint.lint.Run` when called programmatically.
  - Adding dependencies.
- **Never:**
  - Swallow the error silently or exit with status 0.
  - Remove or weaken existing tests.
  - Change which options are recognized.
  - Print the internal exception name or traceback to the user.

## Success Criteria

- [ ] `pylint -Q` prints **no** Python traceback.
- [ ] `pylint -Q` still prints `Command line:1:0: E0015: Unrecognized option found: Q (unrecognized-option)`, or the equivalent format already used.
- [ ] `pylint -Q` prints a concise usage hint identifying the unrecognized option.
- [ ] `pylint -Q` exits with a non-zero status. The specific value is per Open Questions.
- [ ] The same holds for unknown long options and for unknown options mixed with valid ones.
- [ ] Valid invocations produce identical output and exit codes to before.
- [ ] Automated tests cover the above.

## Open Questions

1. **Exit code:** Which value should be used? Options include argparse's conventional `2`, pylint's existing usage-error exit code, or something else. The exit-code conventions are unknown from the issue.
2. **Output content:** Should the output show **both** the E0015 message and the usage hint, or only one? The reporter likes E0015 and suggests the usage hint "for example". Is showing both acceptable, or is it redundant?
3. **Output format:** What exactly should the usage hint contain? Is it a one-line `usage: pylint [options] modules_or_packages` plus an error line, or does it point to `pylint --help`?
4. **Output streams:** Should the usage/error text go to stderr, with the lint message staying where reporter output normally goes?
5. **Config files:** Should unrecognized options in **config files** also stop execution with a usage hint? Or should they keep emitting E0015 and continue linting? What happens today is unknown.
6. **Programmatic callers:** For callers of `pylint.lint.Run(..., exit=False)`, should an unrecognized option raise a (possibly public) exception, call `sys.exit`, or return a status? Is `_UnrecognizedOptionError` relied on by anyone?
7. **Other entry points:** Do other pylint-family entry points share `_config_initialization` (e.g. pyreverse, epylint, symilar), and must they behave the same? This is unknown from the issue.
8. **Changelog:** Is a changelog/"what's new" entry required, and where does it live?
9. **Version target:** Is this a regression introduced during 2.14 development (i.e., did 2.13 handle this cleanly)? If so, should the previous behavior be restored exactly?