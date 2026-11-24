# Spec: Consistent String Representation of `TextChoices` / `IntegerChoices` Members

## Assumptions

1. This is a bug report against Django's enumeration types (`models.TextChoices`, `models.IntegerChoices`, and presumably the base `models.Choices`), introduced in Django 3.0. The reporter's environment is named `django30`.
2. The root behavior is that `str()` (and likely `format()` / f-strings) on a Choices member returns the `enum.Enum` default representation (`'MyChoice.FIRST_CHOICE'`), not the underlying value (`'first'`).
3. The model attribute keeps the enum member on a freshly created instance, because the field stores whatever was assigned and does not coerce it until a save/load round-trip. A retrieved instance holds a plain `str`/`int` from the database. This explains why one test fails and the other passes.
4. `isinstance(MyChoice.FIRST_CHOICE, str)` is already `True`, because `TextChoices` mixes in `str`. Only the string representation differs. The first assertion in the failing test passes and the second fails.
5. The expected fix scope is the string representation of Choices members. Changing field assignment semantics, such as coercing enum members to raw values on `__set__`, is out of scope unless maintainers decide otherwise. See Open Questions.
6. `IntegerChoices` has the same issue: `str(MyIntChoice.ONE)` returns `'MyIntChoice.ONE'` rather than `'1'`. The issue implies this but does not demonstrate it.
7. The fix must not break the `.label`, `.value`, `.name`, `.choices`, `.labels`, `.values`, and `.names` APIs, nor equality and hashing between members and raw values.

## Objective

**What:** Make `str()` of a Django Choices enum member return the string form of its value. For example, `str(MyChoice.FIRST_CHOICE)` should return `"first"`.

**Why:** A freshly created model instance holds the enum member, while a retrieved instance holds the raw value. Today the two stringify differently (`'MyChoice.FIRST_CHOICE'` vs `'first'`). Code that serializes model data, such as templates, API payloads, logging, and string formatting, therefore sends inconsistent data depending on whether the instance was just created or loaded from the database.

**Users:** Django application developers who use `TextChoices` / `IntegerChoices` with `choices=` on model fields.

**Acceptance criteria (user stories):**
- As a developer, when I create an object with `my_str_value=MyChoice.FIRST_CHOICE`, `str(obj.my_str_value)` returns `"first"`. This matches what I get after `MyObject.objects.last()`.
- As a developer, the same holds for `IntegerChoices`: `str(obj.my_int_value)` returns the decimal string of the integer value on both created and retrieved instances.
- As a developer, string formatting of a member (f-strings / `format()`) produces the value, not `ClassName.MEMBER`. This needs confirmation; see Open Questions.

## Tech Stack

- Python, with the `enum` standard library module. The minimum Python version supported by the target Django branch is **unknown**.
- Django `django.db.models` enumeration types (`Choices`, `TextChoices`, `IntegerChoices`). The exact module path is **unknown** from the issue.
- Target Django version/branch for the fix is **unknown**. The bug was reported on 3.0.

## Commands

All commands are **unknown**; the repository is not visible. The reporter used `./manage.py test` in their own project, which is not the Django test suite.

```
Build: unknown
Test: unknown (Django core test runner command not visible in issue)
Lint: unknown
Dev: n/a (library)
```

## Project Structure

**Unknown.** The issue does not show Django's source layout. Needed locations:
- The source file defining `Choices` / `TextChoices` / `IntegerChoices`: unknown path.
- The existing tests for enumeration types: unknown path.
- The documentation for enumeration types in the model field reference, plus release notes for the target version: unknown paths.

## Code Style

Follow existing Django conventions in the enums module (unknown; not visible). The reproduction from the issue serves as the behavioral reference:

