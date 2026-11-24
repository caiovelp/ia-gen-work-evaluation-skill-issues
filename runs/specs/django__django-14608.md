# Spec: Add `nonform` CSS class to FormSet non-form errors

## Assumptions

1. The project is Django. The issue does not name it, but the terms `ErrorList`, `nonfield`, and FormSets match Django's forms framework.
2. Forms already pass `error_class='nonfield'` when they build the `ErrorList` for non-field errors. The `ErrorList` then renders as `class="errorlist nonfield"`. The new behavior should copy this mechanism exactly.
3. FormSet non-form errors are those returned by the formset's non-form-errors accessor. In Django's public API this is `BaseFormSet.non_form_errors()`. They come from:
   - `ValidationError`s raised in the formset's `clean()`
   - built-in formset validation, such as max/min number of forms and an invalid or missing management form
4. A formset may use a custom `ErrorList` subclass, supplied through the formset's `error_class` option. That subclass is assumed to accept an `error_class` keyword argument, as it already must for forms' `nonfield` errors.
5. The change is additive. Existing rendered output gains one extra CSS class. No class is removed or renamed.
6. The change ships in a future feature release with a release note. It is not a bugfix backport.
7. These items are **unknown** because the repository is not visible:
   - exact file paths
   - build, test, and lint commands
   - test module locations
   - docs file locations

## Objective

Developers who render formset errors cannot currently tell non-form errors (errors on the FormSet as a whole) apart from field errors or non-field errors by CSS class.

The goal is that the `ErrorList` holding a FormSet's non-form errors carries the CSS class `nonform`, alongside the base `errorlist` class. This mirrors how Forms tag non-field errors with `nonfield`. A custom `ErrorList`, or plain CSS, can then style or render three categories differently:

- **Form field errors:** `errorlist`
- **Form non-field errors:** `errorlist nonfield`
- **FormSet non-form errors:** `errorlist nonform`

The new class must also be documented for developers. This includes the docs section on rendering form error messages, or an equivalent section in the formset docs.

**User story:** As a developer rendering a formset, I want non-form errors marked with a `nonform` class. That way my templates, CSS, or custom `ErrorList` can render them distinctly.

## Tech Stack

- Django forms framework (Python). Specifically the `ErrorList` and FormSet classes.
- Python and Django versions: **unknown**. The target branch is assumed to be the current development branch.

## Commands

| Purpose | Command |
|---|---|
| Build | unknown |
| Test | unknown (the project's test runner; scope to the forms/formsets test modules) |
| Lint | unknown |
| Docs build | unknown |

## Project Structure

Unknown. These are the expected areas of change, with paths to be confirmed in the repo:

- The FormSet implementation, where non-form errors are built.
- The `ErrorList` utility. A change here is expected only if needed; ideally none is required.
- Forms/formsets test suites.
- Docs: the forms API page covering "rendering form error messages", the formsets topic page, and the release notes for the next feature release.

## Code Style

Follow the existing convention used for `nonfield` in Forms: pass the CSS class through the `ErrorList`'s `error_class` argument at every place the non-form `ErrorList` is constructed. Do not use a new mechanism. No snippet is included because the existing source is not visible.

## Testing Strategy

- **Framework:** the project's existing test framework (unknown).
- **Unit tests in the formset tests** should assert that `non_form_errors()` yields an `ErrorList` whose rendered HTML contains `class="errorlist nonform"`. Cover each source of non-form errors:
  - an error raised from a custom formset `clean()`
  - too many forms submitted (max_num / validate_max)
  - too few forms submitted (min_num / validate_min), if supported
  - a missing or tampered management form, if those errors surface via non-form errors
  - the empty case: no errors, and the formset is either unbound or valid. The returned `ErrorList` should still carry the `nonform` class for consistency, or at minimum not break; see Open Questions.
- **Custom `ErrorList` test:** a formset configured with a custom `error_class` passes `nonform` through to the custom class.
- **Regression:** existing tests expecting `class="errorlist"` for non-form errors need updating. Form `nonfield` tests must stay unchanged and passing.
- **Coverage expectation:** every code path that builds the non-form `ErrorList` is exercised.

## Boundaries

- **Always:**
  - Mirror the `nonfield` implementation pattern.
  - Update the docs and add a release note.
  - Run the full forms/formsets test suites before committing.
- **Ask first:**
  - Any change to `ErrorList`'s constructor signature or rendering logic.
  - Any change to the rendered output of non-field or field errors.
  - Backporting to stable branches.
- **Never:**
  - Remove or rename existing CSS classes.
  - Change the error *contents* or ordering.
  - Alter Form `nonfield` behavior.
  - Delete existing tests rather than updating their expected output.

## Success Criteria

1. Rendering a FormSet's non-form errors as HTML produces `<ul class="errorlist nonform">…</ul>` in every case where non-form errors exist. This holds whether they come from `clean()`, max/min form count validation, or management form validation.
2. The non-form `ErrorList` has `nonform` in its CSS classes, consistent with how `nonfield` is applied for Forms.
3. A formset using a custom `ErrorList` subclass receives `error_class='nonform'` when its non-form error list is created.
4. Field errors still render with `class="errorlist"` only.
5. Form non-field errors still render with `class="errorlist nonfield"` only.
6. The docs describe the `nonform` class next to the existing `nonfield` documentation, and/or in the formsets docs, with an example of the rendered output.
7. A release note announces the new CSS class.
8. All existing and new tests in the forms/formsets suites pass.

## Open Questions

1. Should the empty non-form `ErrorList` also carry the `nonform` class? This covers both an unbound formset and a formset before `full_clean()`. Matching Forms' behavior is assumed, but this needs confirmation.
2. Are there other places that construct the non-form error list besides the main clean path? Examples include a fallback when `_non_form_errors` is `None`, or management-form error paths. The list of construction sites must be confirmed in the source.
3. Which docs pages should be updated? Options are the forms API "rendering form error messages" section, the formsets topic guide, or both.
4. Which release should this target, and should the release note go under "Forms" minor features?
5. Is the extra CSS class in rendered HTML acceptable as a non-breaking change? Third-party code asserting exact HTML (`class="errorlist"`) for formset errors would see different output.
6. Should formset templates or renderers in other output formats (e.g. `as_text`, JSON output) be affected? The assumption is that only the HTML class changes.
7. Repository paths and the test, build, and lint commands are unknown and need to be supplied.