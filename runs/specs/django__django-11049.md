# Spec: Correct Expected Format in the Invalid DurationField Error Message

## Objective

When a user enters an invalid value into a `DurationField`, the validation error message shows the expected input format. That format is wrong.

- **Current message format:** `[DD] [HH:[MM:]]ss[.uuuuuu]`
- **Actual parsing behaviour:**
  - Seconds are mandatory.
  - Minutes are optional.
  - Hours are allowed only when minutes are present.
  - For example, `"14:00"` parses as `00:14:00`, which is 14 minutes, not 14 hours.
- **Correct format:** `[DD] [[HH:]MM:]ss[.uuuuuu]`

The message misleads users about how their input will be read. The issue says this mistake exists in every Django version that supports `DurationField`.

**Users:**
- End users who submit forms or admin pages containing duration inputs.
- Developers who depend on Django's built-in validation messages.

**Primary user story:** As a user who enters an invalid duration, I see an error message whose format matches how Django actually parses durations, so I can correct my input.

**Secondary, proposed in the issue:** Duration fields could have a default `help_text` showing the expected format, because the syntax is not self-explanatory. This is a separate behavioural change and is not yet in scope (see Open Questions).

## Assumptions

1. The message to fix is the `invalid` error message of the model-level `DurationField`. The issue says "invalid DurationField error message" without naming the model field or the form field.
2. The parser's current behaviour is correct and must not change. Only the documented format in the message changes.
3. The corrected string is exactly `[DD] [[HH:]MM:]ss[.uuuuuu]`, as written in the issue.
4. The message is a translatable string. Changing its source text will invalidate existing translations for it. Translation catalogs are refreshed through Django's normal translation process, not edited by hand in this change.
5. The fix targets the main development branch. Backporting is a separate decision for the maintainers.
6. Any tests that assert the exact text of the old message must be updated to the new text.

## Tech Stack

- Python and Django. The exact versions are not stated in the issue and are **unknown**.
- Component: `DurationField`. Whether this means the model field, the form field, or both is unconfirmed.

## Commands

Not given in the issue; all **unknown**.

- Build: unknown
- Test: unknown (Django's own test runner is presumably used, but the exact command is not visible)
- Lint: unknown

## Project Structure

Not visible from the issue; all **unknown**.

- Location of the `DurationField` definition and its `default_error_messages`: unknown
- Location of the duration parsing logic: unknown
- Location of tests covering `DurationField` validation messages: unknown
- Location of documentation that may repeat the format string: unknown
- Location of translation catalogs: unknown

## Code Style

- No code is visible.
- Follow the existing conventions of the surrounding code.
- Keep the message wrapped in the same translation mechanism it already uses.
- Keep the existing placeholder and interpolation style unchanged; only the format substring changes.

## Testing Strategy

- **Framework and test locations:** unknown.
- **Unit level:**
  - Validating an invalid duration value on `DurationField` raises a `ValidationError`.
  - The message of that error contains `[DD] [[HH:]MM:]ss[.uuuuuu]`.
  - The message does not contain `[DD] [HH:[MM:]]ss[.uuuuuu]`.
- **Regression:**
  - Existing parsing tests still pass, confirming the parser is untouched.
  - In particular, `"14:00"` still parses as 14 minutes.
- **Coverage expectation:** every changed message string is asserted by at least one test.

## Boundaries

**Always:**
- Keep the message translatable.
- Update every test and documentation occurrence of the old format string.
- Run the relevant test suite before committing.

**Ask first:**
- Changing the form-level `DurationField` message, if it differs from the model-level one.
- Adding a default `help_text` to duration fields.
- Backporting to stable branches.
- Editing translation catalogs directly.

**Never:**
- Change the parsing behaviour to match the old message.
- Remove or weaken existing duration parsing tests.
- Change the message's interpolation placeholders.

## Success Criteria

1. The invalid-value error message for `DurationField` states the format `[DD] [[HH:]MM:]ss[.uuuuuu]`.
2. The string `[DD] [HH:[MM:]]ss[.uuuuuu]` no longer appears anywhere in the codebase or documentation.
3. A test asserts the corrected format in the error message.
4. Duration parsing behaviour is unchanged, and all existing parsing tests pass.
5. The message is still marked for translation.

## Open Questions

1. **Which field?** Does the fix apply to the model `DurationField`, the form `DurationField`, or both? Does the form field currently show any format in its error message?
2. **Default `help_text`:** Should duration fields get a default `help_text` showing the format?
   - If yes, should that be a separate ticket?
   - It changes rendered output for every existing form, which is a backwards-compatibility concern.
3. **Other locations:** Does the format string appear in other places, such as documentation or release notes, that must also be updated?
4. **Alternate input formats:** The parser may accept other formats, such as ISO 8601 or PostgreSQL interval strings. Should the message mention them, or only the primary format?
5. **Backporting:** Should the fix go to supported stable branches, given it invalidates existing translations? Or should it land only on the development branch?
6. **Release note:** Is a release note required for a corrected user-facing message?