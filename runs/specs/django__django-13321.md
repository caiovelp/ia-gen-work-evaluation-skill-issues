# Spec: Graceful handling of undecodable session data (legacy-format fallback)

## Objective

**Problem.** After upgrading to Django 3.1, a request whose session cookie points to a stored session with invalid or corrupt `session_data` fails with an unhandled exception and returns HTTP 500. The affected user cannot reach any page, including the login page, until the session is removed by other means.

**Failure path, taken from the traceback:**

1. `request.user` is evaluated, which calls `auth.get_user`, then `_get_user_session_key`, then `request.session[SESSION_KEY]`.
2. `SessionStore._get_session` calls `self.load()`, which in `backends/db.py`, line 44, calls `self.decode(s.session_data)`.
3. `SessionBase.decode` (`backends/base.py`, line 118) calls `signing.loads(...)`, which raises `BadSignature`.
4. `decode` then falls back to `self._legacy_decode(session_data)` (line 122).
5. `_legacy_decode` (line 126) calls `base64.b64decode(session_data.encode('ascii'))`, which raises `binascii.Error: Incorrect padding`. Nothing catches this error.

**Expected behavior.** Session data that cannot be decoded should not crash the request. It should be treated the way Django already treats other invalid or tampered session data: the session loads as empty, and the user appears anonymous and can log in again. This applies whether the data fails in the new signing format, the legacy format, or both.

**Users affected.**
- End users with stale or corrupt sessions after an upgrade.
- Operators of Django sites that use the sessions framework.

The reporter's setup was the DB backend, Gunicorn and nginx, with django-otp installed.

**Acceptance criteria**
- AC1: Calling `SessionBase.decode()` on data that is neither valid signed data nor valid legacy-format data returns `{}` and does not raise.
- AC2: This holds specifically for data that is not valid base64 (for example, incorrect padding), which is the reported case.
- AC3: Valid new-format session data still decodes correctly.
- AC4: Valid legacy-format (pre-3.1) session data still decodes correctly, if legacy decoding is supported in this version.
- AC5: Legacy data with a valid base64 shape but a hash mismatch or a malformed payload keeps its existing behavior: it returns `{}`, with any existing logging of suspicious sessions preserved.
- AC6: A request carrying a cookie for such a session gets a normal response instead of a 500. `request.user` is anonymous.

## Assumptions

1. The fix belongs in Django's sessions framework (`django/contrib/sessions/backends/base.py`). It does not belong in django-otp or in the reporter's deployment.
2. The intended contract of `decode()` is: "invalid data yields an empty session, never an exception." The existing `_legacy_decode` already returns `{}` for some failure modes, such as a hash mismatch, but not for base64 errors raised before those checks.
3. The root cause is independent of the backend. Every backend that calls `decode()` (db, cache, cached_db, file) is affected. The signed-cookie backend may follow a different path.
4. The Chrome/Firefox difference only reflects which browser still held the stale session cookie. It is not a browser bug.
5. The Gunicorn/nginx deployment is not relevant to the fix.
6. Corrupt session rows do not need to be deleted or repaired as part of this change. Returning an empty session is sufficient, and the session is then replaced on the next save or login.
7. The target is the Django 3.1.x line where `decode()` falls back to `_legacy_decode`. Whether a fix is backported is decided by the project.

## Tech Stack

- Python: 3.8 in the reporter's environment. The supported range is unknown.
- Django: 3.1. The exact patch version is unknown.
- Modules involved, taken from the traceback:
  - `django.contrib.sessions.backends.base`
  - `django.contrib.sessions.backends.db`
  - `django.core.signing`
  - `django.contrib.auth`
  - `django.contrib.auth.middleware`
- Third party in the report: `django_otp`. It triggers evaluation of `request.user` but is not the cause.

## Commands

