# Spec: BoundWidget.id_for_label should honor the id computed by ChoiceWidget.options

## Objective

`BoundWidget.id_for_label()` builds its own id string, `'id_%s_%s' % (name, index)`. It ignores the id that `BoundField.subwidgets()` and the widget's `subwidgets()`/`options()` already computed and stored in `self.data['attrs']['id']`.

The two ids can diverge in two cases:

- The form is created with a custom `auto_id` format string, for example `auto_id='custom_%s'`.
- The widget has an explicit `attrs={'id': ...}`.

When they diverge, each subwidget's `<input>` gets one id while its `<label for="...">` (and any template using `subwidget.id_for_label`) gets a different one. Labels are then not associated with their inputs. This breaks click-to-select and accessibility.

**Users:** Developers rendering multi-choice widgets subwidget by subwidget, such as `CheckboxSelectMultiple` (the case reported) and possibly `RadioSelect`, with a non-default `auto_id` or a widget-level `id`.

**Desired behavior:** `BoundWidget.id_for_label` returns the same id that is rendered on the corresponding subwidget's input element. That id is the one present in `self.data['attrs']['id']`.

**Acceptance criteria:**

1. With a custom `auto_id`, each `BoundWidget.id_for_label` equals the `id` attribute of the matching rendered input. For example, with `auto_id='prefix_%s'` the expected value is `prefix_<name>_<index>`, assuming the existing per-option suffix scheme.
2. With an explicit widget `attrs={'id': 'X'}`, each `BoundWidget.id_for_label` equals the rendered option id, for example `X_<index>`.
3. With the default `auto_id` (`'id_%s'`), output is unchanged from today: `id_<name>_<index>`.
4. When ids are disabled (`auto_id=False` or empty, and no widget id), `id_for_label` does not raise. It returns an empty or None value, consistent with how `BoundField.id_for_label` behaves without ids, and no bogus `for` attribute is rendered.
5. `BoundField.id_for_label` is unaffected. The issue states this explicitly.

## Assumptions

1. This is the Django forms framework. The classes involved are `BoundField`, `BoundWidget`, and `ChoiceWidget`. The issue suggests these live in Django's forms modules, but exact file paths are **unknown** (not visible).
2. `self.data` in `BoundWidget` is a per-option dict produced by `ChoiceWidget.options()`/`create_option()`. When an id is set, its `attrs` already contains the fully formatted per-option id, including the index suffix.
3. The issue says `subwidgets()` "returns a dict". I assume it actually yields one dict per option, and each `BoundWidget` wraps one of them.
4. `data['attrs']` always exists, but `'id'` may be absent when ids are disabled. The issue's proposed `self.data['attrs']['id']` could therefore raise `KeyError`, so a safe lookup is needed (AC 4).
5. Under default settings, the id stored in `attrs` today is identical to the hard-coded `'id_%s_%s'` string. The change is therefore backward compatible for default usage.
6. The issue says only `CheckboxSelectMultiple` is affected. I assume any `ChoiceWidget` subclass whose subwidgets are rendered through `BoundWidget` (e.g. `RadioSelect`) shares the bug and the fix.
7. Correct label/input association is the intended behavior, and nobody relies on the old divergent ids. This is a bug fix, not a breaking change.

## Tech Stack

- Python and Django (forms package). Versions are **unknown**.

## Commands

- Build: **unknown** (not visible in the issue)
- Test: **unknown**. Presumably the project's standard test runner, targeted at the forms tests.
- Lint: **unknown**
- Dev: N/A

## Project Structure

- Location of `BoundField` / `BoundWidget`: **unknown**. The issue does not give file paths.
- Location of `ChoiceWidget` / `CheckboxSelectMultiple`: **unknown**
- Location of forms tests: **unknown**

## Code Style

- Follow the existing style of the surrounding Django code. No snippet beyond the issue's excerpts is visible.
- The behavior currently quoted in the issue is:
  ```python
  def id_for_label(self):
      return 'id_%s_%s' % (self.data['name'], self.data['index'])
  ```

## Testing Strategy

- Unit or regression tests in the existing forms test suite. The location is **unknown**.
- Cover these cases:
  - A form using `CheckboxSelectMultiple` with a custom `auto_id`. Assert that each subwidget's `id_for_label` matches its rendered input id. Optionally assert that the rendered `<label for>` matches too.
  - A widget with an explicit `attrs['id']`. Make the same assertions.
  - The default `auto_id`. Assert the values are unchanged (regression guard).
  - `auto_id=False`. Assert there is no exception and the result is empty or None.
  - Optionally, `RadioSelect` for parity.
- All existing forms and widget tests must continue to pass.

## Boundaries

- **Always:**
  - Derive the label id from the already-computed option attrs (one source of truth).
  - Keep default-output compatibility.
  - Add regression tests.
- **Ask first:**
  - Changing how `ChoiceWidget.options()` / `id_for_label(id_, index)` formats per-option ids.
  - Changing `BoundField.id_for_label`.
  - Any change to rendered HTML under default settings.
- **Never:**
  - Change public signatures.
  - Remove or loosen existing tests.
  - Introduce `KeyError` when ids are disabled.

## Success Criteria

- Acceptance criteria 1–5 are covered by passing automated tests.
- For every subwidget, `BoundWidget.id_for_label == data['attrs'].get('id')` holds. This equals the rendered input id across default, custom `auto_id`, explicit widget id, and disabled-id configurations.
- The full existing test suite passes with no change to default rendered HTML.

## Open Questions

1. When ids are disabled, should `BoundWidget.id_for_label` return `None` or `''`? What does the subwidget label template expect, so that it omits the `for` attribute?
2. Should the fix explicitly cover all `ChoiceWidget` subclasses rendered via `BoundWidget` (e.g. `RadioSelect`), or is scope limited to `CheckboxSelectMultiple` as the issue states?
3. Does any template or third-party code depend on the old hard-coded `id_<name>_<index>` value even when a custom `auto_id` is set? Should this be noted in release notes?
4. Which Django versions or branches should receive the fix (main only, or backports)?
5. What are the test command and test file locations for the forms suite in this repository?