```python
class MyChoice(models.TextChoices):
    FIRST_CHOICE = "first", _("The first choice, it is")
    SECOND_CHOICE = "second", _("The second choice, it is")

class MyObject(models.Model):
    my_str_value = models.CharField(max_length=10, choices=MyChoice.choices)

obj = MyObject.objects.create(my_str_value=MyChoice.FIRST_CHOICE)
assert isinstance(obj.my_str_value, str)
assert str(obj.my_str_value) == "first"            # currently fails: 'MyChoice.FIRST_CHOICE'
assert str(MyObject.objects.last().my_str_value) == "first"   # currently passes
```

## Testing Strategy

- **Unit tests (enum level):** Add tests in Django's existing enumeration-type test module (path unknown) asserting that:
  - `str(member) == str(member.value)` for `TextChoices` members.
  - `str(member) == str(member.value)` for `IntegerChoices` members.
  - The same holds for custom `Choices` subclasses with other mixin types (e.g. a `float` or `date` mixin), if the base `Choices` is in scope.
  - `format(member)` / f-string output equals the value's string form (pending Open Question 2).
- **Model-level tests:** A model with a `CharField` and an `IntegerField` using `choices=`. Assert that `str(field_value)` is identical on a freshly created instance and on a re-fetched instance. This mirrors the issue's two tests.
- **Regression:** The existing enumeration tests (`.label`, `.choices`, `.values`, `.names`, equality with raw values, membership, `repr`) must continue to pass.
- Coverage expectations: **unknown** project policy. At minimum, both failing paths described above must be covered.

## Boundaries

- **Always:**
  - Keep `repr(member)` informative, i.e. unchanged as `<MyChoice.FIRST_CHOICE: 'first'>` unless maintainers decide otherwise.
  - Preserve equality and hashing between members and raw values.
  - Add tests that fail before the change and pass after.
  - Add a release note if behavior changes in a released version.
- **Ask first:**
  - Changing field descriptor or assignment behavior so that enum members are coerced to raw values on assignment or `save()`.
  - Changing `__format__` behavior.
  - Applying the change to the base `Choices` class (arbitrary mixins) rather than only `TextChoices` / `IntegerChoices`.
  - Backporting to stable branches.
- **Never:**
  - Change `.label`, `.value`, or `.choices` output.
  - Alter the database storage format.
  - Remove or weaken existing enumeration tests.

## Success Criteria

1. `str(MyChoice.FIRST_CHOICE) == "first"` for a `TextChoices` member.
2. `str(MyIntChoice.X) == str(MyIntChoice.X.value)` for an `IntegerChoices` member.
3. For a model field with `choices=MyChoice.choices`, `str(obj.field)` returns the same string for an instance returned by `objects.create(field=MyChoice.FIRST_CHOICE)` and the same row re-fetched from the database. Both tests from the issue pass.
4. `repr()` of members, `.label`, `.value`, `.name`, `.choices`, equality (`MyChoice.FIRST_CHOICE == "first"`), and existing enum tests are unchanged and pass.
5. Documentation and release notes reflect the behavior, if maintainers consider it a user-visible change. Doc location is unknown.

## Open Questions

1. **Scope of fix:** Should only `str()` of Choices members change? Or should model field assignment also normalize enum members to their raw value, so created and retrieved instances hold identical types (`str` vs `MyChoice`)? The latter is a larger behavior change.
2. **Formatting:** Should `format(member)` and f-strings also yield the value? On some Python versions, `str`/`int` mixin enums already format as the value while `str()` does not. Should behavior be made consistent across `str()` and `format()` regardless of Python version?
3. **Base class:** Should the `__str__` change live on the base `Choices` class, so it covers custom mixins like `float` or `datetime.date`? Or only on `TextChoices` and `IntegerChoices`?
4. **Target versions:** Is this treated as a bug in a new 3.0 feature, eligible for backport to the 3.0.x stable branch? Or is it a behavior change for the next feature release only?
5. **Backward compatibility:** Is any existing code expected to rely on `str(member) == 'ClassName.MEMBER'`? Does this warrant a release-note callout?
6. **Repository details:** What are the exact source path for the enums module, the test module location, and the test/lint commands for the Django codebase? All are unknown from the issue.