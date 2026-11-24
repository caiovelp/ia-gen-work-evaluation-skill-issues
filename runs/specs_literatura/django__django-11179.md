## Summary

Calling `delete()` on an instance of a model that has no dependencies does not clear the instance's primary key. After `.delete()` the PK should be set to `None`, but it keeps its previous value.

## Steps to reproduce

1. Use a Django model that has no dependencies (no other models relate to it).
2. Create and save an instance of that model.
3. Call `.delete()` on the instance.
4. Inspect the instance's primary key.

## Observed behavior

The instance's primary key is not updated after `.delete()`. It still holds the value it had before deletion.

## Expected behavior

After `.delete()`, the instance's primary key should be set to `None`.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Not provided in the original report. The reporter points to the relevant code location: `django/db/models/deletion.py`, lines 276–281 (line 280 in particular).

## Version and environment

Not provided in the original report.