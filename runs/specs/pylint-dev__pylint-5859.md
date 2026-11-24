# Spec: `--notes` must match note tags made entirely of punctuation (fixme / W0511)

## Objective

When a user passes a note tag through `--notes` that contains only punctuation characters (e.g. `???`), pylint should report a `fixme` warning (W0511) for comments that start with that tag. It should behave the same way it already does for alphanumeric tags such as `YES`.

**User:** a developer who uses pylint to flag marker comments. Some teams mark comments with symbols such as `???` or `!!!` instead of words.

**Observed (pylint 2.12.2, astroid 2.9.0, Python 3.10.2, macOS 11.6.1):**

Given `test.py`:
```python
# YES: yes
# ???: no
```
`pylint test.py --notes="YES,???"` outputs:
```
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
```

**Expected:**
```
************* Module test
test.py:1:1: W0511: YES: yes (fixme)
test.py:2:1: W0511: ???: no (fixme)
```

**User stories / acceptance criteria:**
- As a user, when I list a punctuation-only tag in `--notes`, comments starting with that tag are reported as W0511.
- As a user, existing alphanumeric tags (defaults and custom) still behave exactly as before. No new false positives or negatives.
- As a user, mixing alphanumeric and punctuation-only tags in one `--notes` value works for both kinds.

## Assumptions

1. The bug lives in the checker that emits W0511 (`fixme`). The fix should be limited to how note tags are matched against comment text, without changing the message format.
2. The likely cause is that the matching pattern relies on word boundaries or word-character semantics. Those never match around non-word characters such as `?`. This is a hypothesis only; the code has not been inspected.
3. Tags from `--notes` are treated as literal strings. Regex metacharacters (`?`, `*`, `+`, `.`, `(`, etc.) must not be interpreted as regex syntax.
4. The tag must still be "delimited" in a sensible way. `# ???: no` matches `???`. Assumed but unconfirmed: `# ????: no` should not match `???`, mirroring how `# YESNO` presumably does not match `YES`.
5. Matching rules for case-sensitivity and for the text following the tag (colon, space, end of comment) stay the same as for alphanumeric tags today.
6. Any related option that supplies a note regex (if one exists) is out of scope unless it shares the broken code path.
7. The expected output's column (`2:1`) matches the existing column convention for line 1. No change to column reporting is intended.

## Tech Stack

- Python (issue reproduced on 3.10.2; the full supported version range is unknown)
- pylint 2.12.2 (reported version); astroid 2.9.0
- Test framework: **unknown** (not visible in the issue)

## Commands

- Reproduce: `pylint test.py --notes="YES,???"` (from the issue)
- Build: **unknown**
- Test: **unknown**
- Lint: **unknown**

## Project Structure

**Unknown.** No repository access. These locations need to be identified:
- the module implementing the `fixme` / W0511 checker and the `--notes` option
- the existing tests for that checker
- the functional test fixtures, if the project uses them
- the changelog / release-notes location

## Code Style

**Unknown.** Follow the conventions of the existing checker module and its tests. No snippet is available from the issue.

## Testing Strategy

The framework and locations are unknown. The tests must cover:
- **Regression test (required):** with `notes=["YES", "???"]`, both `# YES: yes` and `# ???: no` emit W0511 with the messages shown in Expected.
- **Literal handling:** tags containing regex metacharacters (e.g. `???`, `.*`, `+++`) are matched literally. They must not raise a regex error and must not over-match.
- **Mixed tags:** a tag combining letters and punctuation (e.g. `TODO!`) behaves consistently. Its expected semantics are an open question.
- **No regressions:** existing tests for default tags (e.g. FIXME/XXX/TODO, if those are the defaults) and custom alphanumeric tags still pass unchanged.
- **Negative cases:** a comment without any configured tag emits nothing. A tag that appears only as a substring of a longer token follows whatever boundary rule is agreed (see Open Questions).

## Boundaries

- **Always:**
  - Add a regression test that fails before the fix and passes after.
  - Escape user-provided tags before using them in any pattern.
  - Keep the W0511 message text and format unchanged.
  - Run the full existing test suite.
- **Ask first:**
  - Changing matching semantics for alphanumeric tags (boundaries, case-sensitivity).
  - Changing the `--notes` option's parsing or defaults.
  - Touching other note-related options.
  - Adding dependencies.
- **Never:**
  - Remove or loosen existing fixme tests to make the change pass.
  - Interpret `--notes` values as raw regex.
  - Change unrelated checkers.

## Success Criteria

1. `pylint test.py --notes="YES,???"` on the issue's `test.py` produces exactly the Expected output (two W0511 messages, lines 1 and 2).
2. Punctuation-only tags containing regex metacharacters never cause an exception and only match the literal tag.
3. All pre-existing fixme/W0511 tests pass without modification.
4. A new automated regression test covering the issue's scenario exists and passes.
5. A changelog entry is added, if the project requires one (location unknown).

## Open Questions

1. **Boundary semantics:** for punctuation-only tags, what counts as the end of the tag?
   - Should `# ????: x` match tag `???`?
   - Should `# ???x` match it?
   - Should alphanumeric tags keep their current boundary behavior exactly?
2. **Mixed tags** such as `TODO!` or `!TODO`: what is the expected matching rule? Do they currently work?
3. **Leading context:** must the tag be at the start of the comment (after `#` and whitespace), or can it appear anywhere in the comment? Punctuation-only tags should follow whatever the current rule is.
4. **Related options:** is there a separate regex-based notes option, and does it share the affected code path?
5. **Versions:** which Python and pylint versions or branches should receive the fix? Should it be backported to the 2.12.x line?
6. **Changelog:** where is it and what format does it use?
7. **Test conventions:** which test commands, and which unit vs. functional test layout, should the regression test use?