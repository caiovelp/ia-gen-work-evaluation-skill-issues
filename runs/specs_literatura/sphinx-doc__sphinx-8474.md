## Summary
After upgrading to Sphinx 3.3, builds started showing the warning `WARNING: no number is assigned for table:`. It appears with the `singlehtml` and `latex` builders. The reporter found nothing in the changelog that changed `numref` and wants to know which change in the numbering/`numref` logic causes these warnings.

## Steps to reproduce
1. Take an existing documentation project that built without this warning before Sphinx 3.3.
2. Upgrade Sphinx to version 3.3.
3. Build the documentation with the `singlehtml` builder or the `latex` builder.
4. Check the build output for warnings.

(The original report does not include the project's contents or configuration, so no minimal reproducing project is available.)

## Observed behavior
With Sphinx 3.3, the `singlehtml` and `latex` builds print this warning:

```
WARNING: no number is assigned for table:
```

The warning did not appear before the upgrade to 3.3.

## Expected behavior
After upgrading to Sphinx 3.3, the same documentation should build without the new `no number is assigned for table` warnings, as it did with the previous version.

## Stack trace / error output
```
WARNING: no number is assigned for table:
```
No stack trace was provided. The original report does not say which source location or table the warning refers to.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- Sphinx: 3.3 (warning first appeared after upgrading to this version; the previous version is not stated)
- Affected builders: `singlehtml`, `latex`
- Python version, OS, extensions and configuration: Not provided in the original report.