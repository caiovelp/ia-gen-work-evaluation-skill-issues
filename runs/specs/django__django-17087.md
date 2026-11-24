# Spec: Correct migration serialization of class methods on nested classes used as `Field.default`

## Objective

When a model field's `default` is a class method defined on a **nested class**, the migration autodetector writes a dotted reference that skips the enclosing class. The generated migration then fails when it is imported or applied.

**Reported example:**

- Model `Profile` defines a nested `Capability(models.TextChoices)` with `@classmethod default(cls)`.
- The field is `ArrayField(..., default=Capability.default)`.
- The migration contains `default=appname.models.Capability.default`.
- The correct reference is `appname.models.Profile.Capability.default`.

**Users:** Django developers who define choices classes, or other helper classes, inside a model and use their class methods as callable defaults.

**Goal:** The migration writer produces an importable reference for class methods at any nesting depth. The generated migration then loads and applies without manual edits.

### Acceptance criteria

- A class method on a class nested inside a model serializes to `<module>.<Outer>.<Inner>.<method>`.
- A class method on a top-level class still serializes exactly as it does today, so existing migrations see no changes.
- Deeper nesting, such as `Outer.Mid.Inner.method`, serializes with the full nested path.
- The generated migration imports the correct module and evaluates without `AttributeError`.
- Running `makemigrations` again on an unchanged model detects no changes.

## Assumptions

1. The defect is in Django's migration serialization of bound class methods. It most likely builds the path from the class's `__name__` instead of its qualified name, `__qualname__`. This is inferred from the symptom and not verified against source.
2. The bug does not depend on `ArrayField` or PostgreSQL. The issue uses `ArrayField`, but any field with `default=<nested class>.<classmethod>` should reproduce it.
3. The bug does not depend on `TextChoices`. Any nested class with a `@classmethod` should reproduce it.
4. Only the serialized form changes. The runtime behavior of defaults is unaffected.
5. Plain functions and static methods are out of scope unless they are found to have the same defect. Callables defined in local scopes (`<locals>`) remain non-serializable, as they are today.
6. The fix targets Django's main development branch. Whether it is backported is not decided here.

## Tech Stack

- Django, version not specified in the issue (unknown).
- The example uses `django.contrib.postgres.fields.ArrayField` and `models.TextChoices`.
- Python 3.9+ is implied by the `list[str]` annotation. The exact minimum is unknown.

## Commands

The issue does not state these, so they are unknown. Placeholders:

- Test: unknown. This is likely Django's test runner targeting the migrations test suite; to be confirmed.
- Lint/format: unknown.
- Reproduce: `python manage.py makemigrations`, then `python manage.py migrate` in a project containing the example model.

## Project Structure

The issue does not show this, so it is unknown.

- Code: the migration serializer module is suspected (path unknown).
- Tests: the existing migration-writer/serializer tests are expected to be the right place (path unknown).

## Code Style

No project code is visible. Follow Django's existing conventions in the serializer and its tests. A reproduction model, taken from the issue:

```python
class Profile(models.Model):
    class Capability(models.TextChoices):
        BASIC = ("BASIC", "Basic")
        PROFESSIONAL = ("PROFESSIONAL", "Professional")

        @classmethod
        def default(cls) -> list[str]:
            return [cls.BASIC]

    capabilities = ArrayField(
        models.CharField(choices=Capability.choices, max_length=30, blank=True),
        null=True,
        default=Capability.default,
    )
```

## Testing Strategy

**Unit tests at the serializer level:**

- Serializing a class method on a nested class yields the full qualified path and the correct import set.
- Serializing a class method on a top-level class yields the unchanged output, as a regression guard.
- A round-trip check: the serialized string evaluates, with its imports, back to the same callable.

**Optional integration test:**

- A model shaped like the example, run through the autodetector and writer, produces the correct `AddField` default.

**Database coverage:**

- No PostgreSQL-specific test is required if assumption 2 holds.

**Coverage:**

- Expectations are unknown. Follow project norms.

## Boundaries

**Always:**

- Add regression tests that reproduce the reported output before changing behavior.
- Keep output for top-level classes byte-identical.
- Follow the existing serializer patterns.

**Ask first:**

- Changing serialization of other callable kinds, such as functions, static methods, and `functools.partial`.
- Changing the error behavior for non-importable callables.
- Backporting the fix.

**Never:**

- Alter the semantics of existing migration files.
- Add dependencies.
- Make the fix specific to `ArrayField` or PostgreSQL.

## Success Criteria

- For the example model, `makemigrations` emits `default=appname.models.Profile.Capability.default`.
- The generated migration applies successfully with `migrate`.
- New tests fail before the change and pass after it.
- The full migrations test suite passes, and no existing serializer outputs change.

## Open Questions

1. Which Django version(s) are affected, and should the fix be backported?
2. Should static methods and plain functions on nested classes be audited and fixed in the same change?
3. Should a class method on a class defined inside a function (`<locals>` in its qualified name) raise a clear serialization error, matching the handling of other local callables?
4. Is an end-to-end autodetector test wanted, or are serializer-level tests sufficient?