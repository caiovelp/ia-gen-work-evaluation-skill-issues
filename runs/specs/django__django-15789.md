# Spec: Add an `encoder` parameter to `django.utils.html.json_script()`

## Assumptions

1. The target is the Django codebase. The function in question is `django.utils.html.json_script()`, and its template filter counterpart is the documented `json_script` filter (likely in `django/template/defaultfilters.py`, but that location is **unverified**).
2. Today `json_script()` serializes with `json.dumps(value, cls=DjangoJSONEncoder)`. It then escapes HTML-sensitive characters (`<`, `>`, `&`) and wraps the result in `<script type="application/json">`. The issue confirms only the hardcoded `DjangoJSONEncoder`. The escaping details are assumed from general knowledge of Django.
3. The new parameter is a keyword argument named `encoder`. It defaults to `None`, and `None` means "use `DjangoJSONEncoder`". This keeps every existing call working unchanged.
4. `encoder` takes a **class** (a `json.JSONEncoder` subclass), not an instance. This matches the `cls=` convention of `json.dumps` and the `encoder` parameter on `JSONField` and `JsonResponse`.
5. HTML escaping of the output must still apply no matter which encoder is used. A custom encoder must never be able to turn off XSS protection.
6. This change does not alter the template filter's signature. Template filters accept at most one argument, and that slot may already be used by `element_id` (see Open Questions).
7. Both parts of the issue are in scope: (a) the `encoder` parameter and (b) documenting `django.utils.html.json_script()` in the utilities reference docs.
8. This is a new feature. It needs a release note in the next feature release's notes and a `versionchanged`/`versionadded` annotation in the docs.

## Objective

Let Python callers of `django.utils.html.json_script()` choose the JSON encoder class used to serialize the value. Today the encoder is hardcoded to `DjangoJSONEncoder`. Also document `django.utils.html.json_script()` publicly; today only the template filter is documented.

**Users:** developers who build template context or HTML fragments in Python. They need custom serialization, for example for domain objects, special number formats, or types that `DjangoJSONEncoder` does not handle.

**User stories:**
- As a developer, I can call `json_script(value, encoder=MyEncoder)` and the JSON in the output reflects `MyEncoder`'s serialization.
- As a developer who doesn't pass `encoder`, I get exactly the same output as before.
- As a developer reading the docs, I can find `json_script()` in the `django.utils.html` reference. The entry covers its parameters, including `encoder`, and its escaping guarantees.

**Acceptance criteria:**
- `json_script()` accepts an optional `encoder` argument.
- When `encoder` is omitted or `None`, `DjangoJSONEncoder` is used. Output is byte-for-byte identical to the current behavior.
- When `encoder` is given, it is passed as the encoder class to JSON serialization.
- The output is HTML-escaped the same way with any encoder.
- The existing `element_id` behavior is unchanged.
- The `json_script` template filter still behaves as before.
- Docs describe `django.utils.html.json_script()`, including the `encoder` parameter, and cross-reference the template filter.
- A release note announces the new parameter.

## Tech Stack

