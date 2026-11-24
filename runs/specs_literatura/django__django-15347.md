## Summary

In the Django messages framework, a message created with `extra_tags=""` comes back with `extra_tags=None` after it is serialized and deserialized. The report says this happens with any of the built-in storage backends. According to the reporter, the cause is that `MessageEncoder` checks whether `extra_tags` is truthy rather than whether it is not `None`.

This affects the standard API, because `messages.debug`, `messages.info`, etc. all default to `extra_tags=""`.

## Steps to reproduce

1. Start a Python shell with Django available.
2. Configure settings so the messages module can be imported:
   ```python
   from django.conf import settings
   settings.configure()
   ```
3. Import `Message`, `MessageEncoder` and `MessageDecoder`:
   ```python
   from django.contrib.messages.storage.base import Message
   from django.contrib.messages.storage.cookie import MessageEncoder, MessageDecoder
   ```
4. Create a message with `extra_tags=""`:
   ```python
   original_message = Message(10, "Here is a message", extra_tags="")
   ```
5. Encode it, then decode it:
   ```python
   encoded_message = MessageEncoder().encode(original_message)
   decoded_message = MessageDecoder().decode(encoded_message)
   ```
6. Compare `extra_tags` on the original and decoded messages.

## Observed behavior

```python
>>> original_message.extra_tags == ""
True
>>> decoded_message.extra_tags is None
True
```

The decoded message has `extra_tags` set to `None` instead of `""`.

In a real application, a message shown after a redirect had been serialized and deserialized, so its `extra_tags` was `None`. A template tag like `{% if x not in message.extra_tags %}` then raised an error.

## Expected behavior

`extra_tags` should survive serialization and deserialization unchanged. A message created with `extra_tags=""` should still have `extra_tags == ""` after decoding.

## Stack trace / error output

Not provided in the original report. The report says the template tag "caused an error" but does not include the error message or traceback.

## Test case

A minimal test case based on the reproduction in the report:

```python
from django.conf import settings
settings.configure()

from django.contrib.messages.storage.base import Message
from django.contrib.messages.storage.cookie import MessageEncoder, MessageDecoder

original_message = Message(10, "Here is a message", extra_tags="")
encoded_message = MessageEncoder().encode(original_message)
decoded_message = MessageDecoder().decode(encoded_message)

assert original_message.extra_tags == ""
assert decoded_message.extra_tags == ""  # Fails: decoded_message.extra_tags is None
```

## Code example

The template code that failed in production (as described by the reporter, "similar to the following"):

```django
{% if x not in message.extra_tags %}
```

When the message was displayed after a redirect, `message.extra_tags` was `None` instead of `""`, and this caused an error.

## Version and environment

Not provided in the original report.