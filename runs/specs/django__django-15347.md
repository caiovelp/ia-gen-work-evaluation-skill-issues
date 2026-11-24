# Spec: Preserve empty-string `extra_tags` across message serialization round-trips

## Assumptions

1. This is a bug in Django's `django.contrib.messages` framework. The modules named in the issue are `django.contrib.messages.storage.base` (`Message`) and `django.contrib.messages.storage.cookie` (`MessageEncoder`, `MessageDecoder`).
2. The root cause is the one the issue states. `MessageEncoder` checks whether `extra_tags` is truthy rather than checking `is not None`, so `""` is dropped during encoding and the decoder rebuilds it as `None`.
3. "Any of the built-in storage backends" means every backend that serializes through `MessageEncoder`/`MessageDecoder`. The cookie backend does so directly. Session storage and fallback storage are assumed to reuse the same encoder/decoder, but this is not verified.
4. `extra_tags=None` must stay distinct from `extra_tags=""`. A message created with `None` should still decode as `None`. Only the `""` case is broken.
5. The fix must stay backward-compatible with cookies/sessions already in flight. Payloads encoded by the old encoder, which omit `extra_tags`, must still decode without error.
6. The public API defaults (`messages.debug`, `messages.info`, `messages.success`, `messages.warning`, `messages.error`, `messages.add_message`) pass `extra_tags=""`. That is why the issue says all standard usage is affected. This has not been verified against source.
7. This is a single capability (one serialization bug), so no capability map is needed.

## Objective

**What:** When a `Message` with `extra_tags=""` is encoded and then decoded by the messages framework, the decoded message must have `extra_tags == ""`, not `None`.

**Why:** Messages that survive a redirect are serialized by the storage backend. After the round-trip, template code that treats `extra_tags` as a string fails. For example, `{% if x not in message.extra_tags %}` raises an error when the value is `None`. Every standard API call defaults `extra_tags` to `""`, so the bug affects nearly all messages that cross a request boundary.

**Who:** Django developers using `django.contrib.messages` whose templates or code operate on `message.extra_tags` as a string.

**Acceptance criteria (user-level):**
- A message added via `messages.info(request, "...")` and shown after a redirect has `extra_tags == ""`.
- Template expressions that treat `extra_tags` as a string, such as `in` / `not in` checks, do not error after a round-trip.

## Tech Stack

- Python / Django, inside the `django.contrib.messages` contrib app.
- Exact Python and Django versions: **unknown** (not stated in the issue).

## Commands

Not visible in the issue; all **unknown**:
- Build: unknown
- Test (full suite / messages tests only): unknown
- Lint: unknown
- Dev: not applicable (library change)

## Project Structure

Known from the issue (module paths only):
- `django/contrib/messages/storage/base.py`: defines `Message`
- `django/contrib/messages/storage/cookie.py`: defines `MessageEncoder`, `MessageDecoder`

Unknown:
- Location of the existing messages tests
- Location of the session/fallback storage modules, and whether they reuse the cookie encoder/decoder
- Where release notes or changelog entries live

## Code Style

- Follow existing Django project conventions. The specific style guide and linter config are **unknown** because they cannot be seen.
- Behavioral convention required by this fix: distinguish "absent" from "empty" with explicit `is not None` checks, not truthiness.

## Testing Strategy

- **Framework:** unknown. Assumed to be the Django project's own test suite, colocated with existing messages tests.
- **Unit level (encoder/decoder):**
  - Round-trip `Message(level, "text", extra_tags="")` and assert `decoded.extra_tags == ""`.
  - Round-trip `Message(level, "text", extra_tags=None)` and assert `decoded.extra_tags is None`.
  - Round-trip `Message(level, "text", extra_tags="tag1 tag2")` and assert the value is preserved.
  - Decode a payload in the old format, without `extra_tags`, and assert it still decodes successfully. The expected value (`None` vs `""`) is listed under Open Questions.
- **Integration level (storage backends):** for each built-in backend that serializes messages (cookie, session, fallback), store a message added with default `extra_tags`, retrieve it on a subsequent request, and assert `extra_tags == ""`.
- **Regression:** all existing messages tests must still pass.
- **Coverage expectations:** unknown. At minimum, every branch of the encoder's `extra_tags` handling must be exercised.

## Boundaries

- **Always:**
  - Keep `None` and `""` as distinct, preserved values through the round-trip.
  - Keep decoding of previously encoded payloads working.
  - Add regression tests reproducing the exact scenario in the issue.
  - Run the messages test suite before committing.
- **Ask first:**
  - Changing the serialized wire format beyond what is needed. Payload size matters for cookie storage, which has a size limit.
  - Normalizing `None` to `""` in `Message` itself, or changing the default value of `extra_tags` anywhere in the public API.
  - Touching storage backends other than the encoder/decoder path.
- **Never:**
  - Break decoding of existing cookies or session data.
  - Change the public signatures of `messages.add_message`, `messages.debug`, `messages.info`, `messages.success`, `messages.warning`, or `messages.error`.
  - Remove or weaken existing tests.

## Success Criteria

1. The reproduction from the issue passes: `MessageDecoder().decode(MessageEncoder().encode(Message(10, "Here is a message", extra_tags=""))).extra_tags == ""`.
2. The same round-trip with `extra_tags=None` yields `None`.
3. The same round-trip with a non-empty `extra_tags` string yields the identical string.
4. Messages added through the standard API and retrieved after a redirect have `extra_tags == ""` for every built-in storage backend that serializes messages.
5. Payloads produced before the fix still decode without raising.
6. All pre-existing messages tests pass.

## Open Questions

1. Do the session and fallback storage backends serialize through `MessageEncoder`/`MessageDecoder`? Are there other serialization paths that check `extra_tags` by truthiness?
2. For legacy payloads that omit `extra_tags`, should the decoded value be `None` (current behavior) or `""`? Old payloads cannot tell `None` and `""` apart.
3. Is any increase in encoded payload size acceptable for the cookie backend? Encoding `""` explicitly adds bytes per message.
4. Should `Message.extra_tags` instead be normalized so it is never `None` (e.g. coerced to `""`)? That would be a broader behavioral change than this bug requires.
5. Which Django versions or branches should receive this fix? Is a release note required?
6. What are the exact commands to run the messages test suite and linters in this repository?