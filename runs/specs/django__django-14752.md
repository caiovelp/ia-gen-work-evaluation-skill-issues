# Spec: Extension point for result serialization in `AutocompleteJsonView`

## Assumptions

1. **Project.** This is Django, and the target class is `django.contrib.admin.views.autocomplete.AutocompleteJsonView`. The file path `django/contrib/admin/views/autocomplete.py` comes from the dotted module name in the issue and has not been checked against the repository.
2. **Current behaviour of `get()`.** The issue quotes it as:
   - call `process_request(request)`, which returns `term`, `model_admin`, `source_field` and `to_field_name`
   - check `has_perm(request)`, raising `PermissionDenied` on failure
   - call `get_queryset()`, then `get_context_data()`
   - return a `JsonResponse` with `results` and `pagination`

   This may differ slightly in the actual target branch.
3. **Each result today** is `{'id': str(getattr(obj, to_field_name)), 'text': str(obj)}`.
4. **New method name and signature:** `serialize_result(self, obj, to_field_name)`, as proposed in the issue.
5. **Compatibility.** This is a purely additive change. The JSON response format, permission checks, pagination and query behaviour must not change.
6. **Bug in the issue's example.** The example override uses `super.serialize_result(...)`. That is a typo for `super().serialize_result(...)`.
7. **Dict merge operator.** The example uses `dict | dict`, which needs Python ≥ 3.9. That only constrains user code or docs examples, not the core implementation.
8. **Documentation.** The new method is intended as a public, documented extension point. It is not a private helper.

## Objective

Let developers add extra fields to each item in the admin autocomplete JSON response (for example `{'notes': obj.notes}`) by overriding one small method. Today they must copy and override the whole `AutocompleteJsonView.get()`.

**Users:** developers who customize the Django admin and need related-model data on autocomplete items. This is the autocomplete counterpart of adding data attributes to `Select`-based widget options.

**Why:** a copied `get()` falls out of sync as Django changes upstream, which creates ongoing maintenance work.

**User story:** As an admin developer, I can subclass `AutocompleteJsonView` and override only `serialize_result(obj, to_field_name)`. Each result then includes my extra keys, and I still inherit all of the upstream request processing, permission checks and pagination.

## Tech Stack

- Python and Django. The target Django version or branch is unknown.
- The view is a Django class-based view that returns `django.http.JsonResponse`.

## Commands

All of these are unknown, because no repository access was available.

- Build: unknown (not applicable for this change)
- Test: unknown. Use the project's standard test runner for the admin views and autocomplete test modules.
- Lint: unknown
- Docs build: unknown

## Project Structure

| Item | Location |
|---|---|
| Source | `django/contrib/admin/views/autocomplete.py` (inferred from module path, unverified) |
| Tests | unknown; presumably the existing admin autocomplete view tests |
| Docs | unknown; presumably the admin reference docs that cover `ModelAdmin.autocomplete_fields`, `AutocompleteJsonView`, and the release notes |

## Code Style

Follow the existing code style of the file being modified (unknown).

The interface proposed in the issue, for illustration only:

```python
# In get():
'results': [
    self.serialize_result(obj, to_field_name) for obj in context['object_list']
],

def serialize_result(self, obj, to_field_name):
    return {'id': str(getattr(obj, to_field_name)), 'text': str(obj)}
```

## Testing Strategy

- **Framework:** the project's existing test framework (unknown specifics). Place new tests alongside the existing autocomplete view tests.
- **Regression:** the existing autocomplete tests must pass unchanged. This shows the default output is byte-for-byte identical in structure and values.
- **New unit or integration test:** subclass `AutocompleteJsonView` and override `serialize_result` to add an extra key. Then request the view and assert that:
  - each result contains `id`, `text` and the extra key, with correct values
  - `pagination.more` is still correct
- **Direct test of the default method:** for a given object and `to_field_name`, the default `serialize_result` returns exactly `{'id': str(getattr(obj, to_field_name)), 'text': str(obj)}`.
- **No coverage gaps:** permission denial and bad-request paths keep their existing tests and behaviour.

## Boundaries

**Always:**
- Keep the response shape `{'results': [...], 'pagination': {'more': bool}}` unchanged.
- Call `serialize_result` once per object in `context['object_list']`.
- Add tests and documentation for the new method.

**Ask first:**
- Changing the method name or signature, for example passing `request` or other context.
- Also exposing a hook for the top-level response or pagination.
- Backporting to any stable branch.

**Never:**
- Change permission checks, `process_request` semantics, queryset or pagination logic, or the default `id`/`text` values.
- Remove or alter existing tests to make them pass.

## Success Criteria

1. `AutocompleteJsonView` has a method `serialize_result(self, obj, to_field_name)` that returns `{'id': str(getattr(obj, to_field_name)), 'text': str(obj)}` by default.
2. `get()` builds every entry in `results` by calling `self.serialize_result(obj, to_field_name)`. No other behaviour of `get()` changes.
3. A subclass that overrides only `serialize_result`, for example to return `super().serialize_result(obj, to_field_name) | {'notes': obj.notes}`, gets the extra key in every result. It needs no other overrides.
4. All existing autocomplete and admin tests pass without modification.
5. New tests cover both the default serialization and an overridden serialization.
6. The method is documented, including an override example that uses `super()` correctly, and a release note entry is added. Exact doc locations are unknown.

## Open Questions

1. Should `serialize_result` be a documented public API, or an undocumented hook? This affects whether docs and release notes are required.
2. Is `(obj, to_field_name)` the right signature, or should the hook also receive the request or other context for per-request customization?
3. Which Django version or branch should this target? This decides the release-notes location, and whether a docs example may use the `|` dict operator, given the minimum supported Python version.
4. Where exactly do the autocomplete view tests and admin docs live in the repository?
5. Has `get()` diverged in the current branch from the version quoted in the issue?