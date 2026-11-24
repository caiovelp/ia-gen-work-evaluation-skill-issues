## Summary

Merging the `Media` of three or more widgets can emit an unnecessary `MediaOrderConflictWarning` and produce a JS order that breaks a real dependency. In the example below, `text-editor-extras.js` depends on `text-editor.js`, and all other JS files are independent. A valid order exists (`text-editor.js`, `text-editor-extras.js`, `color-picker.js`). Instead, Django warns about a conflict and returns an order that puts `text-editor-extras.js` before `text-editor.js`.

The cause, according to the reporter, is the order in which the additions happen. `ColorPicker().media + SimpleTextWidget().media` produces `Media(css={}, js=['color-picker.js', 'text-editor.js'])`. That intermediate result wrongly imposes the constraint that `color-picker.js` must appear before `text-editor.js`.

## Steps to reproduce

1. Define the following widgets and form:
   - `ColorPicker` with `Media.js = ['color-picker.js']`
   - `SimpleTextWidget` with `Media.js = ['text-editor.js']`
   - `FancyTextWidget` with `Media.js = ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']`
   - `MyForm` with three `CharField`s using these widgets, in this order: `ColorPicker`, `SimpleTextWidget`, `FancyTextWidget`.
2. Access `MyForm().media`.
3. Observe the warning that is emitted and the resulting JS order.

## Observed behavior

- A `MediaOrderConflictWarning` is emitted. It reports `text-editor-extras.js` and `text-editor.js` as being in opposite order.
- The resulting media is:
  ```
  Media(css={}, js=['text-editor-extras.js', 'color-picker.js', 'text-editor.js'])
  ```
- In this result, `text-editor-extras.js` comes before `text-editor.js`, which it depends on.
- This result is worse than the "naïve" order Django 1.11 produced before order-checking was added: `color-picker.js`, `text-editor.js`, `text-editor-extras.js`.
- The pair of files named in the warning also seems wrong. The reporter points out that `color-picker.js` and `text-editor.js` are the pair that got wrongly ordered, through the intermediate merge.

## Expected behavior

- No `MediaOrderConflictWarning` is emitted, because the constraints can all be satisfied.
- `MyForm().media` resolves the JS files to:
  ```
  ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']
  ```

## Stack trace / error output

```
/projects/django/django/forms/widgets.py:145: MediaOrderConflictWarning: Detected duplicate Media files in an opposite order:
text-editor-extras.js
text-editor.js
 MediaOrderConflictWarning,
Media(css={}, js=['text-editor-extras.js', 'color-picker.js', 'text-editor.js'])
```

## Test case

This minimal test is derived from the reproduction snippet in the report:

```python
import warnings

from django import forms
from django.test import SimpleTestCase


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


class MergeThreeMediaTests(SimpleTestCase):
    def test_merge_three_media_no_spurious_conflict(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error', forms.widgets.MediaOrderConflictWarning)
            media = MyForm().media
        self.assertEqual(
            media._js,
            ['text-editor.js', 'text-editor-extras.js', 'color-picker.js'],
        )
```

## Code example

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

MyForm().media
```

The intermediate merge that introduces the wrong constraint:

```python
ColorPicker().media + SimpleTextWidget().media
# Media(css={}, js=['color-picker.js', 'text-editor.js'])
```

## Version and environment

- Exact Django version: Not provided in the original report. The report only says the behavior occurs in a version after Django 1.11, where media order-checking was added.
- The warning comes from `django/forms/widgets.py`, line 145, in the reporter's checkout at `/projects/django/`.
- Python version and OS: Not provided in the original report.