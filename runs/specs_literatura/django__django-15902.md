## Summary

The deprecation warning about the `"default.html"` form template is raised when a formset's management form is produced, even if the project never renders forms with the `{{ form }}` expression. For the management form, the template choice does not matter because it only outputs hidden inputs.

## Steps to reproduce

1. Use a project that never renders forms with the `{{ form }}` expression.
2. Use a formset, so that its management form is produced.
3. Observe the warnings emitted.

## Observed behavior

The new template deprecation warning (relating to `"default.html"`) is raised while the formset's management form is produced, although the project never renders forms with `{{ form }}`.

## Expected behavior

The deprecation warning should not be raised for the management form. The template it uses makes no difference to the output, since it only produces hidden inputs, and the project does not otherwise rely on `{{ form }}` rendering.

## Stack trace / error output

Not provided in the original report. The exact warning text was not included.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

Not provided in the original report.