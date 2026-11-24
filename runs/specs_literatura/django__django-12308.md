## Summary

In the Django admin, read-only `JSONField` values are displayed as a Python dict representation instead of valid JSON.

## Steps to reproduce

1. Have a model with a `JSONField`.
2. Register the model in the Django admin and mark the `JSONField` as read-only.
3. Store a value such as `{"foo": "bar"}` in the field.
4. Open the object's page in the admin and look at how the read-only field is displayed.

## Observed behavior

The value is displayed as a Python dict: `{'foo': 'bar'}`. This is not valid JSON because it uses single quotes.

## Expected behavior

The value should be displayed as valid JSON: `{"foo": "bar"}`.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report.