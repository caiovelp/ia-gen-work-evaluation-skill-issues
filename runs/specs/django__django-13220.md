# Spec: Equality Comparison for `django.core.exceptions.ValidationError`

## Objective

Two `ValidationError` instances built from the same inputs currently compare unequal, because they fall back to identity comparison. This is counter-intuitive and makes tests harder to write. For example, `assertEqual(raised_error, expected_error)` fails even when the errors are semantically identical.

We will add value-based equality (`__eq__`) to `ValidationError` so that identically created instances compare equal. The comparison must not depend on the order of errors:

- within a single field's error list,
- within `non_field_errors`, or
- within a flat list of errors.

**Users:** Django developers writing tests, and developers comparing validation outcomes in application code (form validation, model `clean()` and `full_clean()`, custom validators).

**User stories / acceptance criteria:**
- As a developer, when I build two `ValidationError`s with the same message, code and params, they compare equal.
- As a developer, when I build two list-form `ValidationError`s holding the same errors in a different order, they compare equal.
- As a developer, when I build two dict-form `ValidationError`s with the same fields, and each field holds the same errors in a different order, they compare equal. This includes `NON_FIELD_ERRORS`.
- As a developer, when two `ValidationError`s differ in message content, they compare unequal. They also compare unequal when they differ in field keys, or when one is dict-form and the other is list-form.
- As a developer, comparing a `ValidationError` with an object of another type does not raise, and does not report equality.

## Assumptions

1. The target class is `django.core.exceptions.ValidationError`. It is defined in the `django/core/exceptions.py` module, which I infer from the dotted path in the issue; I have not seen the file.
2. `ValidationError` has three internal shapes, based on general knowledge of Django that I have not verified against this repository:
   - **single:** has `message`, `code` and `params` attributes.
   - **list:** has `error_list`.
   - **dict:** has `error_dict`, which maps field name to a list of errors.
3. "Created identically" means equivalent constructor inputs. A simple comparison of rendered `messages` strings is explicitly called "not enough" by the issue author. So the comparison should consider at least `message`, `code` and `params`, not only the interpolated text. This needs confirmation; see Open Questions.
4. Order independence applies to errors within a list, whether that is a flat `error_list` or a per-field list in `error_dict`. Dict key order is already irrelevant for dict equality.
5. When the other operand is not a `ValidationError`, `__eq__` returns `NotImplemented` rather than `False`, which follows normal Python protocol.
6. In Python 3, defining `__eq__` without `__hash__` makes instances unhashable. Exceptions are currently hashable, and code may put them in sets or dicts. So a consistent `__hash__` must also be defined to avoid a backward-incompatible change.
7. This is a feature addition to Django, not a bug fix. It needs release notes and possibly documentation in the exceptions reference docs.
8. Lazy translation strings (`gettext_lazy`) may be used as messages. Comparison must work for them without crashing, though it may force evaluation.
9. Duplicate errors are significant. `[e1, e1]` and `[e1]` should compare unequal, which means multiset semantics rather than set semantics. This needs confirmation.

## Tech Stack

- Python, within the Django framework codebase. The supported Python and Django versions are **unknown** because they are not stated in the issue.
- No new dependencies.

## Commands

The exact commands are **unknown**, because the repository is not visible. Django's test suite is typically run through the test runner in its `tests/` directory, but the exact invocation, settings and lint tooling must be confirmed from the repository.

```
Build: unknown (no build step expected for a pure-Python change)
Test:  unknown — run the test module(s) covering django.core.exceptions / ValidationError
Lint:  unknown — use the project's configured linters (e.g. flake8/isort if configured)
```

## Project Structure

Only what can be inferred from the issue:

```
django/core/exceptions.py   → ValidationError definition (inferred from dotted path)
tests/…                     → Location of existing ValidationError tests: unknown
docs/…                      → Release notes / exceptions reference: exact paths unknown
```

## Code Style

The existing conventions are **unknown**. Follow the project's existing style in the module being changed: PEP 8, and the surrounding naming and docstring conventions. No style example is reproduced here because no source code is visible.

Key conventions to respect:
- Return `NotImplemented` for unsupported operand types.
- Keep `__eq__` and `__hash__` consistent: equal objects must have equal hashes.

## Testing Strategy

