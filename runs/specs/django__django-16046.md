# Spec: Handle null/empty values in `numberformat.py` without `IndexError`

## Assumptions

1. `numberformat.py` is Django's number formatting utility (likely `django/utils/numberformat.py`, exposing a `format(...)` function). The issue gives only the filename, so the full path and function name are unconfirmed.
2. "Null" covers values that reach the formatter as `None` or as an empty string `""`. The `str_number[0]` lookup only raises `IndexError` when `str_number` is empty.
3. The failure is reached through the admin changelist, when a `list_display` column renders a nullable numeric field (`IntegerField`, `DecimalField`, `FloatField`, etc.) whose value is null. The other route is the localization/number-formatting path (e.g. `localize` or `floatformat`).
4. Expected behaviour for a null or empty input is to return it unchanged and raise no exception. The value should not be coerced to `0` or `"None"`, and existing rendering paths stay responsible for how "empty" is displayed (e.g. the admin's empty value display).
5. Formatting of all non-empty inputs (ints, floats, `Decimal`, numeric strings, negatives, scientific notation) must not change.
6. The change is limited to input handling at the start of the formatter. No public signature changes.

## Objective

When `numberformat.py` receives a null or empty number, it currently raises `IndexError: string index out of range` at:

```python
if str_number[0] == "-"
```

This crashes admin changelist pages that display nullable numeric fields.

**Who is affected:** Admin users viewing changelists, and any code that calls the number formatter with a null or empty value.

**Goal:** The formatter handles null and empty inputs gracefully, with no exception, and leaves every other input's output unchanged.

**Acceptance criteria:**

- Calling the formatter with `None` does not raise. It returns the input unchanged (see Open Questions on exact return value and safe-string marking).
- Calling the formatter with `""` does not raise. It returns `""`.
- An admin changelist with a nullable numeric field in `list_display` and a row whose value is null renders without error.
- Output for existing valid inputs is identical before and after the change.

## Tech Stack

- Python (version unknown)
- Assumed to be Django (version or branch unknown)

## Commands

- Build: unknown
- Test: unknown. The project's standard test runner should be used, targeting the number-format utility tests and admin changelist tests.
- Lint: unknown
- Dev: unknown

## Project Structure

- Source: `numberformat.py` (full path unknown; assumed `django/utils/numberformat.py`)
- Tests: unknown. Assumed to be an existing test module for number formatting utilities.
- Docs/release notes: unknown. A release note entry may be expected.

## Code Style

- Follow the existing conventions of the project and file (not visible here).
- The only code known from the issue is the failing line `if str_number[0] == "-"`.

## Testing Strategy

- **Unit tests** (number formatter):
  - `None` input does not raise and returns the expected value.
  - `""` input does not raise and returns the expected value.
  - Regression: existing positive, negative, decimal, float, `Decimal`, and large/scientific-notation cases are unchanged.
- **Integration test** (optional, if the project's admin tests support it): a changelist with a nullable numeric `list_display` column and a null row renders successfully.
- Write the test first and watch it reproduce the `IndexError`, then confirm it passes after the fix.
- Coverage expectations: unknown. The new branch must be covered.

## Boundaries

- **Always:**
  - Add regression tests reproducing the `IndexError` before fixing.
  - Run the existing number-formatting test suite.
  - Keep the public function signature unchanged.
- **Ask first:**
  - Changing how the admin displays empty values.
  - Changing the return type for null input (e.g. returning `"0"` or `"None"`).
  - Touching callers outside `numberformat.py`.
- **Never:**
  - Change formatting output for non-empty inputs.
  - Silently convert null to zero.
  - Remove or loosen existing tests.

## Success Criteria

- [ ] Formatter called with `None` raises no exception and returns the agreed value.
- [ ] Formatter called with `""` raises no exception and returns `""`.
- [ ] A new regression test fails on the current code with `IndexError` and passes after the change.
- [ ] The full existing number-formatting test suite passes unchanged.
- [ ] Admin changelist rendering of a null numeric field in `list_display` no longer errors (manual or automated check).

## Open Questions

1. **Exact input:** What exact value reaches the formatter in the failing case, `None` or `""`? Is there a traceback or minimal reproduction (model field type, `list_display` config, locale settings such as `USE_THOUSAND_SEPARATOR`)?
2. **Return value for `None`:** Should it return `None` unchanged, an empty string, or the input marked as safe? Should the result be wrapped in the same safe-string marking as normal output?
3. **Fix location:** Should the guard live in `numberformat.py` itself, or should the caller (admin display or localization layer) avoid passing null values? The issue implies the formatter.
4. **Other non-numeric inputs:** Should other non-numeric inputs (whitespace-only strings, other falsy values) be handled too, or only `None` and `""`?
5. **Project details:** Which project version or branch is targeted, and what are the test command and test file location?
6. **Contribution route:** The reporter offers a patch or GitHub PR. Is their proposed fix available to review against this spec?