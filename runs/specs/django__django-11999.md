# Spec: Allow user-defined `get_FOO_display()` overrides on models (regression since Django 2.2)

## Objective

From Django 2.2 onward, a model that defines its own `get_<field>_display()` method for a field with `choices` no longer uses that method. Django's auto-generated display method replaces it. In Django 2.1 the user-defined method took precedence.

**Goal:** Restore the 2.1 behaviour. A `get_<field>_display()` method that the developer explicitly defines on a model must take precedence over the one Django generates automatically.

**User:** Django application developers who customise how choice fields are displayed. This affects `__str__`, templates, admin, and serializers that call `get_FOO_display()`.

**User stories / acceptance criteria:**

- As a developer, when I define `get_foo_bar_display()` on a model with a `choices` field `foo_bar`, calling `instance.get_foo_bar_display()` returns my method's result.
- As a developer, when I do **not** define such a method, `instance.get_foo_bar_display()` keeps its current behaviour. It returns the human-readable label for the stored value, or the raw value if that value is not among the choices.
- Methods defined in the model class body or inherited from a parent class or mixin are not silently replaced. The exact inheritance expectations are listed under Open Questions.

**Reproduction (from the issue):**

```python
class FooBar(models.Model):
    foo_bar = models.CharField(_("foo"), choices=[(1, 'foo'), (2, 'bar')])

    def __str__(self):
        return self.get_foo_bar_display()  # 2.2+: 'foo' or 'bar'; 2.1: 'something'

    def get_foo_bar_display(self):
        return "something"
```

- **Expected:** `str(instance) == "something"`
- **Actual (2.2+):** `str(instance)` is `"foo"` or `"bar"`

## Assumptions

1. This is a regression introduced in Django 2.2. The 2.1 behaviour (user override wins) is the intended contract, not an accident.
2. The likely cause is a change in how the field attaches the generated `get_<name>_display` method during model class creation. In 2.2+ it appears to set the method unconditionally, overwriting any method already defined on the class. This is not verified, because no source code was available.
3. The example's quirks do not affect the bug and are not part of the defect:
   - It uses integer choice values on a `CharField`.
   - It has no `max_length`, which system checks would flag.
4. The fix should apply to every field type that supports `choices` and generates `get_FOO_display()`, not only `CharField`.
5. The fix should be backported to supported release branches. This depends on Django's backport policy, which is unknown here.
6. The public API stays as it is: the method name pattern `get_<field_name>_display` and its zero-argument signature are unchanged.

## Tech Stack

- Python and the Django ORM, model metaclass / field `contribute_to_class` machinery (assumed).
- Affected versions: Django 2.2 and later (per the issue). Working version: Django 2.1.
- Exact Python versions and the target branch are unknown.

## Commands

The issue does not provide them, so all are unknown.

- Build: unknown (likely not applicable)
- Test: unknown (Django's own test-runner invocation is not shown in the issue)
- Lint: unknown
- Dev: not applicable

## Project Structure

Not visible from the issue, so all are unknown.

- Location of the field code that generates `get_FOO_display`: unknown
- Location of the model-method / choices display tests: unknown
- Release notes location for documenting the regression fix: unknown

## Code Style

- Follow the existing Django code style in the files touched. The conventions are not visible here.
- The only code available is the reproduction snippet above. It should be the basis of the regression test.

## Testing Strategy

- **Framework:** Django's own test suite. The runner and location are unknown.
- **Regression test (required):** a model with a `choices` field and an explicitly defined `get_<field>_display()`. Assert that the override's return value is used.
- **Non-regression tests (required):**
  - With no override defined, `get_FOO_display()` returns the choice label for a known value.
  - With no override defined, `get_FOO_display()` returns the raw value for an unknown value.
  - The override can call the default display logic (e.g. via `super()`, if a parent provides it) without infinite recursion. See Open Questions.
- **Inheritance tests (pending answers to Open Questions):**
  - The override is defined on an abstract base class, and the field is on that base.
  - The override is defined on a child class, and the field is on the parent.
  - The override comes from a plain mixin.
  - A concrete child of a model whose field was auto-generated still gets correct behaviour.
- **Test levels:** unit/model-level tests only. No database-dependent behaviour is expected beyond model instantiation.
- **Coverage:** every new branch in the method-attachment logic is exercised.

## Boundaries

- **Always:**
  - Add the regression test from the issue's example.
  - Keep the default behaviour unchanged when no override exists.
  - Run the full model/field test suites before committing.
- **Ask first:**
  - Changing behaviour for overrides inherited from parent models or mixins, if that differs from 2.1.
  - Backporting to older release branches.
  - Adding any deprecation or warning.
  - Changing documented behaviour of `get_FOO_display()`.
- **Never:**
  - Change the method name pattern or signature.
  - Remove or weaken existing tests.
  - Alter unrelated field `contribute_to_class` behaviour, such as descriptors or other generated methods, beyond what this fix needs.

## Success Criteria

1. The issue's `FooBar` example returns `"something"` from both `str(instance)` and `instance.get_foo_bar_display()` on the fixed version.
2. Models without an override return identical `get_FOO_display()` results before and after the change. The existing test suite passes unchanged.
3. A new regression test fails on the current (2.2+) behaviour and passes after the fix.
4. The agreed inheritance scenarios (see Open Questions) behave as specified and are covered by tests.
5. A release note documents the fixed regression, if the project's process requires one (unknown).

## Open Questions

1. **Inheritance semantics:**
   - Should an override defined on a parent model, an abstract base, or a mixin also be respected?
   - Should a child model's auto-generated method replace a parent's custom one when the child redeclares the field?
   - What did 2.1 do in each of these cases?
2. **Calling the default implementation:** Should there be a supported way for an override to delegate to Django's default display logic? Examples are `super().get_foo_bar_display()` or a documented internal helper. Or is a full replacement the only supported pattern?
3. **Which 2.2 change caused this?** Was it deliberate (e.g. related to choices on inherited/overridden fields) in a way that a naive fix could break?
4. **Backport targets:** Which release branches should receive the fix?
5. **Documentation:** Should the docs state explicitly that `get_FOO_display()` can be overridden?
6. **Scope of related generated methods:** Should other auto-generated per-field methods (e.g. next/previous-by-date helpers) get the same "don't overwrite user-defined methods" treatment, or is that out of scope?
7. Repository paths, test commands, and lint commands are unknown and need to be supplied.