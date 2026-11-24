# Spec: Recursive cleansing of iterable settings in `SafeExceptionReporterFilter`

## Objective

`django.views.debug.SafeExceptionReporterFilter.get_safe_settings()` can expose sensitive values. Before Django 3.1 the same function was the module-level `django.views.debug.get_safe_settings()`.

The cause is in `cleanse_setting()`. It recurses into `dict` values, but it returns every other iterable (lists, nested lists, and so on) unchanged. Any dicts inside those containers are never inspected, so keys such as `"secret"` or `"token"` keep their real values.

**Who is affected:** Anyone who views the debug/technical error page or any other consumer of `get_safe_settings()`. Settings that hold credentials inside list- or tuple-shaped structures leak those credentials there.

**What we are building:** `cleanse_setting()` will walk into list and tuple values (and possibly other containers, see Open Questions). Dicts found at any nesting depth will have their sensitive keys cleansed with the same rules already used for top-level and nested dicts.

**Reproduction from the issue.** Given this setting:

```python
MY_SETTING = {
    "foo": "value",
    "secret": "value",
    "token": "value",
    "something": [
        {"foo": "value"},
        {"secret": "value"},
        {"token": "value"},
    ],
    "else": [
        [{"foo": "value"}, {"secret": "value"}, {"token": "value"}],
        [{"foo": "value"}, {"secret": "value"}, {"token": "value"}],
    ],
}
```

**Current output** of `SafeExceptionReporterFilter().get_safe_settings()["MY_SETTING"]`. Nested `secret` and `token` are not cleansed:

```
{'else': [[{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
          [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}]],
 'foo': 'value',
 'secret': '********************',
 'something': [{'foo': 'value'}, {'secret': 'value'}, {'token': 'value'}],
 'token': '********************'}
```

**Expected output:**

```
{'else': [[{'foo': 'value'}, {'secret': '********************'}, {'token': '********************'}],
          [{'foo': 'value'}, {'secret': '********************'}, {'token': '********************'}]],
 'foo': 'value',
 'secret': '********************',
 'something': [{'foo': 'value'}, {'secret': '********************'}, {'token': '********************'}],
 'token': '********************'}
```

### User stories

- As a developer viewing a debug error page, I want credentials nested inside lists or tuples in my settings to be masked, so that they are not disclosed on the page or in reports.
- As a maintainer of a custom `SafeExceptionReporterFilter` subclass, I want the recursion to follow the existing cleansing rules (the hidden-settings pattern and the substitute string), so that my overrides still apply.

## Assumptions

1. The fix targets Django 3.1+, where cleansing lives on `SafeExceptionReporterFilter` (`cleanse_setting()` and `get_safe_settings()`). Whether pre-3.1 branches get a backport is an open question.
2. The existing rule for deciding whether a key is sensitive stays unchanged. In the issue this rule matches `secret` and `token`; the exact pattern is not shown and is presumed to be a class attribute such as `hidden_settings`. Only the traversal changes.
3. The existing mask string stays unchanged. The issue shows `'********************'`; it is presumed to be a class attribute such as `cleansed_substitute`.
4. When a key is itself sensitive, its whole value is replaced with the mask whatever the value's type, and there is no recursion into it. This is presumed to be current behaviour and is kept.
5. When a key is not sensitive and its value is a list or tuple, each element is cleansed recursively. Elements have no key of their own, so their sensitivity comes only from dict keys found deeper in the structure.
6. Container types are preserved: a list stays a list and a tuple stays a tuple.
7. Strings and bytes are not treated as iterables to recurse into.
8. The original settings objects are never mutated. Cleansing returns new containers.
9. Values of other types, such as scalars, callables and arbitrary objects, keep their current handling.
10. No public API signature changes are required.

## Tech Stack

- Python and Django. The exact supported Python versions and target Django branch(es) are **unknown** from the issue.
- The affected module is `django.views.debug`: class `SafeExceptionReporterFilter`, methods `cleanse_setting()` and `get_safe_settings()`. For Django ≤ 3.0 the equivalent is the module-level `get_safe_settings()`.

## Commands

