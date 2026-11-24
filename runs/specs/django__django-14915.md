# Spec: Make `ModelChoiceIteratorValue` hashable

## Assumptions

1. The project is Django itself. The fix belongs in the framework, not in user code.
2. `ModelChoiceIteratorValue` was introduced in Django 3.1. It wraps the raw choice value (usually a primary key) plus the model instance, and it is what `create_option()` receives as `value` for `ModelChoiceField` / `ModelMultipleChoiceField` widgets.
3. The class defines `__eq__`, which compares against the wrapped value, but does not define `__hash__`. Python sets `__hash__ = None` on any class that defines `__eq__` without `__hash__`, which explains the `TypeError: unhashable type`. This is inferred from the error message and has not been verified against source.
4. List membership (`value in [1, 2]`) works because it only uses `__eq__`. Dict and set membership fail because they need `__hash__` first. This matches the behaviour in the report.
5. The intended semantics are that a `ModelChoiceIteratorValue` behaves like its wrapped `.value` for equality, so it should also hash like it. Python's rule requires that `a == b` implies `hash(a) == hash(b)`.
6. Restoring 3.0-compatible behaviour for dict and set lookups counts as a regression fix and is eligible for the 3.1 stable branch. Backport policy is unconfirmed.

## Objective

Restore the Django 3.0 behaviour where the `value` passed to `ChoiceWidget.create_option()` for model choice fields can be used as a dict key or set member. Lookups such as `value in some_dict` and `some_dict[value]` must succeed and match entries keyed by the underlying primary key.

**User:** Developers who subclass `Select`, `SelectMultiple` and similar widgets used with `ModelChoiceField`, and who look up per-option metadata in dicts or sets keyed by pk. A common example is adding `data-*` attributes to options.

**User story:** As a developer upgrading from Django 3.0 to 3.1, I want `if value in self.show_fields:` to work in my `create_option()` override, so that my custom option attributes keep working without code changes.

**Acceptance criteria:**
- `hash(ModelChoiceIteratorValue(v, instance)) == hash(v)` for any hashable `v`.
- `ModelChoiceIteratorValue(1, obj) in {1: [...]}` is `True`.
- `{1: 'x'}[ModelChoiceIteratorValue(1, obj)]` returns `'x'`.
- `ModelChoiceIteratorValue(1, obj) in {1, 2}` is `True`.
- Existing equality behaviour is unchanged. This covers comparisons with raw values, with other `ModelChoiceIteratorValue` instances, and `str()` rendering.
- List membership, which already works, still works.

## Tech Stack

- Python and Django. The supported Python versions for the target branch are unknown.
- Affected component: Django forms. The class is expected to live alongside `ModelChoiceIterator` in Django's model forms module. The exact path is not visible in the issue and is marked as unknown.

## Commands

Unknown. The issue does not contain them. Expected form: Django's test runner, executed from the tests directory against the model forms test modules. The exact command and module labels still need to be confirmed.

- Build: N/A (Python library)
- Test: unknown
- Lint: unknown (presumably flake8/isort per Django contribution guidelines; unconfirmed)

## Project Structure

Unknown from the issue. Locations to be identified:

- **Source:** the module defining `ModelChoiceIteratorValue`.
- **Tests:** the existing test module covering `ModelChoiceField` / `ModelChoiceIterator` widgets.
- **Docs:** release notes for the relevant 3.1.x patch release, if this is treated as a regression fix.

## Code Style

The project's conventions are not visible in the issue. Follow existing Django style in the surrounding module. The reporter's reproduction, which must work after the change, is:

```python
def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
    context = super().create_option(name, value, label, selected, index, subindex, attrs)
    if not value:
        return context
    if value in self.show_fields:  # dict {1: ['first_name', 'last_name']}
        context['attrs']['data-fields'] = json.dumps(self.show_fields[value])
    return context
```

## Testing Strategy

- **Unit test** on `ModelChoiceIteratorValue`:
  - `hash()` equals the hash of the wrapped value.
  - The object can be used as a dict key and a set member.
  - It looks up correctly against raw-pk-keyed dicts.
- **Widget-level regression test:**
  - Write a `Select` subclass that overrides `create_option()` and does a dict lookup on `value`, mirroring the issue.
  - Render it for a `ModelChoiceField` with a real queryset.
  - Assert that the expected `data-*` attribute appears on the matching option.
- **Existing tests** in the model forms / widgets suites must keep passing.
- **Placement:** add the tests next to existing `ModelChoiceField` / iterator tests. The exact files are unknown.

## Boundaries

**Always:**
- Keep `__hash__` consistent with `__eq__`.
- Add a regression test that fails before the change.
- Follow Django's contribution and style guidelines.

**Ask first:**
- Changing `__eq__` semantics.
- Removing or replacing `ModelChoiceIteratorValue`.
- Changing what `create_option()` receives as `value`, for example passing the raw pk again.
- Backport scope.
- Adding a release note or doc change.

**Never:**
- Make the hash depend on the model instance or object identity, since that would break the equality contract.
- Make the wrapper mutable in a way that affects its hash.
- Require users to unwrap `value.value` as the "fix".

## Success Criteria

1. The reporter's `create_option()` example runs without `TypeError` on the target Django version.
2. It produces the same `data-fields` attribute it produced on Django 3.0.
3. A new regression test covering hashability and dict/set lookup passes, and fails without the change.
4. All existing forms and model-forms tests pass.
5. `a == b ⇒ hash(a) == hash(b)` holds for `ModelChoiceIteratorValue` versus its raw value.

## Open Questions

1. **Backport:** Should this be treated as a 3.1 regression and backported to the stable branch, with a release note in the next 3.1.x patch?
2. **Unhashable values:** If the wrapped `.value` is itself unhashable (unusual for a pk, but possible with a custom `to_field_name`), should `hash()` raise `TypeError` as the raw value would? Assumed yes.
3. **Documentation:** Should the docs for `ModelChoiceIteratorValue` and `create_option()` explicitly state that `value` is a wrapper and is hashable and comparable to the raw value?
4. **Repository details:** What are the exact source file, test module, and test command in the repository? These are not visible in the issue.