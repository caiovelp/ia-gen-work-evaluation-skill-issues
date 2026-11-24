## Summary
`numberformat.py` raises `IndexError: string index out of range` when it formats a number field whose value is null for display in an admin `list_display`.

## Steps to reproduce
1. Have a model with a number field whose value is null.
2. Include that field in the admin `list_display`.
3. Open the admin change list so the field's value is formatted for display.

## Observed behavior
Formatting fails at this line in `numberformat.py`:
```python
if str_number[0] == "-"
```
It raises `IndexError: string index out of range`.

## Expected behavior
The original report does not state the expected behavior explicitly. It implies that a null number field in the admin `list_display` should be formatted without raising an `IndexError`.

## Stack trace / error output
```
IndexError: string index out of range
```
The full stack trace is not provided in the original report.

## Test case
Not provided in the original report.

## Code example
This line in `numberformat.py` raises the error:
```python
if str_number[0] == "-"
```

## Version and environment
Not provided in the original report.