## Summary
No error is raised when a blueprint name contains a dot (`.`). Because blueprints can now be nested, every dot in a name is significant. An equivalent error was already added for endpoint names in version 1.0, but the same check is missing for blueprint names.

## Steps to reproduce
1. Create a blueprint whose name contains a dot.
2. Observe that no error is raised.

(The original report does not include a reproduction snippet.)

## Observed behavior
A blueprint whose name contains a dot is accepted without any error.

## Expected behavior
An error is raised when a blueprint name contains a dot, consistent with the existing behavior for endpoint names containing a dot (added in 1.0). Dots are significant now that blueprints can be nested.

## Stack trace / error output
Not provided in the original report.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
Not provided in the original report. The report only notes that the corresponding error for endpoint names was added in version 1.0, and that blueprints can now be nested.