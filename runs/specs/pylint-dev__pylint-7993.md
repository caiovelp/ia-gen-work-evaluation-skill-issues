# Spec: Support escaped (doubled) braces in `--msg-template`

## Assumptions

1. The intended semantics of `--msg-template` follow Python `str.format` rules: `{{` and `}}` are literal braces, and `{name}` or `{name:spec}` are replacement fields. The 1.7.4 behavior and the issue's expected output are consistent with this.
2. The regression comes from template validation and preprocessing added after 1.7. That logic warns about unrecognized arguments. Per the traceback, it lives in or near `pylint/reporters/text.py` around line 206 in 2.12.2. It treats `{{ "Category"` as a field name and appears to strip or mangle the template, which leaves only `" }` in the output. This is inferred from the issue and has not been verified against source.
3. The fix targets the current development branch, not 2.12.2 specifically.
4. The warning about unrecognized arguments is intentional. It should keep firing for genuinely unknown fields such as `{foo}`, and should only stop firing for escaped braces.
5. Only `--msg-template` handling in the text reporter family is in scope. Other reporters such as JSON are unaffected.
6. The repository's build, test and lint commands, test layout, and code style are not visible in the issue. They are marked unknown below.

## Objective

**Problem.** In pylint 2.12.2, a message template with literal braces escaped as `{{ … }}` is misparsed:

- A spurious `UserWarning: Don't recognize the argument '{ "Category"'` is emitted.
- Each message renders as `" }` instead of `{ "Category": "convention" }`.

In pylint 1.7.4 the same template worked. This is a regression.

**Users.** People who use `--msg-template` to produce structured or custom output, such as JSON-like lines for CI tooling.

**User story.** As a pylint user, I can write `--msg-template='{{ "Category": "{category}" }}'` and get one line per message, such as `{ "Category": "convention" }`, with no warning.

**Acceptance criteria**

- **AC1.** The template `{{ "Category": "{category}" }}` renders each message as `{ "Category": "<category>" }` and emits no warning.
- **AC2.** Doubled braces anywhere in a template render as single literal braces. This covers the start, the middle, the end, and positions adjacent to a real field such as `{{{category}}}` → `{convention}`.
- **AC3.** Templates with unknown fields, such as `{foo}` or `{{ {foo} }}`, still trigger the "Don't recognize the argument" warning, naming `foo` only.
- **AC4.** Known fields remain valid and produce no warning, including fields with a format spec such as `{line:03d}`.
- **AC5.** Existing templates without escaped braces produce output identical to current behavior.
- **AC6.** The warning text continues to report only the true field name, never fragments containing `{` or `"`.

## Tech Stack

- Python, pylint itself. Supported Python versions: unknown (issue shows 3.9).
- Affected module: `pylint/reporters/text.py` (per traceback). Other involved modules: unknown.
- astroid version is irrelevant to this bug, by assumption.

## Commands

- Build: unknown
- Test: unknown (the project likely uses pytest; exact invocation unknown)
- Lint: unknown
- Reproduce (from the issue): `pylint test.py --msg-template='{{ "Category": "{category}" }}'`

## Project Structure

- `pylint/reporters/text.py`: location of the template-handling and warning logic (from traceback).
- Test directory for reporters: unknown.
- Changelog or news-fragment location: unknown.

## Code Style

Unknown, because no repository code is visible. Follow the existing conventions in `pylint/reporters/text.py` and the project's lint configuration.

## Testing Strategy

- **Unit tests** on the template handling in the text reporter:
  - Cover each of AC1–AC6 with the template string and expected rendered line.
  - Assert on warnings: none for AC1, AC2 and AC4; exactly one, naming the right field, for AC3.
- **Regression test** reproducing the exact template from the issue.
- **Functional or CLI-level test**, optional. Run pylint on a small file with the issue's template and compare the output lines.
- Framework, file locations and coverage thresholds: unknown. Follow the project's existing reporter tests.

## Boundaries

- **Always:**
  - Add a regression test for the issue's template.
  - Keep the unknown-argument warning working for genuine unknown fields.
  - Run the existing test suite before committing.
- **Ask first:**
  - Changing the warning's wording or category.
  - Changing the semantics of `--msg-template` beyond `str.format` brace escaping.
  - Altering behavior of other reporters.
  - Adding dependencies.
- **Never:**
  - Remove or weaken the unknown-field warning to make the test pass.
  - Silently change output for templates that currently render correctly.
  - Edit unrelated reporters.

## Success Criteria

- The issue's exact command prints `{ "Category": "<category>" }` per message with no `UserWarning`.
- New tests covering AC1–AC6 pass.
- The existing test suite passes.
- A changelog or news entry is added in whatever form the project requires (form unknown).

## Open Questions

1. Is full `str.format` brace semantics the intended contract for `--msg-template`, or only "doubled braces are literal"? For example, how should a lone unmatched `{` or `}` be handled: warn, error, or pass through?
2. Should a malformed template raise an error rather than warn and then produce mangled output?
3. Which branch or versions should receive the fix: main only, or a backport to the 2.12.x maintenance line?
4. Does the project require a changelog or news fragment, and where does it go?
5. Are there documented `--msg-template` examples that should be updated to show brace escaping?
6. What are the exact test commands and the location of the reporter tests?