**Unknown.** The repository is not visible, and the issue does not state build, test or lint commands.

- Build: unknown
- Test: unknown (Django's own test runner invocation is not shown in the issue)
- Lint: unknown
- Dev: not applicable

## Project Structure

**Unknown** beyond what the issue states.

- Implementation: the module `django.views.debug`. The file path is inferred from the module name and is not confirmed.
- Tests: location unknown. Presumably they sit alongside the existing tests for `SafeExceptionReporterFilter`, but this is not confirmed.
- Docs and release notes: location unknown.

## Code Style

**Unknown.** Follow the existing conventions in `django.views.debug` and the project's contribution guidelines. The issue gives no style snippet.

## Testing Strategy

The framework and test file location are **unknown**. Tests are presumed to use Django's standard test suite. Required test cases:

- **Regression test from the issue:** `MY_SETTING` exactly as above produces the expected output.
- **List of dicts:** sensitive keys are masked inside each dict and non-sensitive keys are untouched.
- **Nested lists** (list of lists of dicts): sensitive keys are masked at depth.
- **Tuples:** the same cases as lists, and the result is still a tuple.
- **Dict → list → dict → list** mixed nesting: masking at every level.
- **Sensitive key with a list/tuple value:** the whole value is replaced by the mask, with no partial recursion.
- **Strings and bytes inside lists:** returned unchanged and not split into characters.
- **Lists of scalars under non-sensitive keys:** unchanged.
- **Non-mutation:** the original setting object is identical before and after the call.
- **Subclass override:** a custom filter with a different sensitive-key pattern or mask is honoured inside nested iterables. This applies only if those hooks exist (unconfirmed).
- **Debug page integration (optional):** the technical 500 response does not contain the nested secret values.

## Boundaries

**Always:**
- Keep the existing key-matching rules and mask string.
- Add regression tests that reproduce the issue's example.
- Leave the input settings unmutated.

**Ask first:**
- Extending recursion beyond list and tuple (set, frozenset, generic `Iterable`/`Mapping` subclasses, custom objects).
- Changing which keys count as sensitive.
- Backporting to older branches.
- Any change in the output type of cleansed values.

**Never:**
- Iterate or consume arbitrary iterables such as generators or iterators that may be single-use or have side effects.
- Recurse into strings or bytes.
- Weaken any existing cleansing behaviour.
- Expose settings values in tests' failure output or logs beyond what the fixtures contain.

## Success Criteria

- [ ] `SafeExceptionReporterFilter().get_safe_settings()["MY_SETTING"]` for the issue's example returns exactly the expected output above.
- [ ] Sensitive keys in dicts nested at any depth inside lists or tuples are replaced with the cleansed substitute.
- [ ] List and tuple types are preserved in the output.
- [ ] Top-level and dict-nested cleansing behaviour is unchanged. Existing tests still pass.
- [ ] Strings, bytes, scalars and other non-container values are returned as before.
- [ ] The original settings objects are not mutated.
- [ ] Every scenario under Testing Strategy has a test that fails before the fix and passes after it.
- [ ] Release notes and documentation are updated if the project requires it (location unknown).

## Open Questions

1. **Iterable scope:** Should recursion cover only `list` and `tuple`, or also `set`/`frozenset`, other `Mapping` types such as `OrderedDict` or custom mappings, and generic `Iterable`s? Sets cannot contain dicts, so they may be moot. Is preserving subclass types (for example namedtuples) required?
2. **Backport:** Is this treated as a security fix requiring backports to supported branches, including the pre-3.1 module-level `get_safe_settings()`? The security team approved public disclosure, but the release policy is not stated.
3. **Custom objects:** Should values that are neither dicts nor lists/tuples but contain sensitive data (for example objects with attributes) be addressed? The current assumption is no.
4. **Cycles:** Can settings contain self-referencing containers, and is cycle protection required?
5. **Callables:** Does the existing handling of callable settings (if any) need to interact with the new recursion?
6. **Exception-report variables:** Should the same recursion apply to other cleansing paths in the filter, such as frame-local variables? Or is the scope strictly settings?
7. **Repository details:** What are the actual test command, test file location and release-notes location?