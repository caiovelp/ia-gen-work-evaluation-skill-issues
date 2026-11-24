# Spec: URLField raises ValidationError (not ValueError) for malformed IPv6-like URLs

## Assumptions

1. The issue is in Django. The traceback paths `django/forms/fields.py` and `django/core/validators.py` support this.
2. The `ValueError` comes from Python's `urllib.parse.urlsplit`. That function raises `ValueError("Invalid IPv6 URL")` when the netloc has unbalanced `[` / `]` brackets. The call happens inside the URL validator invoked at `django/core/validators.py` line 130 (`__call__`), which is presumably `URLValidator`.
3. `URLValidator` is the validator `forms.URLField` uses by default. It reaches `urlsplit` during its own validation logic, not through `URLField.to_python`. The traceback goes through `run_validators`, not `to_python`.
4. The expected contract is Django's general rule: `Field.clean()` reports invalid user input only by raising `django.core.exceptions.ValidationError`, never other exception types.
5. The error to raise is the validator's existing "invalid" message and code. No new message or code is introduced.
6. The fuzzer harness (`basic_fuzzer.py`, `fuzzers.py`) is external and is not part of this change.
7. The Django version and the line numbers in the traceback are unknown. They may not match the current main branch.
8. Other `urlsplit` / `urlparse` call sites may have the same problem. One example is `URLField.to_python`, which may already handle `ValueError`; this is not verified. These sites are in scope only if they are reachable from `forms.URLField.clean()`.

## Objective

Calling `forms.URLField().clean('////]@N.AN')` currently raises an uncaught `ValueError: Invalid IPv6 URL`. That breaks the forms contract and causes a 500 error in any view that validates user-submitted URLs. The call must instead raise a `ValidationError` carrying the field's/validator's standard "invalid URL" error.

**Users affected:**
- Django developers using `forms.URLField`, or `URLValidator` directly.
- Their end users, who can trigger this with arbitrary input.

**Acceptance criteria:**
- `forms.URLField().clean('////]@N.AN')` raises `ValidationError`, not `ValueError`.
- The raised error uses the existing "invalid" error code and message ("Enter a valid URL." or whatever the current message is). No new message or code is added.
- Calling the URL validator directly on the same input also raises `ValidationError`. This applies if the validator is confirmed to be the source.
- Valid URLs, including valid bracketed IPv6 URLs such as `http://[::1]/`, still validate unchanged.
- Existing invalid-URL tests still pass with the same error codes.

## Tech Stack

- Python, version unknown. `urllib.parse` behavior around bracket validation has changed across Python versions.
- Django, version and branch unknown.
- No new dependencies.

## Commands

- Build: unknown. No build step is visible in the issue.
- Test: unknown. Django's test runner invocation is not shown in the issue.
- Lint: unknown.
- Reproduction (from the issue, as a Python snippet):
  ```python
  from django import forms
  forms.URLField().clean('////]@N.AN')
  ```
  Settings configuration may be required to run this outside a project. The exact setup is unknown.

## Project Structure

Files known from the traceback:

```
django/forms/fields.py      → Field.clean (line ~151), Field.run_validators (line ~136)
django/core/validators.py   → validator __call__ (line ~130) that calls urllib.parse.urlsplit
```

Test file locations are unknown. They are likely the existing tests for form fields and validators, but the paths are not visible.

## Code Style

No repository code is visible. Follow the existing conventions in `django/core/validators.py`:
- Raise `ValidationError(self.message, code=self.code, ...)` consistently with surrounding validator code. The exact parameters are unknown and should be copied from neighboring raises in the same method.
- The fix should be minimal and local. Do not refactor unrelated validation logic.

## Testing Strategy

- Framework: Django's own test suite. Runner and file paths are unknown.
- Add regression tests:
  - Form-field level: `URLField().clean('////]@N.AN')` raises `ValidationError` with the "invalid" code.
  - Validator level: the URL validator raises `ValidationError` for the same input. Add this only if it is confirmed that the validator raises the `ValueError`.
  - Optionally add closely related inputs that trigger the same `urlsplit` error, such as unbalanced `[` or `]` in the netloc. These should be confirmed against `urlsplit` behavior on the supported Python versions.
- Negative and regression checks: valid IPv6 URLs and existing valid and invalid URL cases keep their current outcomes.
- Coverage expectation: every reachable `urlsplit`/`urlparse` call in the `URLField.clean()` path is covered by a case that makes it raise `ValueError`.

## Boundaries

- **Always:**
  - Convert `ValueError` from URL parsing into `ValidationError` using the existing message and code.
  - Add regression tests.
  - Keep behavior for valid URLs unchanged.
- **Ask first:**
  - Changing error messages or codes.
  - Changing which URLs are accepted beyond turning crashes into validation errors.
  - Modifying `URLField.to_python` or model `URLField`, if they are not on the failing path.
  - Backporting to release branches.
- **Never:**
  - Catch broad `Exception`.
  - Swallow the error and accept the input as valid.
  - Change the fuzzer harness.
  - Alter `urllib` behavior or monkeypatch the standard library.

## Success Criteria

1. The reproduction snippet raises `django.core.exceptions.ValidationError` with code `"invalid"`.
2. No `ValueError` escapes `forms.URLField().clean()` for inputs where `urlsplit` raises `ValueError`.
3. The new regression tests pass. All existing form-field and validator tests pass unchanged.
4. Valid URLs, including bracketed IPv6 hosts, validate exactly as before.

## Open Questions

1. Which Django version or branch should be fixed? Should the fix be backported? Line numbers in the traceback may be outdated.
2. Is the raising `__call__` at `validators.py:130` definitely `URLValidator.__call__`? Which `urlsplit` call in it fails: the one before or after the scheme/regex checks?
3. Should the fix also cover other `urlsplit`/`urlparse` call sites that can raise `ValueError`, such as `URLField.to_python`, `EmailValidator`, or model `URLField`? Or should it stay strictly on the reported path?
4. Which Python versions must be supported? `urlsplit`'s bracket validation has changed across versions, so the set of inputs that raise `ValueError` may differ.
5. Should the `ValidationError` include `params={'value': value}` like other raises in the validator? This depends on the current code's convention.
6. What are the exact test command and test file locations to use?