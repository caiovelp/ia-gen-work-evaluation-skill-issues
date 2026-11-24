# Spec: Clearer assertion failure messages when comparing byte strings

## Objective

When an `assert` comparing two `bytes` objects fails, the explanation from pytest's assertion rewriting reports individual elements as integers. Indexing a `bytes` object in Python yields an `int`, so the message shows ordinals instead of characters:

```
    def test_b():
>       assert b"" == b"42"
E       AssertionError: assert b'' == b'42'
E         Right contains more items, first extra item: 52
E         Full diff:
E         - b''
E         + b'42'
E         ?   ++
```

`52` is the ordinal of `"4"`, but nothing in the message says so. Users read it as a value from the data. The reporter only understood it after trying `b"1"` and seeing `49`.

**Who it affects:** any pytest user writing `assert <bytes> == <bytes>` whose operands differ.

**Goal:** the failure explanation for byte strings must not show bare integer ordinals that look like data. The user should understand the difference from the message alone, without knowing that indexing `bytes` yields `int`.

**Acceptance criteria (user-facing):**
- For `assert b"" == b"42"`, the output has no line saying the first extra item is `52` without context.
- The full diff (`- b''` / `+ b'42'`) is still shown. It is already clear and stays the main explanation.
- The same applies when the left operand is longer than the right ("Left contains more items...").
- Comparisons of non-bytes sequences (lists, tuples) keep their current "first extra item" message. For example, `[1] == [1, 2]` still reports `2`.

## Tech Stack

- Python (supported versions: **unknown**, follow the project's existing policy)
- pytest, specifically its assertion rewriting and comparison-explanation logic (module and function names **unknown** from the issue)
- No new dependencies expected

## Commands

All **unknown**, since the issue gives no repository commands. To fill in from the project's contributor docs:
- Test: unknown (likely the project's pytest/tox invocation)
- Lint: unknown
- Build: not applicable / unknown

## Project Structure

**Unknown.** The issue does not show:
- the source file that builds the "Right/Left contains more items, first extra item: …" explanation
- the test file covering assertion comparison explanations
- the changelog location or format, if the project keeps one

## Code Style

Unknown. Follow the existing style of the surrounding assertion-explanation code. The message wording should stay consistent with the existing lines ("Right contains more items, …", "Full diff:").

## Testing Strategy

- **Framework:** pytest testing itself. The exact harness for running a failing test and capturing its output is unknown and should match existing assertion-message tests.
- **Cases to cover:**
  1. `b"" == b"42"`: right longer, no bare `52` ordinal in the explanation; full diff present.
  2. `b"42" == b""`: left longer, same expectations.
  3. `b"" == b"1"`: the reporter's second example, no bare `49`.
  4. Regression: `[1, 2] == [1]` and `(1,) == (1, 2)` still report the extra item as before.
  5. Depending on Open Question 3: equal-length bytes differing at an index, e.g. `b"1" == b"2"`.
- **Level:** unit or functional tests on the generated explanation text. Use the existing pattern; whether that is direct calls or runs of an inner test session is unknown.
- **Coverage expectations:** unknown. At minimum, every branch touched by the change gets a test.

## Boundaries

- **Always:**
  - Keep the "Full diff" output for bytes unchanged unless a test shows it is wrong.
  - Add regression tests for both directions (left longer and right longer).
  - Keep behavior for non-bytes sequences unchanged.
  - Add a changelog entry if the project requires one (mechanism unknown).
- **Ask first:**
  - Changing the explanation for `bytearray`, `memoryview`, or other buffer types.
  - Changing the "At index N diff" message for equal-length byte strings, if that turns out to have the same problem.
  - Any change to verbose (`-v`/`-vv`) output beyond removing or reformatting the confusing line.
  - Changing the wording of existing messages for other sequence types.
- **Never:**
  - Change the semantics of the assertion, so a pass or fail outcome changes.
  - Remove or loosen existing tests for sequence comparison messages.
  - Introduce new dependencies.

## Success Criteria

1. Running a test with `assert b"" == b"42"` produces a failure explanation that:
   - has no line stating the first extra item is `52` without byte or character context, and
   - still contains the full diff showing `b''` versus `b'42'`.
2. The same holds for `assert b"42" == b""` (left longer).
3. `assert [1] == [1, 2]` still produces "Right contains more items, first extra item: 2", unchanged.
4. All existing assertion-rewriting and comparison tests pass.
5. New tests for criteria 1–3 exist and pass.

## Assumptions

1. The confusing line comes from the generic sequence comparison logic, which treats `bytes` like any other sequence and indexes it, which yields `int`.
2. The full diff already explains byte-string differences well, so the "first extra item" line adds nothing for `bytes`.
3. The preferred default is to **omit** the "first extra item" line for `bytes` operands, relying on the full diff. The alternative is to render the item as a byte literal (e.g. `b'4'`). See Open Question 1.
4. Only `bytes` vs `bytes` comparisons are in scope. Mixed comparisons such as `bytes` vs `str`, or `bytes` vs list of ints, are out of scope.
5. The full diff is shown in the default verbosity shown in the issue. This matches the issue output, but behavior at other verbosity levels is not verified.

## Open Questions

1. **Preferred fix:** suppress the "Left/Right contains more items, first extra item" line for `bytes`, or keep it and render the item readably? Options include `b'4'`, `52 (b'4')`, or `0x34`.
2. **Other byte-like types:** should `bytearray` (and possibly `memoryview`) get the same treatment? Indexing them also yields `int`.
3. **Equal-length mismatches:** for something like `b"1" == b"2"`, does the explanation include an "At index 0 diff: 49 != 50"-style line? If so, is it in scope for this issue?
4. **Verbosity:** is the full diff always shown for bytes at default verbosity? If not, removing the "first extra item" line could leave no detail at all in some modes.
5. **Repository specifics:** which module holds the comparison-explanation code, where are its tests, what test and lint commands should be used, and does the project require changelog fragments?