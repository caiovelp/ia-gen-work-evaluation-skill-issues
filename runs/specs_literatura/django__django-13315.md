## Summary

Passing a `Q` object as `limit_choices_to` on a `ForeignKey` can render duplicate options in the generated form field when the `Q` object involves a join.

## Steps to reproduce

1. Define a model with a `ForeignKey` field.
2. Set `limit_choices_to` on that `ForeignKey` to a `Q` object whose condition involves a join.
3. Render a form containing the form field for this `ForeignKey`.
4. Inspect the available options in the form field.

## Observed behavior

The form field may contain duplicate options.

## Expected behavior

Each choice should appear only once in the form field. (This is implied by the report, which describes the duplicates as a problem.)

## Stack trace / error output

Not provided in the original report.

## Test case

The original report refers to a regression test included in an attached patch ("See regressiontest in patch for a clear view on the problem"). The test itself is not included in the report text.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report.