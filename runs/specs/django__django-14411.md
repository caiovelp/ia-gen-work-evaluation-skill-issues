# Spec: Remove `for` attribute from the label of `ReadOnlyPasswordHashWidget`

## Assumptions

1. The project is Django, and `ReadOnlyPasswordHashWidget` is the read-only password hash display used on the admin user change form. *Unverified: I have no repository access.*
2. The widget renders only text, such as the hash algorithm and a summary of the hash. It renders no `<input>`, `<select>`, `<textarea>` or other labelable element. This is stated in the issue.
3. The `for` attribute comes from the general rule for labels: a field's label gets `for="<id>"` whenever the widget reports a non-empty id for its label. The fix belongs at the widget or field level, not in admin templates. *Unverified.*
4. The `<label>` element itself should still render with its visible text. Only the `for` attribute should go away.
5. No other widgets are in scope.
6. This is a bug fix. No deprecation period or release note beyond normal practice is needed. *Unverified.*

## Objective

In the Django admin, the label for a field that uses `ReadOnlyPasswordHashWidget` has a `for` attribute. That attribute points to an id that is either missing or on a non-labelable element, because the widget renders only text. This is invalid HTML and an accessibility defect: assistive technology cannot follow the label to a control.

**Goal:** when a form field uses `ReadOnlyPasswordHashWidget`, its label renders without a `for` attribute. Everything else about the widget and the label stays the same.

**Users affected:**
- Admin users, especially those using screen readers or other assistive technology.
- Developers who render forms with this widget.

**Acceptance criteria:**
- Rendering the label of a bound field that uses `ReadOnlyPasswordHashWidget` produces `<label>` with no `for` attribute.
- The label text and any label suffix are unchanged.
- The widget's own output (the hash summary text) is unchanged.
- Labels for all other widgets keep their `for` attributes as before.

## Tech Stack

- Python / Django. Exact versions are **unknown**.

## Commands

All commands are **unknown** because the repository is not visible. Placeholders:

```
Test: <unknown — Django test runner invocation, e.g. targeting auth forms tests>
Lint: <unknown>
Build: n/a (library)
```

## Project Structure

**Unknown.** These locations are expected but not verified:

- The widget definition is presumably in the auth forms module of `django.contrib.auth`.
- Tests for auth forms are presumably in the auth tests directory.
- The generic label/`for` logic is presumably in Django's forms core (bound field / widget `id_for_label`).

## Code Style

**Unknown.** Follow the existing Django style in the files touched. No example code is provided, because none is visible.

## Testing Strategy

- Add a regression test that renders the label of a field using `ReadOnlyPasswordHashWidget` and asserts that the output has no `for` attribute.
- Add or keep a test that the widget's rendered output is unchanged.
- Rely on existing form and admin test suites to show that labels for other widgets still include `for`.
- Optionally, check the admin user change page HTML for the password field label.
- Framework and test file locations are **unknown**. Use the existing auth forms and admin test modules.

## Boundaries

- **Always:**
  - Add a regression test.
  - Keep the label element and its text.
  - Keep the change limited to this widget's labeling behavior.
  - Run the full forms, auth and admin test suites.
- **Ask first:**
  - Changing the generic label-rendering logic in forms core, beyond relying on existing extension points.
  - Changing admin templates.
  - Changing the widget's rendered markup.
  - Applying the same treatment to other non-labelable widgets.
- **Never:**
  - Remove the label entirely.
  - Change how password hashes are summarized or displayed.
  - Alter labels of other widgets.
  - Remove or weaken existing tests.

## Success Criteria

1. The label for a field using `ReadOnlyPasswordHashWidget` renders with no `for` attribute, both via the bound field's label tag and on the admin user change form.
2. The label text is unchanged.
3. The widget's rendered output is unchanged.
4. A new regression test fails before the fix and passes after it.
5. Existing forms, auth and admin tests all pass.

## Open Questions

1. Should the label stay a `<label>` element without `for`, or should it become different markup, such as plain text or a `<span>`?
2. Should the widget's rendered container keep any `id` attribute? Could removing it break custom CSS or JS that targets it?
3. Are there other read-only or text-only widgets, in admin or elsewhere, that should get the same fix? Or is scope strictly this widget?
4. Should the fix be general, so any widget can declare itself non-labelable, or specific to this widget?
5. Is a release note required, given that the rendered HTML changes slightly?
6. Which Django versions or branches should receive the fix?