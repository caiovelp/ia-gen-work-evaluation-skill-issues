# Spec: Single "Symbols" Section in Generated HTML Index

## Assumptions

1. The project is a documentation generator with index directives that produce an HTML index page (e.g. `genindex`). The issue does not name the tool. The wording, which mentions index entries, a "Symbols" section and letter links at the top of the index page, matches Sphinx, but this is **unconfirmed**.
2. The index generator groups entries into sections by their leading character. Every entry whose leading character is not a letter goes into one group labelled "Symbols".
3. The duplicate section likely arises for this reason:
   - Entries are sorted by a key in which `@` (U+0040) sorts before ASCII letters, while `£` (U+00A3) and `←` (U+2190) sort after them.
   - Grouping is then applied to the sorted list as consecutive runs, not as a true partition.
   - So non-letter entries split into two runs, and each run gets its own "Symbols" heading.

   This is a hypothesis drawn from the symptoms and has **not been verified** against code.
4. The section anchor is derived from the section label. Two sections called "Symbols" therefore get the same HTML `id`, and both jump-links resolve to the first one.
5. The intended behaviour is **one** "Symbols" section that contains every non-letter entry.
6. Other output formats (e.g. LaTeX, PDF) that build their own index are out of scope unless they share the same grouping code. This is **unknown**.

## Objective

Fix the HTML index so that it never renders more than one "Symbols" section. The current output has these faults:

- Entries beginning with `@` appear in a "Symbols" section before the letter sections.
- Entries beginning with `£` or `←` appear in a second "Symbols" section after the letter sections.
- Both sections share one anchor, so the quick-jump bar shows two "Symbols" links and both go to the first section.

**User:** a documentation author who uses index entries starting with symbols or non-ASCII, non-letter characters.

**Success looks like:** one "Symbols" section, one "Symbols" link in the jump bar, and every symbol-led entry inside that section.

### Acceptance criteria (user-facing)

- Given index entries starting with `@`, `£`, `←` and ordinary letters, the generated HTML index contains exactly one section headed "Symbols".
- That section contains all entries starting with `@`, `£` and `←`.
- The jump-link bar contains exactly one "Symbols" link, and it targets the single Symbols section.
- No two index sections share the same HTML anchor/`id`.
- Letter sections (A–Z) are unchanged in content and order.

## Tech Stack

- Language / framework: **unknown** (presumed Python/Sphinx, not confirmed).
- Templating for the index page: **unknown**.
- Versions affected: **unknown** (not stated in the issue).

## Commands

- Build: **unknown**
- Test: **unknown**
- Lint: **unknown**
- Reproduce (docs build to HTML): **unknown**

## Project Structure

**Unknown.** The repository is not available. Locations to be identified:

- The module that collects index entries, sorts them and groups them into letter/"Symbols" sections.
- The HTML template that renders the index page and its jump-link bar.
- The existing tests for index generation.

## Code Style

**Unknown.** Follow the conventions of the existing index-generation module and its tests. No sample code is visible in the issue.

## Testing Strategy

- **Framework:** unknown. Use the project's existing test framework and fixtures for index building.
- **Unit-level:** feed index entries with leading characters `@`, `£`, `←`, plus letter-led entries, into the grouping logic. Assert:
  - exactly one group labelled "Symbols";
  - it contains all symbol-led entries;
  - letter groups are unaffected.
- **Integration-level:** build a minimal HTML document containing those index entries. Assert:
  - exactly one "Symbols" heading;
  - exactly one "Symbols" jump link;
  - unique anchor ids across all sections.
- **Edge cases to cover:**
  - only symbol entries, with no letter entries;
  - symbols that sort before letters only;
  - symbols that sort after letters only;
  - digits as leading characters (see Open Questions);
  - non-ASCII letters (e.g. `É`, `Ж`) and their grouping (see Open Questions);
  - entries with a leading underscore or other ASCII punctuation (`_`, `!`, `[`).
- **Regression:** existing index tests must continue to pass.

## Boundaries

- **Always:**
  - Add a regression test reproducing the `@` / `£` / `←` case before changing behaviour.
  - Keep the "Symbols" label and anchor naming consistent with current output.
  - Run the full existing test suite.
- **Ask first:**
  - Changing where the Symbols section is placed (before letters vs. after).
  - Changing the sort order of letter sections.
  - Changing how non-ASCII letters are classified.
  - Changing anchor naming schemes, since this could break existing external links.
  - Modifying templates beyond what is needed.
- **Never:**
  - Fix only the anchor collision, e.g. by making the ids unique (`Symbols-1`), while leaving two Symbols sections.
  - Silently drop or reorder entries.
  - Remove or weaken existing index tests.

## Success Criteria

1. For any set of index entries, the HTML index has at most one section labelled "Symbols".
2. Every entry whose leading character is classified as a symbol appears in that single section.
3. The jump bar has at most one "Symbols" link, and it navigates to the Symbols section.
4. All section anchors on the index page are unique.
5. Section placement is deterministic and consistent: the Symbols section always appears in the same position relative to the letter sections. The exact position is to be confirmed.
6. Within the Symbols section, entry ordering is deterministic. The ordering rule is to be confirmed.
7. New regression tests cover the reported case and the edge cases above, and all existing tests pass.

## Open Questions

1. Which project and version is this? Is it Sphinx, and which builder/theme was used?
2. Should the single "Symbols" section appear **before** or **after** the letter sections?
3. Within the Symbols section, how should entries be ordered: by code point, or by locale-aware or another collation?
4. Should entries starting with digits go into "Symbols" or into their own section(s)?
5. How should non-ASCII **letters** be grouped? Options include:
   - their own letter heading (`É`, `Ж`);
   - folding into the base letter (`E`);
   - "Symbols".

   Is current behaviour for these intended?
6. Is the anchor/`id` for the Symbols section part of a stable public URL that must be preserved?
7. Do other builders (LaTeX/PDF, single-page HTML, ePub) share the same grouping logic, and should they be fixed or verified in the same change?
8. Is there any configuration for custom index grouping or sort keys that the fix must respect?
9. Can the reporter provide the exact index directives or entries used? For example, are `@`, `£` and `←` the first characters of single entries, pair entries or see-also entries?