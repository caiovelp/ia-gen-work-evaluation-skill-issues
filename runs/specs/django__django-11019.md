# Spec: Order-independent merging of 3+ Media objects without spurious MediaOrderConflictWarning

## Objective

When a form combines the `Media` of three or more widgets, Django merges the lists one pair at a time. Each pairwise merge can create an ordering constraint that no input actually declared. A later merge then sees a conflict that does not exist, so Django:

1. emits a `MediaOrderConflictWarning` that should not be raised, and
2. produces an asset order that breaks a dependency the inputs did declare.

**Who is affected:** Django users who build forms or widgets whose combined `Media` comes from three or more sources. Third-party widget and admin authors are affected too, because they cannot control the order in which their widgets are combined.

**Reproduction from the issue:**

```python
from django import forms
class ColorPicker(forms.Widget):
    class Media:
        js = ['color-picker.js']
class SimpleTextWidget(forms.Widget):
    class Media:
        js = ['text-editor.js']
class FancyTextWidget(forms.Widget):
    class Media:
        js = ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']
class MyForm(forms.Form):
    background_color = forms.CharField(widget=ColorPicker())
    intro = forms.CharField(widget=SimpleTextWidget())
    body = forms.CharField(widget=FancyTextWidget())
```

**Current behaviour:** `MyForm().media` warns that `text-editor-extras.js` and `text-editor.js` are in opposite order. It returns `js=['text-editor-extras.js', 'color-picker.js', 'text-editor.js']`, which places `text-editor-extras.js` before its dependency `text-editor.js`.

**Expected behaviour:** No warning. It returns `js=['text-editor.js', 'text-editor-extras.js', 'color-picker.js']`.

**Root cause stated in the issue:** `ColorPicker().media + SimpleTextWidget().media` yields `['color-picker.js', 'text-editor.js']`. That result imposes a "color-picker before text-editor" constraint that neither input declared.

**Secondary problem:** The warning names the wrong pair of files. The genuinely misordered pair is `color-picker.js` and `text-editor.js`, but the warning reports a different pair.

### User stories / acceptance criteria

- As a form author, combining several widgets' media gives a final order that respects every ordering declared in any single input list. This holds whenever such an order exists, regardless of how many widgets there are or what order they are declared in.
- As a form author, I see a `MediaOrderConflictWarning` only when the inputs genuinely contradict each other. An example is one list declaring A before B while another declares B before A.
- When a genuine conflict is reported, the files named in the warning are the files that are actually in conflict.

## Tech Stack

- Django, in the `django.forms` Media subsystem. The traceback points at `django/forms/widgets.py`, the module that defines `MediaOrderConflictWarning`.
- Python. Supported versions are unknown, as is the target Django branch or version (see Open Questions).
- The issue refers to "Django 1.11 before order-checking was added", so the bug exists in versions after 1.11.

## Commands

- Build: unknown (not stated in the issue)
- Test: unknown. Django's test runner invocation is not given in the issue.
- Lint: unknown
- Dev: not applicable (library change)

## Project Structure

- `django/forms/widgets.py`: contains the `Media` class, its merge logic, and `MediaOrderConflictWarning`. The path is known from the traceback in the issue.
- Location of the existing forms/media tests: unknown.
- Location of documentation for form assets/Media ordering, and of release notes: unknown.

## Code Style

- Follow existing Django conventions in `django/forms/widgets.py`. No snippet is available beyond the issue.
- Coding style rules (e.g. flake8/isort configuration): unknown.

## Testing Strategy