- Build: unknown (not provided in the issue)
- Test: unknown (Django's test runner invocation is not given in the issue)
- Lint: unknown
- Dev: unknown

## Project Structure

Only these paths are known, from the traceback:

```
django/contrib/sessions/backends/base.py → SessionBase: decode(), _legacy_decode(), _get_session()
django/contrib/sessions/backends/db.py   → SessionStore.load() calls decode()
django/core/signing.py                   → loads(), TimestampSigner.unsign() → BadSignature
django/contrib/auth/__init__.py          → get_user(), _get_user_session_key()
django/contrib/auth/middleware.py        → lazy request.user
```

The location of the session tests is unknown.

## Code Style

Follow the existing conventions in `django/contrib/sessions/backends/base.py`. No repository code is available beyond the traceback lines. The relevant existing lines are:

```python
# base.py, decode()
return signing.loads(session_data, salt=self.key_salt, serializer=self.serializer)
...
return self._legacy_decode(session_data)

# base.py, _legacy_decode()
encoded_data = base64.b64decode(session_data.encode('ascii'))
```

Conventions:
- Match surrounding Django style. The specific linter and formatter config is unknown.
- Keep exception handling explicit and narrow enough not to hide programming errors. Whether to catch broadly or list specific exceptions is an open question (Q2).

## Testing Strategy

- **Framework:** Django's own test suite. The exact runner command is unknown.
- **Unit level, on the session base or each backend's test class:**
  - `decode()` on non-base64 or badly padded data returns `{}`. This test must fail before the fix with `binascii.Error`.
  - `decode()` on base64-valid data that is neither signed nor in valid legacy format returns `{}`.
  - The existing tests for valid new-format data, valid legacy data, and tampered legacy data (hash mismatch) still pass.
- **Integration level:**
  - A stored session whose `session_data` is invalid loads as an empty session through `SessionStore.load()`.
  - Accessing a key on it, as in `request.session[SESSION_KEY]`, raises `KeyError`, not `binascii.Error`. As a result, `auth.get_user` returns an anonymous user.
- **Coverage:** every exception path in `decode()` and `_legacy_decode()` that can be reached from untrusted stored data.
- **Out of scope:** browser-level or deployment-level (Gunicorn/nginx) testing.

## Boundaries

- **Always:**
  - Treat stored session data as untrusted input.
  - Preserve backward compatibility for valid legacy sessions.
  - Preserve the existing suspicious-session logging where it currently applies.
  - Add a regression test that reproduces the reported `Incorrect padding` error.
- **Ask first:**
  - Changing which exceptions `decode()` or `_legacy_decode()` swallow beyond the decoding and validation failures.
  - Adding new logging or security warnings for this case.
  - Changing the behavior of the signed-cookie backend.
  - Deleting invalid session rows automatically.
- **Never:**
  - Let malformed session data cause a 500.
  - Silently accept tampered data as valid.
  - Weaken signature or hash verification.
  - Swallow exceptions so broadly that `SECRET_KEY` or configuration errors are hidden.
  - Change the session serialization format as part of this fix.

## Success Criteria

- [ ] AC1–AC6 are satisfied.
- [ ] A regression test that uses session data with invalid base64 padding passes, and it fails without the change.
- [ ] All existing session and auth tests pass.
- [ ] Reproducing the scenario (a stored session row with garbage `session_data` plus a matching cookie, then a request to a login-protected view) yields a redirect to login or an anonymous response, not a 500.

## Open Questions

1. **Which exceptions must `_legacy_decode` tolerate?** Candidates are `binascii.Error`, `UnicodeEncodeError` from `.encode('ascii')` on non-ASCII data, `ValueError` from the hash/data split, and unpickling or deserialization errors. Should the policy be "any exception means an empty session," or should it be an explicit list?
2. **Should the new failure mode be logged?** The existing code may log `SuspiciousSession` for hash mismatches. Should undecodable data also be logged, or be silent?
3. **Do other backends need changes?** Are the signed-cookie and file backends affected through a different code path?
4. **Which branches should get the fix?** Is it 3.1.x only, or also the main branch? When is legacy-decode support planned for removal?
5. **Should a corrupt session be invalidated server-side?** It could be flushed or deleted on detection, rather than only returning `{}` and being overwritten on the next save.
6. **What is the corrupt data's origin?** Is it a pre-3.1 session, a `SECRET_KEY` change, truncation, or something else? This does not block the fix, but it may affect the tests and release notes.
7. **What are the project's build, test and lint commands and test file locations?** These are unknown from the issue.