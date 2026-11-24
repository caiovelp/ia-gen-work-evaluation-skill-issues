## Summary
When index entries begin with the characters `@`, `£` and `←`, the generated HTML index contains two separate sections both titled **Symbols**. Both sections share the same HTML anchor, so the two **Symbols** links at the top of the index page lead to the first section.

## Steps to reproduce
1. Create index entries whose text begins with each of these characters:
   - `@`
   - `£`
   - `←`
2. Also create index entries that begin with ordinary letters.
3. Build the HTML output.
4. Open the generated index page.
5. Look at the section headings and at the navigation links at the top of the page.

## Observed behavior
- The index contains two sections titled **Symbols**:
  1. The first appears **before** the letter sections and contains the entries starting with `@`.
  2. The second appears **after** the letter sections and contains the entries starting with `£` and `←`.
- Both **Symbols** sections have the same HTML anchor.
- The links at the top of the index page include two **Symbols** links, one before the letters and one after. Both links go to the first **Symbols** section, so the second section can't be reached from these links.

## Expected behavior
All entries that begin with non-letter characters (`@`, `£`, `←`) should appear in a single **Symbols** section. The index page should have only one **Symbols** link, and it should lead to that section.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
Not provided in the original report.