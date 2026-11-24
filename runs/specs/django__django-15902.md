# Spec: Suppress "default.html" Template Deprecation Warning for Formset ManagementForm

## Assumptions

1. This issue is in the Django web framework (`django.forms`). It concerns the deprecation of the default form template `"default.html"` (table-style rendering) in favour of a div-based template.
2. The warning is emitted when a form is rendered through the form renderer with the deprecated default template, and no project-level `FORM_RENDERER` or template override opts in to the new style.
3. When a formset is rendered, its `ManagementForm` is also rendered. That rendering goes through the same template path, so it raises the deprecation warning even when the project never renders forms with `{{ form }}`.
4. The `ManagementForm` contains only hidden inputs (`TOTAL_FORMS`, `INITIAL_FORMS`, `MIN_NUM_FORMS`, `MAX_NUM_FORMS`). For hidden-only output, the table and div templates produce the same visible result, so the warning gives the user nothing to act on.
5. The intended outcome is to stop the warning for management forms only. The deprecation warning for user-facing forms must stay as it is.
6. The fix targets the Django release line that carries this deprecation. The exact version is unknown.
7. The exact source files, class names and warning category for the deprecation are not visible in the issue. They are treated as unknown below.

## Objective

**Problem:** Developers who never render forms with the deprecated default template still get the `"default.html"` deprecation warning. This happens because rendering a formset also renders its `ManagementForm`, and that form uses the default template internally. The warning is noise: the developer cannot act on it, and it hides real deprecation warnings from their own forms. It also breaks test suites that run with warnings treated as errors.

**User:** A Django developer who uses formsets and has either moved off the deprecated form templates or never relied on them.

**Desired behaviour:**
- Rendering a formset's `ManagementForm`, alone or as part of rendering the formset, does **not** emit the `"default.html"` deprecation warning.
- Rendering an ordinary form with the deprecated default template **still** emits the warning, exactly as before.
- The HTML produced for the `ManagementForm` stays semantically the same: the same hidden inputs, names, ids and values.

**Acceptance criteria:**
- AC1: Rendering a formset with default settings emits no `"default.html"` deprecation warning that comes from its `ManagementForm`.
- AC2: Rendering a `ManagementForm` directly (e.g. `str(formset.management_form)`) emits no such warning.
- AC3: Rendering a regular `Form` with the deprecated default template still emits the deprecation warning. Its message and category are unchanged.
- AC4: The `ManagementForm` output keeps the same hidden inputs as before:
  - names, ids and values are unchanged;
  - no visible labels or table rows are introduced.
- AC5: Formset validation behaviour is unchanged, including handling of a missing or tampered management form.

## Tech Stack

- Python, Django (`django.forms`: forms, formsets, form renderers, templates).
- Exact Python and Django versions: **unknown**. This is the release that introduced the `"default.html"` deprecation.

## Commands

All commands are **unknown**; they are not stated in the issue. Django's test runner is presumably used:

```
Test: unknown (e.g. Django's tests/runtests.py with a forms/formsets test label; not confirmed)
Lint: unknown
Build: N/A (library)
```

## Project Structure

**Unknown.** The issue does not reference any file paths. The relevant areas are presumably:
- the module defining `BaseFormSet` and `ManagementForm`;
- the module emitting the `"default.html"` deprecation warning (form rendering / renderer utilities);
- the forms and formsets test suites.

These must be located before planning.

## Code Style

Follow existing Django coding conventions in the touched modules. No code snippet is available from the issue. Style specifics are **unknown** beyond "match surrounding code".

## Testing Strategy

- **Level:** unit and regression tests in Django's existing forms/formsets test suites. The location is unknown.
- **Required tests:**
  - A regression test asserting no deprecation warning is emitted when rendering a formset's management form under default settings (AC1, AC2).
  - A test, or confirmation that one already exists, that a regular form rendered with the deprecated default template still emits the warning (AC3).
  - An assertion on the management form's rendered HTML: hidden inputs only, with unchanged names, ids and values (AC4).
  - The existing formset validation tests continue to pass (AC5).
- **Coverage expectation:** every acceptance criterion is covered by at least one test.

## Boundaries

- **Always:**
  - Keep the deprecation warning for user-rendered forms intact.
  - Add regression tests.
  - Keep the `ManagementForm` HTML output equivalent.
  - Follow Django's deprecation policy.
- **Ask first:**
  - Changing the public API of `ManagementForm` or `BaseFormSet` (e.g. new public attributes or template names).
  - Changing the warning message or category.
  - Adding a release-notes entry and choosing which release it targets.
  - Backporting the change.
- **Never:**
  - Globally silence or remove the `"default.html"` deprecation warning.
  - Change the rendered output of non-management forms.
  - Alter formset validation semantics.
  - Remove or weaken existing tests.

## Success Criteria

- With default settings, rendering any formset (and its `management_form`) produces zero `"default.html"` deprecation warnings that come from the management form.
- Regular forms rendered with the deprecated default template still produce the same deprecation warning.
- The management form HTML contains the same hidden inputs, with identical names, ids and values, as before the change.
- The existing forms and formsets test suites pass, and the new regression tests pass.

## Open Questions

1. **Scope of the special case:** Should only `ManagementForm` be exempt? Or should any form consisting solely of hidden fields also skip the warning?
2. **Mechanism preference:** Should the exemption come from giving `ManagementForm` a template that is not deprecated? Or should the warning check be skipped specifically for management forms? This has implications for custom renderers and for users who override formset templates.
3. **Output change tolerance:** If the management form switches templates, is a whitespace or markup difference acceptable as long as the hidden inputs are identical?
4. **Custom renderers / overrides:** Should a project that customises `ManagementForm` rendering, or the formset `management_form` template, see any change in behaviour?
5. **Target release and backport:** Which Django version should this land in? Should it be backported to the stable branch where the deprecation was introduced?
6. **Release notes:** Is a release-notes entry required, or is this treated as a bug fix without notes?
7. **Commands and paths:** What are the exact test commands, and which source and test files are involved? These are not determinable from the issue.