- **Level:** unit tests for `Media` merging, using the existing forms/media test suite. Its location and framework invocation are unknown; it is presumably Django's own `unittest`-based test suite.
- **Required test cases:**
  1. **The issue's reproduction:** three widgets combined in a form give `js == ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']` with no `MediaOrderConflictWarning` raised.
  2. **Order-independence:** the same three media objects, combined in every permutation of declaration order, all respect the declared dependencies (`text-editor.js` before `text-editor-extras.js`) and emit no warning. Whether the exact final list must be identical across permutations is an open question.
  3. **Genuine conflict:** two lists declaring `[A, B]` and `[B, A]` still emit `MediaOrderConflictWarning`.
  4. **Warning content:** in a genuine conflict, the warning message names the conflicting files.
  5. **Regression:** existing two-object merge behaviour and existing Media tests still pass. This includes CSS merging per media type, duplicate removal, and `Media` defined via `media` property or `class Media` with `extend`.
  6. **CSS parity:** CSS lists that hit the same 3+ merge scenario behave consistently with JS.
- Tests should assert on warnings explicitly. They must assert that no warning occurs in the valid case and that one does occur in the conflict case.
- Coverage expectations: unknown. At minimum, cover the merge function's conflict and non-conflict paths.

## Boundaries

- **Always:**
  - Preserve every relative order declared within any single input list whenever a consistent order exists.
  - Keep de-duplication of repeated assets.
  - Keep the public API unchanged: `Media`, `Media.__add__`, `Media.merge` (if public), and the `MediaOrderConflictWarning` class and its category.
  - Add regression tests for the issue's exact scenario.
- **Ask first:**
  - Changing the internal representation of `Media` objects. For example, keeping the original per-source lists instead of eagerly merged lists, which affects `__repr__`, pickling, and subclasses.
  - Changing the public or semi-public signature of `Media.merge`.
  - Changing the documented ordering guarantees, or the stable order produced for inputs with no dependencies between them.
  - Changing warning text that users or tests may match on.
  - Backporting to stable branches.
- **Never:**
  - Remove or silence `MediaOrderConflictWarning` for genuine conflicts.
  - Delete or weaken existing Media tests to make the change pass.
  - Introduce new dependencies.

## Success Criteria

1. `MyForm().media` from the issue returns `js=['text-editor.js', 'text-editor-extras.js', 'color-picker.js']`.
2. Accessing `MyForm().media` emits zero `MediaOrderConflictWarning`s.
3. For any number (≥3) of Media inputs whose declared orderings are mutually consistent, the merged result is warning-free and satisfies every declared pairwise ordering. This holds independent of the order in which inputs are added.
4. For inputs with a genuine ordering contradiction, a `MediaOrderConflictWarning` is still emitted, and it names files that are actually in conflict.
5. All pre-existing Media/forms tests pass unchanged, unless an expected-output change is explicitly approved.
6. Merging the media of a form with many widgets shows no pathological performance regression. The threshold is unknown; see Open Questions.

## Assumptions

1. The bug is caused by eager pairwise merging, which loses which constraints came from real inputs versus artifacts of earlier merges, as described in the issue.
2. Ordering constraints come only from the relative order of items within each individually declared list (a widget's `class Media` / `media`). Concatenating two independent lists is not intended to create a constraint between their items.
3. When items have no declared relative order, any order is acceptable, but the result should be deterministic. Preferring declaration/first-appearance order is desirable.
4. The same reasoning and fix apply to CSS lists (per medium) as to JS lists.
5. Adding `Media` objects with `+`, including via form/widget media aggregation, is the code path in scope.
6. The fix targets Django's main development branch.

## Open Questions

1. Which Django branch or version is targeted, and should the fix be backported to stable releases?
2. Must the merged order be identical regardless of the order in which widgets are declared on the form, or only consistent with declared dependencies?
3. For unrelated assets, is there a required tie-breaking rule, such as first-seen order? Should results for existing two-object merges remain byte-for-byte identical?
4. When a genuine conflict exists, which pair(s) should the warning report, what should the resulting fallback order be, and may the warning message text change?
5. Is changing `Media`'s internal storage acceptable? This could affect `__repr__`, subclasses, and code that reads `_js`/`_css` directly.
6. Is there a performance budget for merging media on forms with many widgets?
7. Where do the relevant tests and docs live, and are documentation or release-note updates required? (Unknown from the issue.)
8. Should `Media` objects built manually, e.g. `Media(js=[...])` added to widget media, be treated the same as `class Media` declarations for constraint purposes?