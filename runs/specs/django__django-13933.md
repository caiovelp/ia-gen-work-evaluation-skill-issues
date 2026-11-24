# Spec: Include the invalid value in ModelChoiceField's `invalid_choice` validation error

## Objective

When a Django form's `ModelChoiceField` rejects a submitted value, its error message is generic: *"Select a valid choice. That choice is not one of the available choices."* It does not say which value was rejected.

Other fields already name the value:
- `ChoiceField` does, per the issue.
- `ModelMultipleChoiceField` does. The issue quotes its message: *"Select a valid choice. %(value)s is not one of the available choices."*

**Goal:** `ModelChoiceField` should include the offending value in its `invalid_choice` error, matching its sibling fields. Two changes are needed:
1. Pass the invalid value as a `value` parameter when raising the `ValidationError` with code `invalid_choice`.
2. Change the default `invalid_choice` message to use `%(value)s`.

**Users:**
- Developers using Django forms who want useful error messages.
- Developers who customize `error_messages['invalid_choice']` and want `%(value)s` interpolated, as other choice fields allow.
- End users of those forms.

**User stories / acceptance:**
- When I submit a value that is not in the field's queryset, the error message contains that value.
- When I set a custom `invalid_choice` message with `%(value)s`, it is filled with the submitted value.
- When I set a custom `invalid_choice` message without `%(value)s`, it renders exactly as before, with no error or change.
- The error code stays `invalid_choice`.

## Assumptions

1. The target is Django's own codebase, and `ModelChoiceField` / `ModelMultipleChoiceField` are the classes quoted in the issue. Their file location is not given in the issue and is **unknown**. It is presumably the forms/models module.
2. `ModelChoiceField` currently raises `ValidationError(..., code='invalid_choice')` without `params`. This is inferred from the issue's description, not seen in code.
3. The new default message should match `ModelMultipleChoiceField`'s wording exactly: `'Select a valid choice. %(value)s is not one of the available choices.'` This keeps the message consistent and lets it reuse the existing translation string.
4. The `value` param is the value that failed lookup. If a model instance was submitted and converted to its key or `to_field_name` before lookup, the converted key is used. The current conversion logic is not visible, so this is to be confirmed (see Open Questions).
5. Values that count as "empty" still return `None` or raise `required`. They do not trigger `invalid_choice`, so their behavior is unchanged.
6. Lookup failures caused by invalid types or values (e.g. a non-integer for an integer pk) should also raise `invalid_choice` with the value. This assumes those failures already map to `invalid_choice` today.
7. `ModelMultipleChoiceField` already passes `value` for its own `invalid_choice` path and needs no change. Its inheritance of messages and validation from `ModelChoiceField` must not regress.
8. Changing the default message text is acceptable as a minor behavior change and should be documented in release notes and the forms field reference docs.
9. A `ValidationError` with a params dict formats safely even when the message has no placeholders. Custom messages without `%(value)s` therefore keep working.

## Tech Stack

- Python and Django. The exact versions supported by the target branch are **unknown**.
- Django forms framework (`ChoiceField`, `ModelChoiceField`, `ModelMultipleChoiceField`, `ValidationError`).
- Django's i18n (`gettext_lazy` as `_`) for the default message.

## Commands

The issue does not include these, so all are **unknown**:
- Build: unknown (none expected for a pure-Python change)
- Test: unknown (Django's own test runner invocation and the relevant test module labels are not given)
- Lint: unknown
- Dev: not applicable

## Project Structure

Paths are not visible in the issue and are **unknown**. Expected areas of change:
- Source module defining `ModelChoiceField` (unknown path)
- Tests for model form fields / `ModelChoiceField` error messages (unknown path)
- Documentation for `ModelChoiceField` error message keys in the forms fields reference (unknown path)
- Release notes for the target version (unknown path)
- Translation catalogs: no manual edits expected. Reusing the existing `ModelMultipleChoiceField` string avoids a new msgid.

## Code Style

- Follow Django's existing conventions as shown in the issue:
  - `default_error_messages` dicts with `_()`-wrapped strings
  - Implicit string concatenation across lines
  - Curly quotes where Django uses them
- Raise errors as `ValidationError(message, code='...', params={...})`, consistent with how `ChoiceField` reports `%(value)s`.
- No code snippet from the actual implementation is visible, so no further style samples are given.

## Testing Strategy

- **Framework:** Django's own test suite. Runner command and locations are unknown.
- **Level:** unit tests on the form field, plus a form-level test if existing tests use that pattern.
- **Cases to cover:**
  1. `clean()` with a pk not in the queryset: the message contains that pk and the code is `invalid_choice`.
  2. `clean()` with a value of invalid type for the pk field: an `invalid_choice` error that includes the value. The expected behavior is to be confirmed.
  3. `to_field_name` set, value not found: the message contains the submitted value.
  4. Custom `error_messages={'invalid_choice': '... %(value)s ...'}`: the placeholder is interpolated.
  5. Custom `invalid_choice` message without a placeholder: it renders verbatim.
  6. `ModelMultipleChoiceField` invalid-choice and `invalid_pk_value` behavior is unchanged (regression).
  7. Update any existing tests that assert the old default text `"That choice is not one of the available choices."` for `ModelChoiceField`.
- **Coverage expectation:** every new or changed branch in the raise path is covered. The project's numeric threshold is unknown.

## Boundaries

- **Always:**
  - Keep the error code `invalid_choice`.
  - Keep the message translatable.
  - Match the wording of `ModelMultipleChoiceField` and `ChoiceField`.
  - Add or adjust tests alongside the change.
  - Document the changed default message.
- **Ask first:**
  - Using message wording that differs from `ModelMultipleChoiceField`'s.
  - Changing how values are normalized before lookup (e.g. instance-to-key conversion).
  - Changing `ModelMultipleChoiceField` or `ChoiceField`.
  - Backporting to stable branches.
- **Never:**
  - Change which inputs are accepted or rejected.
  - Expose data beyond the submitted value, such as queryset contents or other rows.
  - Hand-edit compiled or translated locale files.
  - Remove existing tests instead of updating them.

## Success Criteria

- [ ] An invalid `ModelChoiceField` submission yields a `ValidationError` with code `invalid_choice` and `params` containing `value`.
- [ ] The default rendered message reads `Select a valid choice. <value> is not one of the available choices.`
- [ ] Custom `invalid_choice` messages with `%(value)s` are interpolated. Those without it render unchanged.
- [ ] Valid choices, empty values, and `required` handling behave exactly as before.
- [ ] `ModelMultipleChoiceField` behavior and messages are unchanged, and its tests pass.
- [ ] All existing form and model-form tests pass, with assertions on the old default text updated.
- [ ] Docs and release notes mention that `ModelChoiceField`'s `invalid_choice` message now includes `%(value)s`.

## Open Questions

1. **Value representation for instances.** If a model instance (not in the queryset) is passed, should `%(value)s` show the extracted key (pk or `to_field_name` value) or the instance's `str()`? The extracted key would be consistent with what was looked up.
2. **Wording and translations.** Is reusing `ModelMultipleChoiceField`'s exact message string acceptable, so existing translations apply? Or does the project want quoted output, e.g. `“%(value)s”`, as in `invalid_pk_value`?
3. **Version policy.** Is this a new-feature-level change for the next release only, or eligible for backport?
4. **Release notes.** Should the release notes explicitly call out the changed default text as a minor backwards-incompatible change, for users whose tests assert the old message?
5. **Paths and commands.** Where are the source module, test modules, docs page, and release notes file, and what is the test command? All are unknown from the issue.