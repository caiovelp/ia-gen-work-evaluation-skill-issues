# Spec: Correct the recursive-relationship hint for ambiguous intermediary models

## Objective

When a `ManyToManyField` uses an intermediary (`through`) model that has more than two `ForeignKey`s, and `through_fields` is not set, Django's system checks report an error. That error's hint currently reads:

```
'If you want to create a recursive relationship, '
'use ForeignKey("%s", symmetrical=False, through="%s").'
```

The hint is wrong in two ways:

1. **Wrong field class.** `symmetrical` and `through` are `ManyToManyField` arguments, not `ForeignKey` arguments. A user who follows the hint literally gets invalid code.
2. **Outdated requirement.** According to the reporter, `symmetrical=False` has not been required for recursive relationships with an intermediary model to `self` since Django 3.0.

**Users:** Django developers who define M2M relationships with custom intermediary models and hit this check error.

**Goal:** The hint gives correct, current, copy-pasteable guidance.

**Acceptance criteria:**
- The hint references `ManyToManyField`, not `ForeignKey`.
- The hint no longer presents `symmetrical=False` as required, pending confirmation of Open Question 1.
- Every occurrence of this hint is corrected, if it appears in more than one place (see Assumptions).
- Any existing tests that assert the old hint text are updated. At least one test asserts the new text.
- No other check message, error id, or check behaviour changes.

## Assumptions

1. The hint is emitted by Django's model-field system checks for M2M intermediary models, in the related-fields module. The exact file path, check id(s), and line numbers are **unknown**: there is no repository access.
2. The same hint may appear in two sibling errors: one for ambiguous "from" foreign keys and one for ambiguous "to" foreign keys. Both need the same fix if both exist.
3. The reporter's claim that `symmetrical=False` is unnecessary since Django 3.0 is correct. This is unverified.
4. The `%s` placeholders keep their current meaning and substitution order. This is assumed to be (related model / `"self"`, through model name).
5. This is a message-text fix only. It needs no deprecation and no behaviour change.
6. Existing tests assert this hint text verbatim and will need updating. Test file locations are **unknown**.
7. Docs may quote the hint, for example in the system check reference. Whether they do is **unknown**. If they do, they should be updated to match.
8. The reporter's PR exists but is not visible. This spec does not depend on it.

## Tech Stack

- Python / Django, current main branch. The exact version is **unknown**.
- Affected subsystem: system checks framework (`django.core.checks`) as used by relational model fields.

## Commands

All of these are **unknown**. They are not given in the issue and the repository is not accessible.

```
Build: unknown (pure Python; likely none)
Test:  unknown (Django's own test runner invocation not visible)
Lint:  unknown
Dev:   n/a
```

## Project Structure

**Unknown.** No repository access. The expected areas are:

- Relational field definitions and their checks: path unknown
- Tests for invalid model definitions / field checks: path unknown
- System check reference docs: path unknown
- Release notes, if the project requires an entry for message changes: path unknown

## Code Style

- Follow the existing style of the surrounding check message. Keep the implicit string concatenation and `%`-formatting exactly as it is used now.
- Do not reformat unrelated code.
- No real snippet of the surrounding code is available beyond the hint quoted in the issue.

## Testing Strategy

- **Framework:** Django's own test suite. The runner command is unknown.
- **Level:** Unit tests of model checks. Define an intermediary model with more than two FKs and no `through_fields`, run the model checks, and assert the exact `Error` (message, hint, `obj`, `id`).
- **Coverage:**
  - Update existing assertions on the old hint.
  - Ensure both the "from" and "to" ambiguity variants are covered, if both exist.
  - Optionally cover a recursive (`"self"`) intermediary case.
- **Regression:** The full check-related test modules pass unchanged apart from the hint text.

## Boundaries

- **Always:**
  - Keep error ids, messages, and trigger conditions unchanged.
  - Update tests that assert the hint alongside the text change.
  - Keep both hint variants consistent.
- **Ask first:**
  - Changing the error message itself, beyond the hint.
  - Adding a release note.
  - Touching documentation beyond quoting the corrected hint.
  - Backporting to stable branches.
- **Never:**
  - Change check logic or `through_fields` resolution behaviour.
  - Alter `ManyToManyField` semantics around `symmetrical`.
  - Delete failing tests instead of updating them.

## Success Criteria

- Triggering the ambiguous-intermediary check produces a hint of the form `use ManyToManyField("<model>", through="<through>")`. The final wording depends on Open Question 1.
- The string `ForeignKey(` with `symmetrical=` or `through=` no longer appears in any check hint.
- Updated tests pass, and no other tests in the checks and model-field suites regress.
- Any docs that quote the hint match the code.

## Open Questions

1. **Is `symmetrical=False` truly unnecessary in all cases?** Should the hint drop it entirely, or mention it only as optional? Please confirm against the Django 3.0 change that relaxed the requirement.
2. **Should the hint mention `through_fields`?** Specifying `through_fields` is the actual fix for an intermediary model with more than two FKs. The current hint only addresses the recursive case. Is changing the hint's scope in or out of this change?
3. **How many places emit the hint?** Does it appear in both the "from" and "to" ambiguity errors, and anywhere else?
4. **Is a release note required** for a corrected check hint? Should it be backported to supported stable branches?
5. **Do the docs quote this hint verbatim** anywhere that must be updated?
6. **Should the reporter's PR be the basis for review,** or should this be an independent implementation?