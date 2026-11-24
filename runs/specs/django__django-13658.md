# Spec: ManagementUtility uses its own computed program name for the preliminary option parser

## Assumptions

1. This is the Django project. The class is `ManagementUtility`, probably in `django/core/management/__init__.py`. That location comes from the issue context and has not been checked in the repository.
2. `CommandParser` is Django's subclass of `argparse.ArgumentParser`. It accepts and forwards the standard `prog` keyword argument.
3. With argparse, when `prog` is not given it defaults to `os.path.basename(sys.argv[0])`. The `%(prog)s` placeholder in `usage` expands to that value. When `sys.argv[0]` is `None`, `os.path.basename(None)` raises `TypeError` while the parser is being built.
4. The parser in question is the preliminary one. It parses `--settings` and `--pythonpath` in `ManagementUtility.execute()`, and it is built with `usage='%(prog)s subcommand [options] [args]', add_help=False, allow_abbrev=False`.
5. `self.prog_name` is computed in `__init__` and is already correct, including the `'__main__.py'` → `'python -m django'` mapping. It needs no change.
6. `execute_from_command_line` is technically private API. The fix is still worth making as a small correctness and consistency improvement.
7. The scope is only this preliminary parser. Other places that may read `sys.argv` (for example subcommand parsers or `BaseCommand.create_parser`) are out of scope unless the investigation finds that they block the reporter's use case. See Open Questions.

## Objective

When `ManagementUtility` (or `execute_from_command_line(argv)`) is called with an explicit `argv`, it should get the program name from that `argv` and not from the global `sys.argv`.

Right now, `__init__` computes `self.prog_name` from the supplied `argv`. The preliminary `CommandParser` in `execute()` ignores that value, so argparse falls back to `sys.argv[0]`. As a result:

- Usage and error text from this parser can show the wrong program name when the supplied `argv[0]` differs from `sys.argv[0]`.
- In embedded environments where `sys.argv[0]` is `None`, building the parser raises an exception. That happens even though the caller supplied a valid `argv`, so the caller has to patch `sys.argv[0]` globally as a workaround.

**User:** a developer embedding Django who calls `execute_from_command_line(custom_argv)` / `ManagementUtility(custom_argv).execute()` in a process where `sys.argv` is wrong or unusable.

**Success:** passing a custom `argv` is enough for the preliminary parser to work. No mutation of `sys.argv` is required.

## Tech Stack

- Python, Django core management framework (`django.core.management`)
- `argparse` (via `CommandParser`)
- Supported Python and Django versions: unknown, not stated in the issue

## Commands

Unknown. Not visible in the issue. Django's test runner is likely invoked from the `tests/` directory (e.g. `./runtests.py <module>`), but the exact command, flags, and target test module are unverified.

```
Build: unknown
Test: unknown
Lint: unknown
Dev: n/a
```

## Project Structure

Unknown beyond what the issue implies:

```
django/core/management/__init__.py  → ManagementUtility, execute_from_command_line (assumed location)
django/core/management/base.py      → CommandParser (assumed location)
tests/                              → test suite; exact module for management/admin-script tests unknown
```

## Code Style

The repository is not visible. Follow the existing Django conventions in the surrounding code. The issue suggests passing `prog` explicitly as a keyword argument alongside the existing ones, with one keyword per line when the call is wrapped. That suggestion is not code from the repository, and the final form should match the file's existing style.

## Testing Strategy

- Framework: Django's own test suite (unittest-based). The exact location for management-utility tests is unknown.
- Regression test(s) needed, at unit/integration level against `ManagementUtility` / `execute_from_command_line`:
  1. With `sys.argv[0]` temporarily set to `None` (patched and restored within the test), run `execute_from_command_line` with a custom `argv` whose `argv[0]` is a valid name and that includes `--settings` and/or `--pythonpath` plus a simple subcommand or help invocation. It should not raise `TypeError` (or any other exception) from parser construction.
  2. With `sys.argv[0]` set to something different from the supplied `argv[0]`, any usage text produced by the preliminary parser should contain the program name derived from the supplied `argv`, not from `sys.argv`.
- The existing management command and admin script tests should still pass, especially the `python -m django` → `'python -m django'` program-name behavior.
- Coverage expectation: unknown. At minimum, the regression scenario above must be covered.

## Boundaries

- **Always:**
  - Use the already computed `self.prog_name` and do not re-derive the program name.
  - Keep the existing preliminary parser behavior unchanged otherwise: the usage string, `add_help=False`, `allow_abbrev=False`, and the handling of `--settings`, `--pythonpath`, and unknown args.
  - Add a regression test.
  - Restore any patched `sys.argv` in tests.
- **Ask first:**
  - Extending the fix to other parsers or code paths that read `sys.argv` (e.g. per-command `create_parser`, autocomplete, help output).
  - Changing how `self.prog_name` is computed.
  - Making any `execute_from_command_line` behavior a documented or public guarantee.
- **Never:**
  - Mutate `sys.argv` globally inside Django to work around the problem.
  - Change the public signatures of `ManagementUtility` / `execute_from_command_line`.
  - Remove or weaken existing tests.

## Success Criteria

1. The preliminary `CommandParser` in `ManagementUtility.execute()` gets its program name from `self.prog_name` and not from `sys.argv[0]`.
2. `execute_from_command_line(argv)` with a valid `argv[0]` does not raise from preliminary parser construction when `sys.argv[0]` is `None`.
3. Usage text rendered by the preliminary parser uses `self.prog_name`, including `'python -m django'` when `argv[0]` is `__main__.py`.
4. When `argv` is omitted (`argv=None`), behavior is unchanged, because `self.argv` then defaults to `sys.argv[:]`.
5. A new regression test fails before the change and passes after it. The existing management tests all pass.

## Open Questions

1. Does the reporter's scenario (`sys.argv[0] is None` with a custom `argv`) hit other `sys.argv[0]`-dependent code after this parser? Examples are subcommand parsers built by `BaseCommand.create_parser`, help output, or autocomplete. If so, is fixing those in scope for this issue, or should they be separate tickets?
2. Which test module is the canonical home for this regression test (e.g. admin-script tests vs. a dedicated management-utility test), and what is the exact command to run it?
3. Should the fix be backported to any maintained release branches, or should it land only on the main development branch?
4. Should a release note be added, given that `execute_from_command_line` is private API?
5. Which Python versions must be supported? This affects whether argparse's default-`prog` behavior differs across versions.