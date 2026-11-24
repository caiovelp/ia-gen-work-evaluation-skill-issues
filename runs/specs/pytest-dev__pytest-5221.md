# Spec: Display Fixture Scope in `pytest --fixtures` Output

## Objective

Show each fixture's scope in the output of `pytest --fixtures`, so users don't need the docs or source code to find it.

**Problem (from the issue):** The scope of a fixture is visible only in the documentation, when someone has documented it, or in the source code. `pytest --fixtures` lists available fixtures but not their scopes.

**Users:**
- Test authors choosing which fixtures to request. Scope affects whether state is shared, how expensive a fixture is, and which fixtures can depend on which.
- Plugin users browsing fixtures from installed plugins whose source they don't normally read.

**User stories:**
- As a test author, when I run `pytest --fixtures`, I can see each fixture's scope (`function`, `class`, `module`, `package`, `session`) next to its name.
- As a plugin user, I can see the scope of plugin-provided fixtures without opening the plugin's source.

**What success looks like:** A user can find any listed fixture's scope from `pytest --fixtures` output alone.

## Assumptions

1. The change applies to `pytest --fixtures`. Whether `--fixtures-per-test` should also show scope is not stated (see Open Questions).
2. "Scope" means the scope registered with the fixture definition: `function`, `class`, `module`, `package` or `session`.
3. `function` is the default scope. To reduce noise, scope may be shown only for non-`function` fixtures. This is a proposal, not a requirement from the issue (see Open Questions).
4. The scope appears on the same line as the fixture name, for example `tmp_path_factory [session scope]`. The exact format is undecided (see Open Questions).
5. Existing content stays: fixture name, location shown in verbose mode, docstring, and the grouping by defining module/plugin. Scope is added information only.
6. The change covers built-in fixtures, plugin fixtures and user-defined fixtures (conftest and test modules) equally.
7. Fixtures with a dynamic (callable) scope have no single static value. They need a defined representation (see Open Questions).
8. No new command-line flag is added. Scope is shown by default.
9. Changing this output may break tools that parse `--fixtures` output. This is acceptable for a feature release, with a changelog entry.

## Tech Stack

- Language: Python. Supported versions are **unknown** (not in the issue).
- Project: pytest itself.
- Key dependencies: **unknown**. No new dependencies are expected.

## Commands

Not given in the issue. All are **unknown** until the repository's contributing docs or CI configuration are checked.

```
Build: unknown
Test: unknown (likely runs pytest's own test suite via the project's configured runner — confirm)
Lint: unknown
Dev/manual check: pytest --fixtures            (from the issue)
                  pytest --fixtures -v         (assumed: verbose variant also shows scope — confirm)
```

## Project Structure

**Unknown.** The issue gives no paths. The following still need to be found:
- The module that implements the `--fixtures` listing
- Where fixture definitions store their scope
- Where tests for `--fixtures` output live
- Where changelog entries and documentation for `--fixtures` live

## Code Style

**Unknown.** Follow the conventions of the code around the `--fixtures` implementation, and match how the existing output formats names, locations and docstrings (colors/markup, indentation).

## Testing Strategy

- **Framework:** pytest's own test suite. The exact helper or fixture for running pytest in-process or in a subprocess and checking its output is **unknown**. Use whatever the existing `--fixtures` tests use.
- **Test level:** Functional/integration tests that run `pytest --fixtures` on a generated test project and match lines in the output.
- **Cases to cover:**
  - A fixture of each scope (`function`, `class`, `module`, `package`, `session`) defined in a conftest and in a test module. The output shows the correct scope according to the chosen display rule (all scopes vs. non-default only).
  - Built-in fixtures with a known non-function scope show it (`tmp_path_factory` is session-scoped).
  - A fixture with a dynamic/callable scope is displayed as decided in Open Questions, without crashing.
  - Verbose mode (`-v`) still shows locations and also shows scope.
  - Fixtures without docstrings still show scope correctly.
  - Private fixtures (leading underscore, shown only with `-v`) show scope when listed.
  - Existing `--fixtures` tests still pass, or are updated only where the output format change requires it.
- **Coverage:** Every new or changed line in the display logic is exercised by at least one test. The project's coverage threshold is **unknown**.

## Boundaries

- **Always:**
  - Add tests for every scope value and for the default/verbose modes.
  - Add a changelog entry in the project's format (location and format **unknown**).
  - Update the documentation that shows sample `--fixtures` output, if any exists.
  - Keep fixture name, location and docstring in the output.
- **Ask first:**
  - Changing the order or grouping of fixtures in the output.
  - Adding a new CLI option, such as a flag to hide or show scope.
  - Also changing `--fixtures-per-test`.
  - Changing any public API or fixture-definition internals to expose scope.
  - Any format choice that could noticeably break downstream parsers of `--fixtures` output.
- **Never:**
  - Change fixture scoping behavior. This is a display-only change.
  - Remove or weaken existing tests without approval.
  - Add runtime dependencies.

## Success Criteria

1. Running `pytest --fixtures` on a project with fixtures of every scope shows each fixture's scope on or next to its name line, following the agreed display rule (all scopes, or only non-`function` scopes).
2. Built-in session-scoped fixtures, such as `tmp_path_factory`, show `session` scope in the default output.
3. `pytest --fixtures -v` shows scope along with the existing location information.
4. Fixtures with a dynamic/callable scope produce the agreed representation and never cause an error.
5. Apart from the added scope information, the output (names, docstrings, grouping, ordering) is unchanged for existing projects.
6. New tests cover criteria 1–4 and pass. The full existing test suite passes.
7. A changelog entry describes the new behavior, and any docs showing `--fixtures` output are updated.

## Open Questions

1. **Display rule:** Show scope for every fixture, or only for non-`function` (non-default) fixtures to reduce noise?
2. **Format:** What exact text and placement? For example `name [session scope]`, `name (scope: session)`, or a separate indented line. Should it be colored or highlighted like other parts of the output?
3. **Dynamic scopes:** How should a fixture whose scope is a callable appear? Options: `[dynamic scope]`, omit it, or attempt to evaluate it (likely not, since evaluation depends on config).
4. **`--fixtures-per-test`:** Should it also show scopes in this change, or should that be a follow-up?
5. **Verbose-only?** Should scope appear in default output or only with `-v`? The issue suggests default output, which this spec assumes.
6. **Compatibility:** Are there known consumers (IDE plugins, scripts) that parse `--fixtures` output and would be affected? Does the change need a deprecation or opt-out path?
7. **Repository specifics:** Supported Python versions, test/lint commands, the file implementing `--fixtures`, the location of existing tests for it, and the changelog convention are all unknown and need confirming.