# Spec: Expose Model Class in Admin `app_list` Context (and Public App-Dict Builder)

## Objective

A developer building a custom admin view needs to manipulate the `app_list` structure. Each model entry is currently a serialized dictionary. It does not carry the model class, so the developer cannot easily get to the model's attributes, `_meta`, or methods.

The issue requests two changes:

1. **Add the model class to each model entry in `app_list`.** Code that consumes `app_list`, such as custom views, templates and template tags, can then reach the actual model class directly.
2. **Make the `_build_app_dict` method public.** It is used by both the `index` and `app_index` views, and custom admin views would like to reuse it without calling a private API.

**User:** Developers who extend or customize the admin site with custom views or templates that consume `app_list`.

**User stories:**
- As a developer writing a custom admin view, I want each model entry in `app_list` to include its model class, so that I can filter, sort or annotate entries using real model metadata.
- As a developer, I want a public, supported method that builds the app dictionary, so that my custom views can produce the same structure as `index` and `app_index` without relying on a private method.

**Acceptance criteria (draft):**
- Every model entry in `app_list` contains a new key holding the model class. The key name is proposed as `model`; see Open Questions.
- All existing keys in each model entry keep their current names, values and semantics.
- The `index` and `app_index` views both produce entries containing the model class.
- A public method with the same behavior as the current `_build_app_dict` exists, and both `index` and `app_index` use it.
- Code that currently calls `_build_app_dict` keeps working, or follows a documented deprecation path (to be decided; see Open Questions).
- The new context key and, if made public, the method are documented.

## Assumptions

1. This is the Django project. `app_list`, `index`, `app_index` and `_build_app_dict` refer to Django admin's admin site class. The issue does not name the file or class explicitly.
2. `app_list` is a list of app dictionaries, and each app dictionary contains a list of per-model dictionaries. The model class is added to those per-model dictionaries, not to the app dictionaries.
3. "Serialized model" in the issue means the per-model dictionary of display data (names, URLs, permissions). It does not mean a serialized model instance.
4. Adding a new key to the per-model dict is backward compatible for existing templates and consumers.
5. The model class is added as-is, the class object itself. It is not an instance, a string path or a content type.
6. A public method keeps the same signature and return shape as the current `_build_app_dict`.
7. Permission filtering is unchanged. Only models the user may see appear in `app_list`, so exposing the class does not widen access.
8. The change targets the next feature release. It is not a backport.

## Tech Stack

- Python / Django (the admin contrib app). Exact supported versions: **unknown**, not stated in the issue.
- No new dependencies expected.

## Commands

All unknown, because none are given in the issue and the repository is not visible:

- Build: unknown
- Test: unknown (Django's own test runner is presumed, but the exact invocation is not stated)
- Lint: unknown
- Dev: unknown

## Project Structure

Unknown from the issue. Relevant locations to be confirmed:

- The admin site class that defines `index`, `app_index` and `_build_app_dict`: location unknown.
- Admin tests covering `index` / `app_index` context: location unknown.
- Admin documentation describing `AdminSite` methods and template context: location unknown.
- Release notes for the target version: location unknown.

## Code Style

Unknown; follow the existing conventions of the surrounding admin code. No example snippet is available from the issue.

Conventions inferred from the issue:
- Private methods use a leading underscore (`_build_app_dict`). A public counterpart would drop the underscore, for example `build_app_dict`. The final name is subject to review.

## Testing Strategy

- **Framework:** the project's existing test framework. The exact setup is unknown.
- **Test level:** integration-style tests that request the admin `index` and `app_index` views and inspect the `app_list` context variable. Unit-level tests of the builder method can be added if it becomes public.
- **Cases to cover:**
  - `index` context: each model entry includes the model class, and it is the correct class (identity check).
  - `app_index` context: same as above, scoped to the single app.
  - Existing keys in model entries remain present and unchanged (regression).
  - If the method is made public, calling it directly returns the same structure the views use, including the label-filtered variant used by `app_index`.
  - If a deprecation path is chosen for `_build_app_dict`, the old name still works and emits the agreed warning.
- **Coverage expectation:** unknown; at minimum every new or changed behavior above is covered.

## Boundaries

- **Always:**
  - Preserve existing keys and values in `app_list` entries.
  - Keep permission filtering identical; only already-visible models get the class attached.
  - Document new public API and context keys, and add a release note.
  - Run the admin test suite before submitting.
- **Ask first:**
  - The name of the new context key.
  - Whether to make `_build_app_dict` public, and if so its name and signature.
  - Whether to keep, alias or deprecate `_build_app_dict`.
  - Any change to the shape of `app_list` beyond adding the model class.
- **Never:**
  - Remove or rename existing context keys.
  - Expose models the requesting user lacks permission to see.
  - Change the rendered output of the default admin templates as a side effect.
  - Remove `_build_app_dict` without an agreed compatibility or deprecation path.

## Success Criteria

1. Requesting the admin index view gives an `app_list` in which every model entry exposes the corresponding model class under the agreed key.
2. Requesting an app's index view gives the same result for that app's models.
3. All pre-existing admin tests pass without modification. Existing keys are unchanged.
4. If approved, a public app-dict builder method exists, is used by both `index` and `app_index`, and is documented. Its relationship to `_build_app_dict` (alias, deprecation or replacement) matches the approved decision.
5. Documentation and release notes describe the new key and, if applicable, the public method.

## Open Questions

1. **Key name:** Should the model class be exposed as `model`, or under another name? Does it collide with any existing key?
2. **Scope split:** The issue bundles two changes: adding the model class and making the method public. Should both ship together, or should the public-method change be handled or decided separately?
3. **Public method decision:** Should `_build_app_dict` actually become public? If yes, what is its name (for example `build_app_dict`) and is its current signature acceptable as a stable public API?
4. **Compatibility of `_build_app_dict`:** Keep it as an alias, deprecate it with a warning, or leave it alone alongside a new public method?
5. **Related methods:** Should other app-list helpers (for example a method returning the full sorted `app_list`, if one exists) be documented alongside this change? This is unknown from the issue.
6. **Target version:** Which release does this target, and is this considered a new feature (release notes) rather than a bug fix?
7. **Documentation location:** Where are `AdminSite` methods and the admin template context documented, so that the new key and method can be added?
8. **Commands / paths:** What are the exact test, lint and build commands and file locations? None are given in the issue.