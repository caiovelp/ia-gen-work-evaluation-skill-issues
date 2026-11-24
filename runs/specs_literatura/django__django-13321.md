## Summary

After upgrading a staging server to Django 3.1, every request from a browser that still holds an old, apparently invalid session crashes with an unhandled exception during session decoding. Signature verification fails with `BadSignature`. Django then falls back to the legacy decoder, which raises `binascii.Error: Incorrect padding`. The reporter cannot log in with Chrome at all, while Firefox works. The reporter notes the issue looks similar to another existing issue, but the link was not preserved.

## Steps to reproduce

1. Run a site on a Django version earlier than 3.1 and have an active session in a browser (here, Chrome). The exact previous version is not stated.
2. Upgrade the server to Django 3.1. In the reporter's setup, this is a staging server running Gunicorn behind an nginx proxy.
3. In the same browser, which still holds the old session, browse to any URL, e.g. `/overview/`.
4. Try to log in.

## Observed behavior

- Every request from Chrome, on any URL, fails with "Internal Server Error" (e.g. `Internal Server Error: /overview/`).
- Logging in with Chrome is impossible because every attempt to access the site crashes.
- Logging in with Firefox works fine.
- The problem occurs only on the staging site.
- The crash is triggered when `request.user` is evaluated (via `request.user.is_authenticated` in `django/contrib/auth/mixins.py` and `django_otp/middleware.py`). This reads `request.session[SESSION_KEY]` and loads the session from the database backend (`db.py`). `decode()` then raises `BadSignature`, and the fallback `_legacy_decode()` raises `binascii.Error: Incorrect padding`. That exception propagates uncaught.

## Expected behavior

Invalid or undecodable session data should not crash the request. The user should still be able to access the site and log in.

## Stack trace / error output

```
Internal Server Error: /overview/
Traceback (most recent call last):
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 215, in _get_session
return self._session_cache
AttributeError: 'SessionStore' object has no attribute '_session_cache'
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 118, in decode
return signing.loads(session_data, salt=self.key_salt, serializer=self.serializer)
File "/usr/local/lib/python3.8/site-packages/django/core/signing.py", line 135, in loads
base64d = TimestampSigner(key, salt=salt).unsign(s, max_age=max_age).encode()
File "/usr/local/lib/python3.8/site-packages/django/core/signing.py", line 201, in unsign
result = super().unsign(value)
File "/usr/local/lib/python3.8/site-packages/django/core/signing.py", line 184, in unsign
raise BadSignature('Signature "%s" does not match' % sig)
django.core.signing.BadSignature: Signature "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" does not match
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
File "/usr/local/lib/python3.8/site-packages/django/core/handlers/exception.py", line 47, in inner
response = get_response(request)
File "/usr/local/lib/python3.8/site-packages/django/core/handlers/base.py", line 179, in _get_response
response = wrapped_callback(request, *callback_args, **callback_kwargs)
File "/usr/local/lib/python3.8/site-packages/django/views/generic/base.py", line 73, in view
return self.dispatch(request, *args, **kwargs)
File "/usr/local/lib/python3.8/site-packages/django/contrib/auth/mixins.py", line 50, in dispatch
if not request.user.is_authenticated:
File "/usr/local/lib/python3.8/site-packages/django/utils/functional.py", line 240, in inner
self._setup()
File "/usr/local/lib/python3.8/site-packages/django/utils/functional.py", line 376, in _setup
self._wrapped = self._setupfunc()
File "/usr/local/lib/python3.8/site-packages/django_otp/middleware.py", line 38, in _verify_user
user.otp_device = None
File "/usr/local/lib/python3.8/site-packages/django/utils/functional.py", line 270, in __setattr__
self._setup()
File "/usr/local/lib/python3.8/site-packages/django/utils/functional.py", line 376, in _setup
self._wrapped = self._setupfunc()
File "/usr/local/lib/python3.8/site-packages/django/contrib/auth/middleware.py", line 23, in <lambda>
request.user = SimpleLazyObject(lambda: get_user(request))
File "/usr/local/lib/python3.8/site-packages/django/contrib/auth/middleware.py", line 11, in get_user
request._cached_user = auth.get_user(request)
File "/usr/local/lib/python3.8/site-packages/django/contrib/auth/__init__.py", line 174, in get_user
user_id = _get_user_session_key(request)
File "/usr/local/lib/python3.8/site-packages/django/contrib/auth/__init__.py", line 58, in _get_user_session_key
return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 65, in __getitem__
return self._session[key]
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 220, in _get_session
self._session_cache = self.load()
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/db.py", line 44, in load
return self.decode(s.session_data) if s else {}
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 122, in decode
return self._legacy_decode(session_data)
File "/usr/local/lib/python3.8/site-packages/django/contrib/sessions/backends/base.py", line 126, in _legacy_decode
encoded_data = base64.b64decode(session_data.encode('ascii'))
File "/usr/local/lib/python3.8/base64.py", line 87, in b64decode
return binascii.a2b_base64(s)
binascii.Error: Incorrect padding
```

## Test case

Not provided in the original report.

## Code example

Not provided in the original report.

## Version and environment

- Django: 3.1, upgraded from an earlier, unspecified version
- Python: 3.8, according to the paths in the traceback (`/usr/local/lib/python3.8/...`)
- Session backend: database (`django/contrib/sessions/backends/db.py`, according to the traceback)
- Third-party packages: `django_otp` (its middleware appears in the traceback)
- Server: staging site running Gunicorn behind an nginx proxy
- Browsers: Chrome fails (holds an old session), Firefox works
- OS: Not provided in the original report