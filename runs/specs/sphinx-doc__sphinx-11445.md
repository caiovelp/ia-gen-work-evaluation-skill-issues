# Spec: Preserve top-level headings that start with a domain role when `rst_prolog` is set

## Objective

**Problem.** When `rst_prolog` is set in `conf.py`, a document whose first section title starts with an interpreted-text role (e.g. `` :mod:`mypackage2` ``) does not get that title:

- The heading does not render correctly in the page.
- The heading does not appear in the toctree of the parent document (e.g. `index.html`).

The same document renders correctly in two cases:

- The title is plain text (`mypackage2` instead of `` :mod:`mypackage2` ``).
- `rst_prolog` is not set.

The reporter says the bug exists since at least Sphinx v4.0.0 and is still present on `7.1.0+/d3c91f951`.

**Users.** Sphinx users who set `rst_prolog`, for substitutions or other shared markup, and who title pages with domain roles. A common case is API pages titled `` :mod:`package` ``.

**Goal.** With `rst_prolog` set, a document whose first title starts with a role must produce the same title, section structure and toctree entry as when `rst_prolog` is unset. The prolog's own content, such as substitution definitions, must still apply.

### Acceptance criteria (user-facing)

1. Using the issue's reproduction, the page built from `mypackage.rst` shows a top-level heading containing `mypackage2`.
2. That page keeps "Subheading" as a second-level section under the top heading.
3. The `index` toctree has an entry for `mypackage`, and its title contains `mypackage2`.
4. Substitutions defined in `rst_prolog` (e.g. `|psf|`) still resolve in the document.
5. Output for documents without a role in the first title is unchanged.

## Assumptions

1. The bug is in how Sphinx inserts `rst_prolog` text into a document's source. It is not a docutils parsing bug, since the same source parses correctly without a prolog.
2. A line such as `` :mod:`mypackage2` `` at the top of a file is probably being mistaken for a docinfo / field-list line (`:name: value`). The prolog would then be inserted *after* that line instead of before it, which separates the title text from its `=====` underline. **This is a hypothesis.** It is not confirmed from code; the implementation phase must verify it.
3. The fix should be general to any role at the start of the first line, in any domain (`:mod:`, `:class:`, `:py:func:`, `:any:`, …), not only `:mod:`.
4. Genuine docinfo / field-list metadata at the top of a file must keep its current behavior. Examples are `:orphan:`, `:tocdepth: 2`, `:nocomments:` and `:author: X`. The prolog must still be inserted after real docinfo.
5. `rst_epilog` is out of scope unless the investigation shows the same defect there.
6. The issue lists no extensions, so the bug reproduces with no extensions enabled.
7. The reproduction script mixes directories. It runs `sphinx-build -b html . _build` but greps `docs/_build/index.html`. The intended build is source dir `docs`, output `docs/_build`.

## Tech Stack

- Python (reporter: CPython 3.11.3)
- Sphinx (reporter: `7.1.0+/d3c91f951`; also reproduced on v4.0.0)
- Docutils 0.20.1
- Jinja2 3.1.2, Pygments 2.15.1 (incidental)
- Supported Python, Sphinx and docutils version ranges for the fix: **unknown**

## Commands

Reproduction, taken from the issue with the directory mix-up corrected per Assumption 7:

```bash
sphinx-quickstart --no-sep --project mypackage --author me -v 0.1.0 --release 0.1.0 --language en docs
echo -e 'Welcome\n=======\n\n.. toctree::\n\n   mypackage\n' > docs/index.rst
echo -e ':mod:`mypackage2`\n=================\n\nContent\n\nSubheading\n----------\n' > docs/mypackage.rst
echo -e 'rst_prolog = """\n.. |psf| replace:: Python Software Foundation\n"""\n' >> docs/conf.py
sphinx-build -b html docs docs/_build
grep 'mypackage2' docs/_build/index.html
```

- Expected after fix: `grep` finds `mypackage2` in `index.html`.
- Observed before fix: it does not.

Repository commands are **unknown**, since the repository is not visible:

- Build: unknown
- Test: unknown (likely pytest; unverified)
- Lint: unknown

## Project Structure

**Unknown.** No repository access. The prolog-insertion logic most likely sits in a reST utility module in Sphinx, and tests sit in a `tests/` tree. Exact paths must be confirmed before planning.

## Code Style

**Unknown.** Follow the existing conventions of the Sphinx codebase: formatting, type hints, linters. No snippet is available from the issue.

## Testing Strategy

Exact framework, locations and fixtures are unknown. Required coverage:

- **Unit level, prolog insertion.** Given source lines and a prolog, assert where the prolog is inserted.
  - First line is a role-prefixed title followed by an underline: the prolog goes before the title, and title and underline stay adjacent.
  - First lines are real docinfo fields (`:orphan:`, `:tocdepth: 2`, `:author: me`): the prolog still goes after them (regression guard).
  - Plain-text first title: behavior unchanged.
  - Role-prefixed title with an overline as well as an underline, if supported.
- **Integration level, build.** Build a small project with `rst_prolog` set and a document titled `` :mod:`mypackage2` `` containing a subsection. Assert:
  - The document title is `mypackage2`, rendered via the role.
  - The parent toctree contains the entry.
  - The subsection is nested under the title.
  - A substitution from the prolog resolves.
- Coverage threshold: unknown.

## Boundaries

**Always:**
- Write a failing test reproducing the issue before changing code.
- Keep existing docinfo-before-prolog behavior intact.
- Run the existing test suite before proposing the change.

**Ask first:**
- Changing the public behavior or semantics of `rst_prolog` / `rst_epilog` beyond this bug.
- Altering how genuine docinfo fields are detected in ways that may affect other documents.
- Adding dependencies.
- Changing docutils-facing parsing hooks.

**Never:**
- Special-case only `:mod:`.
- Strip or rewrite the user's title text.
- Silently drop the prolog for affected documents as a workaround.
- Remove or weaken existing tests.

## Success Criteria

- [ ] The issue's reproduction (with corrected paths) produces `mypackage2` in `docs/_build/index.html`.
- [ ] The `mypackage` page has an `<h1>`-level title containing `mypackage2`, and "Subheading" is nested beneath it.
- [ ] `rst_prolog` substitutions still work in the affected document.
- [ ] Documents starting with real docinfo fields still receive the prolog after the docinfo block.
- [ ] Documents with plain-text titles produce unchanged output.
- [ ] New unit and integration tests fail before the fix and pass after it; the existing suite passes.

## Open Questions

1. Is Assumption 2 correct, i.e. is the role line misidentified as docinfo during prolog insertion? It needs confirming in the code.
2. How should Sphinx tell a docinfo field (`:tocdepth: 2`) from a title starting with a role (`` :mod:`x` ``)? Options to discuss:
   - The backtick after the second colon.
   - Checking whether the next line is a section underline.
   - Another rule.

   Which is acceptable to maintainers?
3. Does `rst_epilog` or any other source-mangling step have the same defect?
4. Should titles whose role is not on the first line, or that use an overline, be covered too?
5. Which Sphinx versions should receive the fix: main only, or backports to supported branches?
6. Does the bug also affect non-HTML builders (LaTeX, man, etc.)? Presumably yes, since it happens at parse time; should integration tests cover them?
7. What are the repository's actual test, lint and build commands, and where do the existing tests for prolog handling live?