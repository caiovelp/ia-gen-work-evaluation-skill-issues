## Summary
In the Django admin, the `<label>` element rendered for the `ReadOnlyPasswordHashWidget` widget has a `for` attribute that points to a non-labelable element. The widget renders only text, not an input, so there is no labelable element for the label to reference.

## Steps to reproduce
1. Open an admin page that displays a field using `ReadOnlyPasswordHashWidget`.
2. Inspect the rendered HTML for that field's `<label>` element.
3. Note the value of the label's `for` attribute and find the element it references.

## Observed behavior
The `<label>` element has a `for` attribute. The element it points to is not labelable, because the widget renders plain text rather than an input element.

## Expected behavior
Because the widget has no labelable element, its `<label>` should not have a `for` attribute.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
Not provided in the original report. The issue occurs in the Django admin with `ReadOnlyPasswordHashWidget`.