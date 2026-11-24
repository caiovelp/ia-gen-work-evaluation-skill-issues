## Summary
After upgrading from Django 2.2 to 3.0, passing a named 2-tuple as the argument to a `__range` queryset filter raises a `TypeError`. The same code works on 2.2.

According to the reporter, `django.db.models.sql.query.Query.resolve_lookup_value` resolves lookups in each tuple element and then rebuilds the tuple. It keeps the original type (the named tuple) but passes an iterator to its constructor. Named tuples cannot be built from a single iterator argument, so construction fails with missing arguments.

## Steps to reproduce
1. Use Django 3.0.
2. Define a named tuple with two fields.
3. Pass an instance of it as the value of a `__range` lookup in a queryset filter.
4. Evaluate the queryset.
5. Run the same code on Django 2.2 for comparison.

## Observed behavior
On Django 3.0 the filter raises:
`TypeError: __new__() missing 1 required positional argument: 'far'`

The named tuple is rebuilt from an iterator instead of from its individual elements, so the constructor receives too few positional arguments.

## Expected behavior
A named 2-tuple should be accepted as a `__range` argument, as it was on Django 2.2.

## Stack trace / error output
```
TypeError: __new__() missing 1 required positional argument: 'far'
```
The full stack trace was not provided in the original report.

## Test case
Not provided in the original report.

## Code example
Not provided in the original report.

## Version and environment
- Works on: Django 2.2
- Fails on: Django 3.0
- Python version, database backend and OS: Not provided in the original report.