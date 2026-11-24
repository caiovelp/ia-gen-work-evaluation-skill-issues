# Spec: viewcode must honor `viewcode_enable_epub=False` when html and epub builds run in one invocation

## Objective

**Problem.** With `sphinx.ext.viewcode` enabled and `viewcode_enable_epub=False`, which the issue describes as the default, running `make html epub` still produces viewcode module pages (highlighted source pages) in the epub output. The reporter expects epub builds to omit these pages unless `viewcode_enable_epub=True`.

**Who is affected.** Sphinx users who build HTML and EPUB in one command, as in `make html epub`, with viewcode enabled. Their epub ends up containing source-code pages they did not ask for.

**Goal.** Whether viewcode module pages appear in an epub build depends only on `viewcode_enable_epub`. It must not depend on which builders ran earlier in the same invocation or on what is cached from a previous build.

**Acceptance criteria (user stories)**
- As a user with `viewcode_enable_epub=False`, when I run `make html epub`, the HTML output contains viewcode module pages and the epub output contains none.
- As a user with `viewcode_enable_epub=False`, when I run `make epub` alone, the epub output contains no viewcode module pages. This is presumably already true; it is a regression guard.
- As a user with `viewcode_enable_epub=True`, epub output contains viewcode module pages, whether epub is built alone or after html.
- HTML-only builds behave exactly as they do today.

## Assumptions

1. `viewcode_enable_epub` defaults to `False`, as the issue implies ("should not be created for epub by default").
2. The bug only shows up when an HTML-family build runs before the epub build, either in the same `make` invocation or through a shared build environment. The issue only shows `make html epub`, and does not say whether `make epub` alone is affected.
3. Root-cause hypothesis, not verified: viewcode decides per build whether to *collect* module info, but generates pages from data stored in the shared/pickled build environment. Data collected during the html build is therefore reused when the epub builder generates pages. This must be confirmed against the source.
4. "Module pages" covers both the per-module highlighted source pages and the `_modules/index` overview page.
5. The fix targets the Sphinx 3.x branch, since the reporter used "HEAD of 3.x". Whether it should also be forward-ported is an open question.
6. The issue says "epub", but the same logic probably applies to every epub-family builder name that viewcode checks. The exact set is unknown.
7. Other viewcode behaviour is unchanged: `viewcode_import`, `viewcode_follow_imported_members`, and the `[source]` links in HTML.

## Tech Stack

- Python. The reporter used 3.9.1; the project's supported range is unknown.
- Sphinx, 3.x branch.
- Extension under change: `sphinx.ext.viewcode`. Its file location is unknown and not shown in the issue.
- Builders involved: `html`, `epub`.

## Commands

- Reproduce, from the issue: `make html epub`, run in a Sphinx project with `extensions = ['sphinx.ext.viewcode']` and `viewcode_enable_epub = False`.
- Build: unknown.
- Test: unknown. The project's test runner and flags are not visible.
- Lint: unknown.

## Project Structure

Unknown. No repository layout is visible. To be filled in once these are located:
- the viewcode extension source module
- the existing viewcode tests and their test-root fixtures

## Code Style

Unknown. Follow the existing conventions of the viewcode extension and the Sphinx codebase. No snippet is available.

## Testing Strategy

- **Framework:** unknown (to be confirmed from the repo).
- **Regression test (required):** using the existing viewcode test fixtures, build `html` and then `epub` against the *same* source and build environment, with `viewcode_enable_epub=False`. Assert that:
  - the html output contains module pages
  - the epub output contains no module pages and no `_modules` index
- **Complementary tests:**
  - epub-only build with `viewcode_enable_epub=False`: no module pages
  - html then epub with `viewcode_enable_epub=True`: epub contains module pages
  - existing viewcode HTML tests keep passing unchanged
- **Level:** integration (real builder runs). The bug lives in how builders interact through shared environment state, so unit tests alone are not enough.

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after it.
  - Keep HTML output unchanged.
  - Keep the meaning and default of `viewcode_enable_epub` unchanged.
- **Ask first:**
  - Changing the config value's default or semantics.
  - Changing which builder names count as "epub".
  - Changing the stored environment data format in ways that could affect incremental builds or pickled environments.
  - Backporting or forward-porting beyond 3.x.
- **Never:**
  - Remove or weaken existing viewcode tests.
  - Disable viewcode for non-epub builders.
  - Fix the problem by requiring users to run separate clean builds.

## Success Criteria

1. With `viewcode_enable_epub=False`, `make html epub` yields an epub with zero viewcode module pages, and the HTML output still has them.
2. With `viewcode_enable_epub=True`, epub output includes module pages, whether built alone or after html.
3. An epub-only build with the default setting produces no module pages.
4. A new automated regression test covers the html → epub sequence and passes.
5. The existing test suite passes.
6. The changelog entry required by the project's convention is added. The convention itself is unknown.

## Open Questions

1. Does `make epub` alone, from a clean build directory, also produce module pages? Or does the bug need a prior html build in the same environment?
2. Does the bug also show up across *separate* invocations that share a build directory (`make html` and then, later, `make epub`)? If so, does the fix need to cover that case too?
3. Besides `epub`, which builders must the fix cover (e.g. `epub3`, or other epub-derived builders)?
4. Besides the module pages and `_modules/index`, should epub also omit any `[source]` links or references that point to module pages?
5. Which branch should receive the fix: 3.x only, or should it be merged forward?
6. What are the project's test, lint, and changelog conventions and commands? They are not visible from the issue.