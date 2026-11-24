# Spec: Customizable Help Formatter for Django Management Commands

## Objective

Command authors cannot control how `manage.py help <command>` renders the `help` text. Argparse's default formatting reflows the text, so line breaks and indentation are lost. For example, a multi-line "Example usage:" block ends up merged into one paragraph.

**Goal:** Let a management command author choose the argparse help formatter for their command, for example one that keeps the original line breaks and indentation of `help`. Default behavior for all existing commands stays the same.

**Users:** Authors of custom Django management commands (subclasses of `BaseCommand`) who want readable multi-line help, such as usage examples.

**User stories:**
- As a command author, I can opt my command into a formatter that keeps the newlines and indentation in `help`, so `./manage.py help my_command` shows examples the way I wrote them.
- As a command author who does nothing, my command's help output looks exactly as it does today.

**Acceptance criteria (from the issue):**
Given this `help`:
```
Import a contract from tzkt.
Example usage:
    ./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
```
- When the command opts in to a raw/preserving formatter, the description prints with its line breaks and the indented example line intact.
- The usage line and the positional/optional argument sections still render correctly.

## Assumptions

1. The issue is about Django's management command framework: `BaseCommand`, `manage.py help <cmd>`, and the argparse-based `CommandParser`.
2. Today `BaseCommand.create_parser()` builds the parser with a fixed, Django-specific formatter class. That class appears to reorder the common options (`--version`, `-v`, `--settings`, …) after the command-specific ones, which matches the usage line in the issue. Authors cannot override this formatter without reimplementing `create_parser()`.
3. The intended fix is opt-in customization, not a change to the global default. Changing the default would alter the help output of every existing command.
4. A customized formatter is used only for formatting `--help`/`help` output. It does not change argument parsing.
5. The preferred approach lets authors pass or select an argparse `formatter_class`, such as `argparse.RawDescriptionHelpFormatter` or a subclass of Django's formatter. Django's default stays in place when nothing is specified.
6. The project's normal contribution rules apply: a regression test, a docs update for custom management commands, and a release note.

## Tech Stack

- Python, using the standard-library `argparse` (formatter classes such as `HelpFormatter` and `RawDescriptionHelpFormatter`).
- Django management command framework (`BaseCommand`, `CommandParser`, Django's help formatter).
- Supported Python and Django versions: **unknown**.

## Commands

The issue does not show any of these, so all are unknown:
- Build: unknown (likely none needed)
- Test: unknown
- Lint: unknown
- Reproduce: `./manage.py help <command>` in a project with a command whose `help` is multi-line (taken from the issue)

## Project Structure

**Unknown.** The repository layout is not visible. The affected areas are:
- The module that defines `BaseCommand`, `CommandParser` and the Django help formatter (path unknown)
- Tests for management command parsing and help output (path unknown)
- Documentation on writing custom management commands (path unknown)
- Release notes for the target version (path unknown)

## Code Style

Unknown from the issue. Follow the conventions of the existing `BaseCommand` / `create_parser()` code. The only code in the issue is the author's command:

```python
class Command(BaseCommand):
    help = '''
    Import a contract from tzkt.
    Example usage:
        ./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
    '''
```

## Testing Strategy

- **Framework / location:** unknown. Use the project's existing management command test suite.
- **Regression tests:**
  - A command that specifies a preserving formatter produces help in which the multi-line `help` keeps its newlines and indentation.
  - A command that specifies nothing produces the same help output as before, including the common options appearing after command-specific ones.
  - A custom formatter still gets a correct usage line and argument sections.
  - Parsing behavior (arguments, defaults, errors) is the same whether or not a custom formatter is set.
- **Level:** unit and integration tests around parser creation and `print_help` output. No end-to-end tests needed.

## Boundaries

- **Always:** Keep default help output byte-for-byte unchanged for commands that don't opt in. Add regression tests. Document the new option.
- **Ask first:** Changing the default formatter globally. Changing the public signature of `create_parser()` or `CommandParser` in a way that could break subclasses that override them. Deprecating anything.
- **Never:** Change argument parsing semantics. Strip or alter `help` text content. Break third-party commands that already override `create_parser()`.

## Success Criteria

- [ ] A command author can choose the help formatter for a command without copying or reimplementing `create_parser()`.
- [ ] With a raw/preserving formatter, the issue's `tzkt_import` example renders as in the "expected" output: description lines preserved and the example line indented.
- [ ] Commands that don't opt in produce exactly the same help output as before.
- [ ] Django's ordering of common options keeps working, or the docs explain how to keep it when using a custom formatter.
- [ ] Tests cover the opt-in case, the default case, and unchanged parsing.
- [ ] Docs and release notes describe the new customization point.

## Open Questions

1. **API shape:** What should the extension point be?
   - A `formatter_class` keyword passed through `create_parser(prog_name, subcommand, **kwargs)`
   - A class attribute on `BaseCommand`
   - Something else

   Which is preferred for consistency with existing `BaseCommand` hooks?
2. **Common-option ordering:** If an author picks a plain argparse formatter, should Django's reordering of common options be lost? Or should Django provide a raw-description variant of its own formatter?
3. **Default behavior:** Is preserving `help` formatting by default ever in scope? The assumption is no, for backward compatibility.
4. **Target version and backport:** Which Django version should this ship in? Is it treated as a new feature (no backport) or a bug fix?
5. **Docs location:** Where should this be documented: the custom management commands how-to, the `BaseCommand` reference, or both?
6. **Repository details:** The test command, the file paths for `BaseCommand` and its tests, and the supported Python versions are unknown and need confirming.