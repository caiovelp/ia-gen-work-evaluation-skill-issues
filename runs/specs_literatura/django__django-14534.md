## Summary

`BoundWidget.id_for_label()` ignores the `id` that `ChoiceWidget.options` sets for each subwidget. It builds its own id with the hard-coded pattern `'id_%s_%s' % (name, index)` instead of using the id stored in `self.data['attrs']['id']`. If a form is created with a custom `auto_id`, the label ids for the subwidgets of a `CheckboxSelectMultiple` do not follow that `auto_id` format string. The reporter notes that this differs from `BoundField.id_for_label()`, which is not affected.

## Steps to reproduce

1. Define a form with a field that uses a `CheckboxSelectMultiple` widget.
2. Create the form and override the `auto_id` argument with a custom format string.
3. Go through the field's subwidgets (`BoundField.subwidgets`) and call `id_for_label()` on each `BoundWidget`. You can also render the labels of the subwidgets.
4. Compare the returned id with `widget.data['attrs']['id']` for the same subwidget, which is the id built from the `auto_id` format.

## Observed behavior

`BoundWidget.id_for_label()` always returns `'id_<name>_<index>'`, built from `self.data['name']` and `self.data['index']`. It ignores the id in `self.data['attrs']['id']`. As a result, the subwidget label ids do not follow a custom `auto_id` format string.

According to the reporter, this only happens when rendering the subwidgets of a `CheckboxSelectMultiple` widget. It is unrelated to `BoundField.id_for_label()`.

## Expected behavior

`BoundWidget.id_for_label()` should return the id that was computed for the subwidget, available as `self.data['attrs']['id']`. That id follows the `auto_id` format string given when the form was created.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Current implementation of `BoundField.subwidgets`, as quoted in the report:

```python
class BoundField:
    ...
    def subwidgets(self):
        id_ = self.field.widget.attrs.get('id') or self.auto_id
        attrs = {'id': id_} if id_ else {}
        attrs = self.build_widget_attrs(attrs)
        return [
            BoundWidget(self.field.widget, widget, self.form.renderer)
            for widget in self.field.widget.subwidgets(self.html_name, self.value(), attrs=attrs)
        ]
```

`self.field.widget.subwidgets(...)` returns dicts that are passed to `BoundWidget` as `widget`. In each one, `widget['attrs']['id']` holds the id that should be used for the label.

Current implementation of `BoundWidget.id_for_label`, as quoted in the report:

```python
class BoundWidget:
    ...
    def id_for_label(self):
        return 'id_%s_%s' % (self.data['name'], self.data['index'])
```

## Version and environment

Not provided in the original report.