- **Framework:** Django's own test suite, which uses `unittest` and `django.test`. The exact module location is unknown.
- **Level:** Unit tests on `ValidationError` directly. No integration or end-to-end tests are needed.
- **Cases to cover:**
  - **Single-message errors:**
    - The same message compares equal.
    - Different messages compare unequal.
    - The same message with a different `code` compares unequal, if Open Question 1 is resolved that way.
    - The same message with different `params` compares unequal.
    - The same rendered text produced by different `params` follows the decided semantics.
  - **List-form errors:**
    - The same errors in the same order compare equal.
    - The same errors in a different order compare equal.
    - Different contents compare unequal.
    - Different multiplicity compares unequal, per Assumption 9.
  - **Dict-form errors:**
    - The same fields with errors in a different order within each field compare equal.
    - Different field keys compare unequal.
    - The same messages under different fields compare unequal.
    - `NON_FIELD_ERRORS` ordering is handled the same way as other fields.
  - **Cross-shape comparisons** (single vs list, list vs dict): behaviour as decided in Open Question 3.
  - **Nested construction:** a `ValidationError` built from a list of `ValidationError`s equals one built from equivalent plain messages, if they normalize to the same internal form.
  - **Other types:** comparing with a non-`ValidationError` such as a string, `None` or another exception returns unequal and does not raise.
  - **Inequality operator:** `!=` behaves as the negation of `==`.
  - **Hashing:**
    - Instances remain hashable.
    - Equal instances produce equal hashes, including for differently ordered lists and dicts.
  - **Lazy strings:** errors built with lazy translation strings compare without error.
- **Coverage:** every branch of the new `__eq__` and `__hash__` is exercised.

## Boundaries

- **Always:**
  - Keep the comparison order-independent within error lists.
  - Keep `__hash__` consistent with `__eq__`.
  - Add tests for every acceptance criterion.
  - Add a release note entry.
- **Ask first:**
  - Changing the existing constructor or attribute structure of `ValidationError`.
  - Changing `messages`, `message_dict` or `__repr__` behaviour.
  - Changing the equality semantics of subclasses or related exceptions.
- **Never:**
  - Make `ValidationError` unhashable.
  - Raise from `__eq__` for foreign types.
  - Modify unrelated exception classes.
  - Remove or weaken existing tests.

## Success Criteria

1. `ValidationError('msg') == ValidationError('msg')` is `True`.
2. `ValidationError('msg', code='a') == ValidationError('msg', code='b')` follows the decided semantics, expected to be `False`.
3. `ValidationError('%(v)s', params={'v': 1}) == ValidationError('%(v)s', params={'v': 2})` is `False`.
4. `ValidationError(['a', 'b']) == ValidationError(['b', 'a'])` is `True`.
5. `ValidationError({'f': ['a', 'b']}) == ValidationError({'f': ['b', 'a']})` is `True`. The same holds for `NON_FIELD_ERRORS`.
6. `ValidationError({'f1': ['a']}) == ValidationError({'f2': ['a']})` is `False`.
7. `ValidationError('msg') == 'msg'` is `False` and does not raise.
8. `hash()` succeeds on all shapes of `ValidationError`. Instances that compare equal have equal hashes.
9. All existing tests in the suite continue to pass.
10. A release note documents the new behaviour.

## Open Questions

1. **What does "created identically" compare?** Should equality compare raw `message`, `code` and `params`, or only rendered message text? Example: are `ValidationError('x', code='a')` and `ValidationError('x', code='b')` equal? The assumed answer is that all three are compared.
2. **Rendered vs. raw message:** should `ValidationError('%(v)s', params={'v': 'x'})` equal `ValidationError('x')`? They produce identical `messages` but were not created identically.
3. **Cross-shape equality:** should a single-message error equal a list-form error containing that one message? For example, `ValidationError('a') == ValidationError(['a'])`.
4. **Duplicates:** should duplicate errors affect equality? This is the choice between multiset and set semantics.
5. **Unhashable or unorderable params:** how should order-independent comparison and hashing handle `params` containing values that are unhashable or unorderable, such as dicts or lists? Is a best-effort normalization acceptable?
6. **Subclasses:** should equality consider exact type, so that a `ValidationError` subclass instance never equals a base instance with the same content?
7. **Target version:** which Django version should this land in, and which docs pages need updating beyond the release notes?
8. **Test location:** where do existing `ValidationError` tests live, and what are the exact commands to run them? Both are unknown without repository access.