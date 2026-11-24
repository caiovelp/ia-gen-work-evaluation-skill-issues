# Spec: Remove the `for` attribute from MultiWidget's `<label>`

## Objective

When a form field uses the base `MultiWidget` class, its `<label>` is generated as `<label for="{id}0">`. The label then points only at the first sub-widget, and the developer cannot change this.

Other widgets let the developer choose. The issue names `ChoiceWidget`, which has an `add_id_index` attribute. That attribute controls whether the label id gets an index suffix.

**Requested change (as stated in the issue):** remove the `id_for_label` method from the `MultiWidget` class entirely. The result should be that labels rendered for a raw `MultiWidget` no longer carry a `for="..._0"`-style attribute.

**Users:** Django developers who render forms containing `MultiWidget`-based fields, and the end users and assistive technologies that rely on `<label for>` linking.

**User stories / acceptance (draft):**
- As a developer using a raw `MultiWidget`, I want its label not to point arbitrarily at the first sub-widget.
- As a developer subclassing `MultiWidget`, I want to be able to define my own label-target behaviour, as `ChoiceWidget` allows.

## Assumptions

1. The project is Django. The class meant is `django.forms.widgets.MultiWidget`. The repository is not visible, so this is inferred from the class names in the issue.
2. "Remove `for = ...`" means the rendered `<label>` for a field whose widget is a raw `MultiWidget` should have no `for` attribute.
3. Today, `MultiWidget.id_for_label(id_)` returns `id_ + '0'`, i.e. `f'{id_}0'`. Exactly how it is built (for example, whether an underscore is included) is not visible.
4. Label rendering omits the `for` attribute when the widget's `id_for_label` returns a falsy value. This needs to be confirmed in the code.
5. Built-in `MultiWidget` subclasses may depend on the current base behaviour. Examples could include `SplitDateTimeWidget`, `SplitHiddenDateTimeWidget` and `SelectDateWidget`, but which of these inherit `id_for_label` is not visible. Their behaviour must be checked and decided explicitly, not changed silently.
6. This is a single capability, so no capability map (Phase 0) is needed.
7. This is a user-visible behaviour change. It will likely need release notes and a docs update.

## Tech Stack

- Python / Django. The supported versions are **unknown**.
- No new dependencies are expected.

## Commands

All of the following are **unknown**, because the repository is not visible:
- Build: unknown
- Test: unknown. Presumably Django's test runner, but the exact invocation and flags are not visible.
- Lint: unknown
- Dev: not applicable (library)

## Project Structure

**Unknown.** The likely locations below are inferred, not verified:
- Widget implementation: probably the forms widgets module, e.g. `django/forms/widgets.py`. **Unverified.**
- Label rendering: probably the bound-field or label-tag logic in the forms package. **Unverified.**
- Tests: forms/widgets test suite. **Path unknown.**
- Docs: widget reference docs and release notes. **Paths unknown.**

## Code Style

Unknown. Follow the existing conventions of the surrounding code; no snippet is available from the issue. The only API shape known from the issue is:
- `MultiWidget.id_for_label(id_)` exists and produces `f'{id_}0'`.
- `ChoiceWidget.add_id_index` is a boolean-like attribute that controls index suffixing.

## Testing Strategy

- **Framework:** Django's test suite. The exact runner and command are unknown.
- **Unit level:**
  - `MultiWidget().id_for_label('id_x')` returns the agreed value, which is still open (see Open Questions), instead of `'id_x0'`.
  - Built-in `MultiWidget` subclasses keep or change their `id_for_label` behaviour as explicitly decided.
- **Rendering level:**
  - A form field using a raw `MultiWidget` renders its label with no `for` attribute.
  - Fields using affected subclasses render labels as decided.
- **Regression:**
  - Run the existing forms and widgets tests.
  - Expect, and review deliberately, any assertions on rendered HTML that contain `for="..._0"`-style ids. Do not update them blindly.
- **Coverage:** the project's expectation is unknown. At minimum, every changed code path needs a test.

## Boundaries

- **Always:**
  - Run the existing forms and widget test suites.
  - Add tests for the new label behaviour.
  - Document the behaviour change.
- **Ask first:**
  - Changing `id_for_label` behaviour of built-in `MultiWidget` subclasses.
  - Choosing between deleting the method outright and overriding it with a "no label target" return.
  - Adding a configuration attribute similar to `add_id_index`.
  - Any deprecation path.
- **Never:**
  - Change `ChoiceWidget` / `add_id_index` behaviour.
  - Change how sub-widget `id` attributes are rendered. Only the label target is in scope.
  - Remove or weaken failing tests without approval.

## Success Criteria

1. A form field using a raw `MultiWidget` renders `<label>` with no `for` attribute.
2. `MultiWidget` no longer hard-codes the `f'{id_}0'` label target.
3. Subclasses of `MultiWidget` can still provide their own `id_for_label` and have it honoured in label rendering.
4. Behaviour of built-in `MultiWidget` subclasses matches an explicit, documented decision.
5. Sub-widget `id` attributes in the rendered widget HTML are unchanged.
6. The existing test suite passes, with any changed expectations reviewed and justified.
7. Docs and release notes describe the change.

## Open Questions

1. **Delete or override?** Literally deleting `id_for_label` from `MultiWidget` would make it inherit the base `Widget.id_for_label`. That base method likely returns `id_` unchanged, so the label would get `for="id_x"`. No sub-widget has that id, which may give a broken `for` instead of none. Should `MultiWidget.id_for_label` instead return an empty value, so that no `for` is rendered?
2. **Opt-in?** Should there be an opt-in attribute, analogous to `ChoiceWidget.add_id_index`, that lets developers keep the indexed label target? Or is overriding `id_for_label` in a subclass sufficient?
3. **Built-in subclasses.** Which built-in `MultiWidget` subclasses should keep pointing the label at a sub-widget, and which should drop `for`? Examples are `SplitDateTimeWidget` and `SelectDateWidget`.
4. **Deprecation.** Is a deprecation period required for this rendered-HTML change, or is a release-note mention sufficient?
5. **Accessibility.** With no `for`, the label is not programmatically associated with any input. Is that acceptable, or should an alternative such as `fieldset`/`legend` be considered? The latter is likely out of scope for this change.
6. **Commands and paths.** The exact test, lint and build commands and file paths are unknown and need confirmation from the repository.