- Python and the standard library `json` module (`json.dumps(..., cls=...)`)
- Django: `django.utils.html`, `django.core.serializers.json.DjangoJSONEncoder`
- Docs: Sphinx/reStructuredText (assumed from Django's conventions; paths **unknown**)
- Supported Python and Django versions: **unknown**

## Commands

Not stated in the issue, so all are **unknown**:

```
Build: unknown
Test: unknown (Django's test runner invocation, e.g. for the utils_tests / template filter test suites, not verified)
Lint: unknown
Docs build: unknown
```

## Project Structure

Only the module paths named in the issue are known:

```
django/utils/html.py          → json_script() lives here (module path stated in issue)
<unknown>                     → json_script template filter implementation
<unknown>                     → DjangoJSONEncoder (import path django.core.serializers.json assumed)
<unknown tests dir>           → tests for django.utils.html
<unknown tests dir>           → tests for the json_script template filter
<unknown docs path>           → django.utils reference docs (where json_script() docs should be added)
<unknown docs path>           → built-in template filter docs (json_script filter, already documented)
<unknown docs path>           → release notes for the next feature release
```

## Code Style

The codebase is not visible, so this section does not reproduce existing code. Intended public usage, for illustration only:

```python
from django.utils.html import json_script

json_script({"a": value}, "my-id", encoder=MyCustomEncoder)
```

Conventions to follow (assumed from Django's practices, **not verified**):
- Keep the parameter optional with a `None` default, consistent with `encoder` parameters elsewhere in Django.
- Follow the project's existing formatting and lint configuration (tooling **unknown**).
- Docs use the project's existing reST function directives and version-change annotations.

## Testing Strategy

- **Framework:** Django's own test suite, which is `unittest`-based (runner command **unknown**).
- **Unit tests for `django.utils.html.json_script()`:**
  - A custom encoder subclass changes the serialized output. For example, an encoder that serializes some type in a recognizable way, and the output contains that representation.
  - With a custom encoder, `<`, `>`, and `&` in the encoded data are still escaped in the output.
  - Calls without `encoder`, and with `encoder=None`, produce output identical to the existing expected outputs.
  - `encoder` works together with an `element_id` and without one.
- **Regression:** existing `json_script` tests for both the utility and the template filter still pass unchanged.
- **Docs:** the docs build succeeds with the new entry (command **unknown**).
- Coverage threshold: **unknown**.

## Boundaries

- **Always:**
  - Keep the parameter backward compatible (optional, default preserves `DjangoJSONEncoder`).
  - Keep HTML escaping regardless of encoder.
  - Add tests for the new parameter.
  - Add docs and a release note.
- **Ask first:**
  - Changing the template filter's signature or behavior.
  - Accepting encoder instances or callables in addition to classes.
  - Adding further passthrough options, such as arbitrary `json.dumps` kwargs.
  - Changing the parameter's position or name.
  - Backporting to stable branches.
- **Never:**
  - Change the default encoder.
  - Weaken or bypass output escaping.
  - Change the `<script>` element structure or the `element_id` semantics.
  - Remove or alter existing tests to make new behavior pass.

## Success Criteria

1. `json_script(value)` and `json_script(value, element_id)` return the same strings as before the change.
2. `json_script(value, encoder=CustomEncoder)` serializes `value` using `CustomEncoder`. A test shows that output differs from the default where the encoders differ.
3. With any encoder, the returned markup contains no unescaped `<`, `>`, or `&` from the JSON payload.
4. The `json_script` template filter's existing tests pass without modification.
5. `django.utils.html.json_script()` appears in the reference docs. The entry documents `value`, `element_id`, and `encoder`, the default encoder, and the escaping behavior, and links to the template filter.
6. A release note for the next feature release mentions the new `encoder` parameter.
7. The full relevant test suites and the docs build pass (commands **unknown**).

## Open Questions

1. **Parameter signature:** should `encoder` be keyword-only, or a third positional parameter after `element_id`? Is `element_id` currently optional in the targeted version? This affects ordering and the docs.
2. **Class vs. instance:** confirm `encoder` takes a `JSONEncoder` subclass, as `json.dumps(cls=...)` does, and not an instance or a plain `default` callable.
3. **Template filter exposure:** should the `json_script` filter gain any way to choose an encoder? Filters take one argument, so the assumption is no. Confirm this is out of scope.
4. **Documenting the utility:** the issue asks whether `django.utils.html.json_script()` should be documented. The assumption is yes. Confirm where it belongs (the `django.utils.html` section of the utilities reference) and whether to document only `json_script()` or audit other undocumented `django.utils.html` helpers too (assumed: only `json_script()`).
5. **Version targeting:** which Django release receives this feature, and therefore which release notes file and `versionchanged` version to use?
6. **Escaping contract:** should the docs explicitly warn that a custom encoder's output is still escaped, and that the encoder must produce valid JSON?
7. **Test, lint, and docs commands, and exact file paths:** these are unknown and need confirmation against the repository.