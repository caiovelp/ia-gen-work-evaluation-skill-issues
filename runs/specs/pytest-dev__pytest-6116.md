# Spec: Short Command-Line Alias for `--collect-only`

## Assumptions

1. The request concerns the `pytest` CLI option `--collect-only`. Its current behavior (collect tests and report them without executing) stays the same. Only a shorter way to invoke it is being added.
2. The shortcut is an **alias**. `--collect-only` itself stays fully supported, so existing scripts, CI configs and docs keep working.
3. The issue asks for a "one char" option. It also says the requester is open to community input on which character. The spec therefore treats the exact spelling as undecided: a single-dash one-character flag (`-X`) or a short double-dash alias (`--co`).
4. The alias must not collide with any existing short or long option. That includes options registered by pytest's built-in plugins.
5. Collisions with third-party plugins that register the same flag are a risk to assess. pytest cannot fully guarantee against them.
6. The issue asks for community voting before implementation. This spec assumes the maintainers decide to proceed. Whether to proceed at all is still open.
7. The option is registered through pytest's existing option-registration mechanism (argparse-based). The exact file and function are unknown.

## Objective

Users who often run `pytest --collect-only` find the flag long to type. The goal is a short alias that triggers exactly the same behavior.

**Users:** pytest users who inspect test collection interactively, for example to check which tests a `-k` or `-m` expression selects, or to debug collection errors.

**User story:**
As a pytest user, I want to type a short option instead of `--collect-only`, so that I can inspect collected tests quickly from the terminal.

**Acceptance criteria:**
- Invoking pytest with the new alias produces the same output and exit code as `--collect-only` for the same arguments.
- The alias combines with other options in the same way as `--collect-only` (e.g. `-q`, `-k`, `-m`, path arguments).
- If it is a single-dash one-char flag, it can be clustered with other single-char flags where argparse allows (e.g. `-qX`). Whether this is required is an open question.
- `pytest --help` lists the alias next to `--collect-only`.
- `--collect-only` continues to work unchanged.

## Tech Stack

- Python, pytest itself (repository of `pytest-dev/pytest`).
- CLI parsing: pytest's own option layer over `argparse`. Exact module and version are unknown, since the repository is not visible.

## Commands

Not visible in the issue; **unknown**.
- Build: unknown
- Test: unknown (likely runs pytest's own test suite, possibly via tox; not confirmed)
- Lint: unknown
- Docs build: unknown

## Project Structure

Unknown from the issue. Relevant locations to be identified:
- Where `--collect-only` is registered: unknown.
- Tests for CLI option parsing and collect-only behavior: unknown.
- CLI reference / usage documentation: unknown.
- Changelog mechanism (e.g. changelog fragments): unknown.

## Code Style

Unknown. Follow the existing conventions used where `--collect-only` and its sibling options are registered. Do not invent a new pattern.

## Testing Strategy

- **Framework:** pytest's own test suite (pytest testing itself). Exact helpers and fixtures are unknown.
- **Levels:**
  - Functional/acceptance tests that run pytest in a temporary project and compare the alias with `--collect-only`: same collected items in the output, same exit code.
  - Tests for combination with `-q` and with a selection option (`-k` or `-m`).
  - A test confirming `--help` output mentions the alias.
  - A regression check that `--collect-only` still works.
- **Coverage:** new code paths must be exercised. The project-specific coverage threshold is unknown.

## Boundaries

- **Always:**
  - Keep `--collect-only` working and documented.
  - Verify the chosen alias does not collide with any built-in option.
  - Add a changelog entry and update the CLI docs/help text.
  - Run the full test suite before submitting.
- **Ask first:**
  - The final choice of alias spelling and character.
  - Any change to the semantics of `--collect-only`.
  - Changing or reassigning any existing short option.
  - Adding dependencies.
- **Never:**
  - Remove or rename `--collect-only`.
  - Repurpose an existing short flag.
  - Silently shadow an option of a widely used plugin without maintainer sign-off.

## Success Criteria

1. Running pytest with the alias on a sample project lists the same collected items, with the same exit code, as `pytest --collect-only` on that project.
2. `pytest <alias> -q` and `pytest <alias> -k <expr>` behave identically to the `--collect-only` equivalents.
3. `pytest --help` shows the alias alongside `--collect-only`.
4. No existing pytest option's behavior changes. The existing test suite passes.
5. A changelog entry and documentation update exist for the new alias.

## Open Questions

1. **Go/no-go:** Did the community vote or maintainer review approve adding a shortcut at all?
2. **Spelling:** Should this be a true single-character flag (`-X`) or a short long-form alias such as `--co`? A single char is a scarce resource in the pytest/plugin ecosystem. A short long-form alias carries less collision risk.
3. **Which character:** If single-char, which letters are still unused by pytest core? Which are commonly taken by popular plugins (e.g. `pytest-xdist`'s `-n`)? The full list of taken short options is not visible in the issue.
4. **Existing abbreviation:** Does pytest's argument parser already accept prefix abbreviations of long options (e.g. `--collect`)? If so, is that enough to resolve the request, or is it intentionally disabled or unreliable?
5. **Clustering:** If a single-char flag is chosen, must it support clustering with other short flags (e.g. `-qX`)?
6. **Plugin conflicts:** How should pytest behave if a third-party plugin already registers the chosen flag, and is that acceptable?
7. **Docs/changelog conventions:** Which documentation pages and changelog format must be updated? Unknown from the issue.