# Spec: Callable model-field defaults must not be overwritten by submitted data in the hidden initial input of ModelForms

## Objective

**Problem.** In the Django admin, an inline form can lose its validation errors and its data on a second, unchanged submit. This happens when the inline's model field has a callable default (here `ArrayField(..., default=list)`). The form field then renders a hidden initial input (`show_hidden_initial=True`).

**Reproduction from the issue:**

1. Models: `Thing`, and `RelatedModel` with an FK to `Thing` and `plop = ArrayField(models.CharField(max_length=42), default=list)`.
2. Admin: `ThingAdmin` with a `TabularInline` for `RelatedModel`, `extra = 1`, using a `ModelForm` whose `clean()` always raises `ValidationError("whatever")`.
3. Go to `/admin/my_app/thing/add/` and type anything (e.g. `test`) in `plop`.
4. Submit. The inline shows the error, which is correct.
5. Submit again without changes. No error is shown, the inline is dismissed, and `plop` is now empty. This is wrong.

**Observed cause (from the issue).** After the first submit, the re-rendered form contains:

```html
<input type="hidden" name="initial-relatedmodel_set-0-plop" value="test" id="initial-relatedmodel_set-0-id_relatedmodel_set-0-plop">
```

The hidden "initial" input carries the user-submitted value (`test`) instead of the field's true initial value (the callable default, `[]`). On the second submit, `has_changed()` compares the submitted `test` with the hidden initial `test` and concludes the form is unchanged. The formset then treats the extra form as empty and skips validation. The user's data is silently discarded.

**Users affected:**

- Admin users editing inlines.
- More generally, any developer who renders a bound `ModelForm` or formset containing fields with callable defaults.

**Success** means re-submitting an unchanged, invalid form keeps reporting the same validation errors and keeps the entered data.

**Acceptance criteria / user stories:**

- As an admin user, when I re-submit an invalid inline without changes, I still see the validation error and my input is preserved.
- As a developer, a bound form's hidden initial input (`initial-<prefix>-<field>`) always holds the field's initial value, never the submitted value.

## Assumptions

1. The bug is in Django core (forms / model forms / formsets), not in the admin templates or in `ArrayField` specifically. `ArrayField` is just a common field with a callable default.
2. `show_hidden_initial=True` is set automatically on form fields generated from model fields with callable defaults. The reporter's workaround (forcing `show_hidden_initial=False`) is consistent with this.
3. The hidden initial widget is rendered from the bound value (`data`) when the form is bound, instead of from `initial`. This is the root mechanism.
4. The same defect likely affects any field type with a callable default, not only `ArrayField` / PostgreSQL. This needs to be confirmed with a non-Postgres field.
5. The expected behavior is that the hidden initial value reflects the value the form was originally initialized with. For an unsaved instance, that is the evaluated callable default.
6. The fix must not change the rendered value of the visible widget. That widget should still show the user's submitted data.
7. The reporter's workaround (globally disabling `show_hidden_initial`) is not the desired fix. Hidden initial exists so that `has_changed()` works correctly for callable defaults.

## Tech Stack

- Django. The affected version(s) are **unknown** (not stated in the issue).
- Python version: **unknown**.
- `django.contrib.postgres` (`ArrayField`) and PostgreSQL appear in the reproduction. Whether they are required to reproduce is **unknown** (see Assumption 4).
- `django.contrib.admin` (`ModelAdmin`, `TabularInline`).

## Commands

All **unknown** — not visible from the issue or repository.

- Build: unknown
- Test (full suite): unknown
- Test (targeted forms / model_forms / admin_inlines / postgres tests): unknown
- Lint: unknown

## Project Structure

**Unknown.** No repository access is available.

Likely relevant areas are the Django forms layer (bound field rendering and hidden initial handling), model form field generation (callable default → `show_hidden_initial`), formsets (empty extra-form detection via `has_changed()`) and the admin inlines. The exact file paths are unconfirmed.

## Code Style

**Unknown** beyond following existing Django project conventions. No code snippet is provided, because none is visible.

## Testing Strategy

Framework and locations are **unknown** (presumably Django's own test suite). Required test coverage:

- **Form level (no admin, no Postgres if possible):**
  - Take a form field with `show_hidden_initial=True` whose initial comes from a callable.
  - Bind it with data that differs from initial.
  - Render it, and assert that the hidden initial input contains the *initial* value, not the submitted value.
- **Round-trip `has_changed()`:**
  - Simulate submit → render → resubmit, using the rendered hidden initial value as POST data.
  - Assert that `has_changed()` is still `True` on the second submit.
- **Formset level:**
  - Use an extra form with a callable-default field, invalid on submit.
  - Resubmit using the re-rendered hidden initial.
  - Assert that the form is not skipped as empty and that its errors persist.
- **Admin regression (inline):**
  - Reproduce the issue's scenario.
  - Assert that the second submit still shows the error and that the entered value is preserved.
- **`ArrayField`-specific test:** run under PostgreSQL if the existing test infrastructure supports it.
- **Non-regression:**
  - Fields without callable defaults are unaffected.
  - The visible widget still renders the submitted data.
  - Unbound forms render the hidden initial unchanged.

## Boundaries

- **Always:**
  - Write regression tests that reproduce the issue first.
  - Keep visible widgets rendering bound data.
  - Preserve existing `show_hidden_initial` semantics for `has_changed()`.
- **Ask first:**
  - Changing the public behavior or signature of form or bound-field APIs.
  - Changing when `show_hidden_initial` is enabled for model fields.
  - Any change that alters rendered HTML for non-callable-default fields.
  - Backporting to older release branches.
- **Never:**
  - "Fix" this by disabling `show_hidden_initial` globally for callable defaults.
  - Special-case `ArrayField` only, if the root cause is generic.
  - Remove or weaken existing tests.

## Success Criteria

1. Following the issue's reproduction steps, the second (unchanged) submit still displays the `ValidationError` on the inline and keeps the `plop` value.
2. For a bound form, the `initial-…` hidden input renders the field's initial value (e.g. empty for `default=list`), never the submitted value.
3. On re-submission, `has_changed()` returns `True` for a form whose submitted data differs from the true initial value.
4. All existing forms, model_forms, formsets and admin inline tests pass. New regression tests fail before the fix and pass after.

## Open Questions

1. Which Django version(s) are affected, and should the fix be backported?
2. Does the bug reproduce with a non-`ArrayField` field that has a callable default (e.g. `CharField(default=some_callable)`)? This determines whether the scope is generic or `ArrayField` / `contrib.postgres`-specific.
3. Should the hidden initial value come from the form's `initial` at bind time, or be re-evaluated from the callable on each render? This matters for non-deterministic callables such as `timezone.now` or `uuid4`.
4. Is the `ArrayField` widget's handling of list vs. string values (`[]` vs. `""`) part of the comparison mismatch, and does it need its own fix?
5. Should the reporter's workaround (`show_hidden_initial=False`) be documented as unsupported or discouraged once this is fixed?
6. What are the repository's exact test and lint commands, and what is the test layout? All of these are unknown.