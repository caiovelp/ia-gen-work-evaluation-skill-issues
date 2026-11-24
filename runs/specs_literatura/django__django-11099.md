## Summary
`ASCIIUsernameValidator` and `UnicodeUsernameValidator` in `contrib.auth.validators` accept usernames that end with a trailing newline. Both validators use the regex `r'^[\w.@+-]+$'`, and in Python regexes `$` also matches just before a trailing newline. A username such as `"username\n"` therefore passes validation, although the intent is to allow only alphanumeric characters plus `.`, `@`, `+`, and `-`.

## Steps to reproduce
1. Create an instance of `ASCIIUsernameValidator` or `UnicodeUsernameValidator` from `contrib.auth.validators`.
2. Call the validator with a valid username followed by a newline character, for example `"username\n"`.
3. Check whether a validation error is raised.

## Observed behavior
The username with the trailing newline is accepted. No validation error is raised.

## Expected behavior
The validator should reject any username that contains a newline, including a trailing one. Only alphanumeric characters and `.`, `@`, `+`, `-` should be allowed.

## Stack trace / error output
Not provided in the original report.

## Test case
A minimal test case derived from the report's description (the original report contains no test code):

```python
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator

for validator in (ASCIIUsernameValidator(), UnicodeUsernameValidator()):
    try:
        validator("username\n")
    except ValidationError:
        pass  # expected
    else:
        raise AssertionError(f"{type(validator).__name__} accepted a username with a trailing newline")
```

## Code example
The regex currently used by both validators, as quoted in the report:

```python
r'^[\w.@+-]+$'
```

## Version and environment
Not provided in the original report.