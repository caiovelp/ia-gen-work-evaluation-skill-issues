# Spec: Valid JSON for Read-Only `JSONField` Values in the Django Admin

## Objective

When a model `JSONField` is shown read-only in the Django admin, its value is rendered as a Python literal instead of JSON. For example, `{"foo": "bar"}` appears as `{'foo': 'bar'}`. That output is not valid JSON, cannot be copied back into a JSON input, and does not match what users see when the field is editable.

**Goal:** Read-only `JSONField` values in the admin are rendered as valid JSON. Rendering goes through the same serialization path the editable form field uses (the form `JSONField`'s `prepare_value`), so the read-only and editable views stay consistent.

**Users:** Django admin users viewing `JSONField` data, and developers who mark `JSONField`s as `readonly_fields`.

**Proposed approach (from the issue, to be validated):** Add a special case for `JSONField` in `django.contrib.admin.utils.display_for_field` that delegates to the form `JSONField`'s `prepare_value`. The issue says not to call `json.dumps` directly, because `prepare_value` already handles the `InvalidJSONInput` case.

### Acceptance criteria

1. A read-only `JSONField` holding `{"foo": "bar"}` displays as `{"foo": "bar"}` (double quotes, valid JSON). It does not display as `{'foo': 'bar'}`.
2. All JSON value types render as valid JSON:
   - nested objects
   - lists
   - strings
   - numbers
   - booleans (`true`/`false`, not `True`/`False`)
   - JSON `null` inside structures (`null`, not `None`)
3. Serialization uses the form field's `prepare_value`, not a direct `json.dumps` call, so `InvalidJSONInput` values are handled the way the form field handles them.
4. A custom `encoder` configured on the model `JSONField` is respected, matching how the editable form field serializes.
5. An empty value (`None` / SQL NULL) behaves as it does for other fields: it shows the admin's empty value display. See Open Questions about JSON `null` versus SQL NULL.
6. Output is still HTML-escaped wherever the admin currently escapes `display_for_field` output. No new XSS vector is introduced.
7. Display of all non-`JSONField` fields is unchanged.
8. Regression tests cover the cases above and pass, and the existing admin test suites still pass.

## Assumptions

1. The bug is in `django.contrib.admin.utils.display_for_field`, as the issue states. Read-only admin fields (and possibly changelist cells) get their display string from this function.
2. The current behaviour comes from a fall-through branch that calls `str()` (or similar) on the Python value, which produces the `repr`-style dict.
3. The form field `django.forms.JSONField` exposes `prepare_value`, which serializes Python values to JSON and passes `InvalidJSONInput` through unchanged.
4. The model `JSONField` carries an optional `encoder`, which must reach the form field used for serialization.
5. The fix belongs in Django core (`django.contrib.admin`), not in user code or a third-party package.
6. Existing ordering in `display_for_field` stays in place: choices/flatchoices first, then booleans, then the empty-value handling. The `JSONField` case is added without disturbing these.
7. No database or migration changes are required.
8. The Django version, Python version, and supported database backends are those of the current development branch. The exact versions are unknown.

## Tech Stack

- Python and Django (exact versions unknown)
- Components involved:
  - `django.contrib.admin.utils` (`display_for_field`)
  - `django.db.models.JSONField`
  - `django.forms.JSONField` (`prepare_value`, `InvalidJSONInput`)
- No new dependencies.

## Commands

The repository is not visible, so all commands are unknown.

- Build: unknown (a pure-Python change is likely; no build step expected)
- Test: unknown. The project's test runner and the admin-related test module labels need confirming.
- Lint: unknown. The project's configured linters/formatters need confirming.
- Dev: unknown

## Project Structure

Only the following module is known from the issue:

- `django/contrib/admin/utils.py` → contains `display_for_field` (the change site)

These locations are unknown:

- the model `JSONField` and the form `JSONField` source files
- the tests for `display_for_field` / admin utils
- the tests for admin read-only field rendering
- the release notes / docs location for a bugfix entry

## Code Style

The project's style guide and an example snippet are unknown (repository not visible). Follow the conventions of the surrounding code in `django/contrib/admin/utils.py`, including:

- the existing `isinstance` / field-type dispatch style used in `display_for_field`
- import style
- line length and formatting as enforced by the project's linters

## Testing Strategy

- **Framework:** the project's existing test framework and runner. The exact invocation is unknown.
- **Unit level (`display_for_field`):** call it directly with a `JSONField` and these values:
  - a dict
  - a nested dict/list
  - a list
  - a string
  - a number
  - a boolean
  - a structure containing JSON `null`
  - `None` (empty value)
  - an `InvalidJSONInput` instance
  - a value that needs a custom `encoder` (e.g., a type the default encoder cannot serialize)
- **Integration level (admin):** render a change view where a `JSONField` is in `readonly_fields`. Assert:
  - the rendered content shows valid JSON
  - the output is HTML-escaped as before
- **Regression:** existing admin utils and admin view tests pass unchanged. Non-`JSONField` displays are unaffected.
- **Coverage:** every new branch in `display_for_field` is exercised by at least one test.

## Boundaries

**Always:**
- Use the form field's `prepare_value` for serialization (per the issue).
- Respect the model field's `encoder`.
- Preserve HTML escaping of admin output.
- Add regression tests.
- Keep behaviour for other field types unchanged.

**Ask first:**
- Changing display behaviour in the changelist (`list_display`) as well as read-only change-form fields, if both share `display_for_field`.
- Changing how `None` / JSON `null` is displayed.
- Pretty-printing or indentation choices.
- Touching `display_for_value` or other admin utilities.
- Adding release notes or changing the public API.

**Never:**
- Call `json.dumps` directly in place of `prepare_value`.
- Introduce unescaped HTML output.
- Add dependencies.
- Change database or model field behaviour.
- Remove or weaken existing tests.

## Success Criteria

- `display_for_field` returns valid JSON (parseable with a JSON parser) for every JSON-serializable value of a model `JSONField`. The verified example is `{"foo": "bar"}` → `{"foo": "bar"}`.
- `InvalidJSONInput` values are rendered the same way the form `JSONField.prepare_value` renders them, without raising.
- Values that need the field's custom `encoder` serialize successfully using that encoder.
- An empty value (`None`) renders as the configured empty value display, unless the Open Questions decide otherwise.
- The admin change view with a read-only `JSONField` shows JSON-formatted, HTML-escaped content.
- New tests fail before the change and pass after it. The full existing admin test suite passes.

## Open Questions

1. **Scope of surfaces:** `display_for_field` is likely used by both read-only change-form fields and changelist columns. Should the changelist display also switch to JSON, or should only read-only fields change?
2. **JSON `null` vs SQL NULL:** A top-level JSON `null` stored in the field likely reaches `display_for_field` as Python `None`, the same as SQL NULL. Should it show the empty value display or the literal `null`? Is distinguishing them in scope?
3. **Constructing the form field:** Should `prepare_value` be invoked on a form field obtained from the model field's `formfield()`, or on a directly instantiated `forms.JSONField(encoder=field.encoder)`? This matters for custom `JSONField` subclasses that override `formfield()`.
4. **Formatting:** Should the read-only output match the editable widget exactly, including any non-ASCII handling and spacing? Or is compact JSON acceptable? Should pretty-printing or indentation be considered (probably out of scope)?
5. **`InvalidJSONInput` reachability:** In which real admin flows can a read-only field's value be an `InvalidJSONInput`? Is a direct unit test sufficient to cover it?
6. **Serialization errors:** If the encoder fails (e.g., an unserializable value with no suitable encoder), should the display fall back to the previous `str()` output, or should the error propagate?
7. **Subclasses:** Should subclasses of `JSONField` (including third-party ones) get the new behaviour via an `isinstance` check?
8. **Process:** Is a release note required, and should the fix be backported to supported release branches?
9. **Unknown tooling:** What are the project's exact test, lint, and build commands, and where do the relevant test modules live?