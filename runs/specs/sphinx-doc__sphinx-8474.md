# Spec: Remove spurious "no number is assigned for table" warnings after upgrading to Sphinx 3.3

## Objective

After upgrading to Sphinx 3.3, builds with the `singlehtml` and `latex` builders emit a new warning:

```
WARNING: no number is assigned for table:
```

The reporter says the documentation did not change, only the Sphinx version. They found nothing in the changelog about `numref` or numbering. So either:

- **(a)** Sphinx 3.3 introduced a regression that emits this warning where it should not, or
- **(b)** Sphinx 3.3 deliberately changed behavior and did not document it.

**Users affected:**
- Documentation authors who build with `singlehtml` or `latex`.
- Projects that use `-W` (warnings as errors). For them, a spurious warning is a build failure.

**Goal:**
1. Determine which Sphinx 3.3 change causes the warning.
2. Classify it as a bug or an intended change.
3. Then do one of the following:
   - If it is a bug: stop the warning in cases where it does not point to a real authoring problem.
   - If it is intended: make it actionable, by naming the offending target and source location and by documenting the change in the changelog.

**Acceptance criteria (user-facing):**
- A project that built without this warning on Sphinx 3.2.x, and has no real numbering problem, builds without it on the fixed version with `singlehtml` and `latex`.
- If a reference really cannot be numbered, the warning still appears. It identifies the referenced label or target and the document or line where the reference occurs. It is never emitted with an empty trailing description, as in the reported `...for table:`.
- The `html` builder behaves the same as before for the same input, or any difference is explained in the changelog.

## Assumptions

1. The warning text comes from Sphinx's own cross-reference / `numref` resolution code, not from a third-party extension. This is unverified; the reporter did not list their extensions.
2. The trailing empty text after `table:` suggests the referenced table has no caption or title, or that the warning was triggered by something other than an explicit `:numref:` role.
3. The regression is between 3.2.x and 3.3.0. The exact last-good version is unknown.
4. The reporter's project builds cleanly on the previous Sphinx version under the same configuration.
5. The fact that only `singlehtml` and `latex` are affected matters. These builders assign or look up figure numbers differently from the multi-page `html` builder, for example in how documents are merged or how numbers are keyed. This is a hypothesis to verify, not a known fact.
6. The fix belongs in Sphinx itself, not in user documentation, unless investigation shows the warning is correct.

## Tech Stack

- Sphinx (Python). The affected version is 3.3; the target fix version is unknown.
- Builders involved: `singlehtml`, `latex`; `html` is the comparison baseline.
- The Python version, docutils version and extensions in the reporter's environment are unknown.

## Commands

The issue gives no commands. All of the following are **unknown / to be confirmed**:

- Build/reproduce: unknown. Likely a `sphinx-build -b singlehtml …` / `-b latex …` invocation, but the exact flags and paths are not given.
- Test: unknown. The repository's test runner and invocation are not visible.
- Lint: unknown.

## Project Structure

Not visible from the issue. The following are **unknown**:

- The location of the cross-reference / `numref` resolution code.
- The location of figure/table number assignment for each builder.
- The location of builder-specific tests and test fixture projects.
- The location of the changelog file (the reporter refers to a "changelog").

## Code Style

Unknown. Follow the existing conventions in the Sphinx repository. No snippet is available from the issue.

## Testing Strategy

The framework and locations are unknown and must be confirmed in the repo. The tests needed are:

1. **Reproduction fixture.** A minimal Sphinx project that triggers the warning on 3.3 with `singlehtml` and `latex`. Its exact content is to be found during investigation. Candidates are listed under Open Questions.
2. **Regression tests (per builder).** Build the fixture with `singlehtml` and `latex`. Assert that the warning output does not contain `no number is assigned for table` when the input is valid.
3. **Negative test.** Use a fixture containing a real unnumberable reference, for example a `numref` to a table with no caption, if that is invalid. Assert that the warning is still emitted and includes the target identifier.
4. **Baseline parity.** Build the same fixtures with `html` and assert consistent behavior.
5. Run the existing `numref` / numbering test suites, which must still pass.

## Boundaries

**Always:**
- Reproduce the warning before changing behavior.
- Identify the specific 3.3 change responsible.
- Add regression tests for `singlehtml` and `latex`.
- Add a changelog entry.

**Ask first:**
- Removing the warning entirely, rather than suppressing it only in invalid cases.
- Changing how figure or table numbers are assigned for any builder.
- Changing the warning's text, category or type, since users may filter on these via `suppress_warnings`.
- Backporting to a patch release.

**Never:**
- Silence the warning globally in a way that hides genuine broken numbered references.
- Change behavior of the `html` builder without documenting it.
- Remove or weaken existing numbering tests.

## Success Criteria

- [ ] The root-cause change in 3.3 is identified and documented, as a link to the commit/PR or a description in the fix.
- [ ] The minimal reproduction emits the warning on 3.3 and does not emit it after the fix, for both `singlehtml` and `latex`.
- [ ] Genuine unnumberable references still produce a warning that names the target and the source location. The description is not empty.
- [ ] No new failures in existing numbering / cross-reference tests.
- [ ] The changelog entry describes the fix, or describes the intended behavior change if the warning is deemed correct.

## Open Questions

1. **Reproduction:** Can the reporter provide a minimal project, or at least the following?
   - Their `conf.py`, especially `numfig`, `numfig_format`, `numfig_secnum_depth` and the extensions list.
   - An example of the table and the reference that triggers the warning.
2. **Which construct is the trigger?**
   - An explicit `:numref:` to a table?
   - A `:ref:` or `:any:` role, or an intersphinx reference, that resolves to a table?
   - A table with no caption that is referenced by label?
   - A third-party extension, such as an autosummary-style table generator?
3. **Is `numfig` enabled** in the reporter's project? If it is disabled, should any numbering warning be emitted at all?
4. **Which builders are affected?** Does the warning also appear with the multi-page `html` builder, or strictly only with `singlehtml` / `latex`? This determines whether the cause is in shared resolution logic or in builder-specific number assignment.
5. **Last good version:** Is it 3.2.1? Was the warning present in any 3.3 pre-release?
6. **Intended or not:** Was a stricter check or new warning deliberately introduced in 3.3 without a changelog entry? If so, is the desired outcome only better messaging and documentation?
7. **Empty description:** Why is the text after `table:` empty in the warning? Is the empty description itself a bug, independent of whether the warning should fire?
8. **Workaround:** Should a temporary workaround be documented for users on `-W`? For example, a `suppress_warnings` entry, if this warning has a suppressible type. Its type/subtype is unknown.