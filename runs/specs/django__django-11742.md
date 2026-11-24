# Spec: System check that `max_length` fits the longest choice

## Objective

Add a validation check that fails when a field's `max_length` is shorter than the longest value in its `choices`.

Today the mistake goes unnoticed until someone saves a record whose choice value is too long. Depending on the backend, that save fails or the value is silently truncated. The check should report the problem at development time instead, through the framework's existing model or field check mechanism.

**Users:** developers who define model fields with both `max_length` and `choices`.

**User stories**
- As a developer, when a field's choices include a value longer than `max_length`, I get a check error when checks run. The error names the field and the offending length.
- As a developer, when every choice value fits within `max_length`, I see no new check output.
- As a developer, fields without `choices` or without `max_length` behave exactly as before.

**What counts as success:** a configuration error that used to surface only at save time is now caught at check time, with no false positives on valid configurations.

## Assumptions

1. The project is Django. `Field.max_length` and `Field.choices` refer to model fields, and the change belongs in the existing system checks framework, run via `manage.py check` and implicitly by other management commands. *(Inferred from terminology; not stated in the issue.)*
2. The check compares the stored choice **values** (the first element of each pair), not the human-readable labels.
3. Grouped choices (named groups containing nested `(value, label)` pairs) must be flattened, so that every leaf value is checked.
4. The check applies to any field that defines both `max_length` and `choices`, including subclasses of the character field. Fields where `max_length` is `None` or unset are skipped.
5. Length means the length of the value as a string, i.e. character count, not byte count.
6. The problem is reported as an **Error**, not a Warning, because the configuration cannot store some declared choices.
7. The check runs regardless of database backend, including backends that do not enforce `max_length` (for example, SQLite).
8. Existing checks on `choices` structure, such as malformed choices, take precedence. The new check only runs when `choices` is otherwise well-formed, to avoid duplicate or confusing errors.
9. Enumeration-based choices (e.g. `TextChoices`) are covered once normalised to `(value, label)` pairs.

## Tech Stack

- Language and framework: Python / Django *(assumed; versions unknown)*
- Relevant subsystems: model field definitions; system checks framework *(exact modules unknown)*

## Commands

| Purpose | Command |
|---|---|
| Build | Unknown |
| Test (full suite) | Unknown |
| Test (targeted: field checks) | Unknown |
| Lint | Unknown |
| Run checks in a project | Unknown; likely the framework's `check` management command (unconfirmed) |

## Project Structure

Unknown; I have no repository access. These need to be identified:
- The source file where field-level checks on `choices` and `max_length` are implemented
- The test module(s) covering invalid model/field definitions
- The documentation page listing system check IDs and messages
- The release notes for the target version

## Code Style

Unknown. Follow the conventions of the existing field checks:
- Same error object type
- Same message phrasing style
- Same `hint` usage
- Same `obj` reference
- Same check ID numbering scheme

The new check ID must be the next unused ID in the relevant series; it cannot be determined without the repository.

## Testing Strategy

- **Framework:** the project's existing test runner *(unknown)*.
- **Level:** unit tests on field/model check output, alongside existing tests for invalid field definitions.
- **Cases to cover:**
  - A flat choice value longer than `max_length` → one error
  - A value exactly equal to `max_length` → no error (boundary)
  - All values shorter → no error
  - A grouped/optgroup choice whose nested value is too long → error
  - A field with `choices` but no `max_length` → no error
  - A field with `max_length` but no `choices` → no error
  - Malformed `choices` → only the existing malformed-choices error, not the new one
  - Non-string choice values, e.g. integers, measured by their string length
  - Enumeration-based choices
  - Multi-byte/unicode values measured by character count
- **Regression:** the existing check test suite still passes unchanged.
- **Coverage target:** unknown; every branch of the new check is exercised.

## Boundaries

- **Always:**
  - Use the existing checks framework and message conventions
  - Add tests for every case above
  - Document the new check ID and add a release note
- **Ask first:**
  - Choosing Error vs Warning
  - Applying the check to fields beyond character-type fields
  - Changing the behaviour of existing `choices` checks
  - Adding dependencies
- **Never:**
  - Change runtime save/validation behaviour as part of this work
  - Alter database schema generation
  - Remove or renumber existing check IDs
  - Weaken existing tests

## Success Criteria

1. A model field with `max_length=N` and a choice value of length `N+1` or more produces exactly one check error when system checks run. The error identifies the field.
2. The error message states the minimum `max_length` required, i.e. the length of the longest choice value.
3. A choice value of exactly `N` characters produces no error.
4. Nested values inside grouped choices are included in the comparison.
5. Fields lacking either `choices` or `max_length` produce no new output.
6. Malformed `choices` yield only the pre-existing error for that condition.
7. The new check has a unique, documented ID and appears in the checks reference documentation.
8. All existing tests pass. New tests cover the cases listed under Testing Strategy.

## Open Questions

1. Is this Django? Which version or branch is targeted?
2. Should violations be an **Error** (blocking) or a **Warning**? Should they be silenceable via the standard silencing mechanism?
3. Should the error message report the required minimum length, list the offending value(s), or both? If multiple values are too long, should there be one error or one per value?
4. How should non-string choice values (integers, enums, lazy translation objects) be measured? Is `len(str(value))` acceptable?
5. Should the check apply only to character fields, or to any field with both `max_length` and `choices`? This includes third-party fields and form fields.
6. How should callable or dynamically generated `choices` be handled? Should they be evaluated at check time or skipped?
7. Should the check also cover model form fields or serializer-level fields, or only model fields?
8. Is there an existing check ID series this should join? What is the next free ID?
9. Should existing projects that currently pass checks be flagged immediately? Is a deprecation period or a warning-first rollout needed for backwards compatibility?