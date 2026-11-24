# Spec: Correct Import Paths for Nested Classes in Generated Migrations

## Objective

When `manage.py makemigrations` serializes a field or field argument whose class is defined **inside another class**, the generated migration refers to it as a top-level class of its module. The outer class name is dropped.

| Input | Currently generated | Expected |
|---|---|---|
| Field subclass `Outer.Inner` in `test1/models.py` | `test1.models.Inner(max_length=20)` | `test1.models.Outer.Inner(max_length=20)` |
| Enum `Thing.State` passed as `EnumField(enum=State)` | `enum=test1.models.State` | `enum=test1.models.Thing.State` |

The generated migration then fails at import or load time with `AttributeError` on the module, or it resolves to the wrong object.

**Users:** Django developers who nest custom field classes, or classes passed as field arguments (enums, choices classes, and so on), inside other classes or models. Third-party field authors, such as django-enumfields, are affected indirectly.

**Success:** Generated migrations reference nested classes by their full dotted path within the module (`module.Outer.Inner`). The migration file imports and applies without errors.

### Acceptance criteria

1. A model field whose class is a nested `Field` subclass is serialized as `<module>.<Outer>.<Inner>(...)`.
2. A class object passed as a field argument, where that class is nested in another class or model, is serialized as `<module>.<Outer>.<Inner>`.
3. Nesting deeper than one level is serialized with every enclosing class in the path, for example `<module>.A.B.C`.
4. The import statement emitted for the migration is still the **module** (for example `import test1.models`), not a nonexistent `test1.models.Outer` module.
5. Serialization of top-level classes and existing built-in references (for example `models.CharField`, `models.AutoField`) is unchanged.
6. A generated migration containing nested references can be imported and executed, so `migrate` succeeds.

## Assumptions

1. The bug is in Django core's migration serialization (field deconstruction and/or type/class serialization), not in django-enumfields. Both reproductions share one symptom: the outer class name is lost. That suggests a single root cause, probably the use of the class's short name instead of its qualified name. This is unverified because the source is not visible.
2. Python 3 is targeted, where `__qualname__` is available. Python 2 support is out of scope unless the target branch still requires it.
3. Classes defined inside **functions** (qualified names containing `<locals>`) cannot be imported. Their current behavior is out of scope, beyond not making it worse.
4. The fix belongs in Django core and must not require third-party field authors to change their `deconstruct()` implementations.
5. Already-generated migrations with incorrect paths are not rewritten automatically. Users regenerate them or fix them by hand.

## Tech Stack

- Django. The affected version or branch is **unknown** and not stated in the issue.
- Python 3 (assumed; see Assumptions).
- Reproduction uses django-enumfields (`enumfields.Enum`, `enumfields.EnumField`). This is for the reproduction only, not as a dependency of the fix.

## Commands

- Reproduce: `manage.py makemigrations` (taken from the issue).
- Build: **unknown**.
- Test runner and flags for the Django test suite: **unknown** (repository not visible).
- Lint: **unknown**.

## Project Structure

- App module in the reproduction: `test1/models.py`, inferred from the generated reference `test1.models`.
- Location of Django's migration serializer and field deconstruction code: **unknown**, not visible.
- Location of existing migration-writer and serializer tests: **unknown**.

## Code Style

No project code is visible. Follow the existing Django conventions in the files touched. The inputs that reproduce the problem, taken verbatim from the issue:

```python
class Outer(object):
    class Inner(models.CharField):
        pass

class A(models.Model):
    field = Outer.Inner(max_length=20)
```

```python
import enum
from enumfields import Enum, EnumField

class Thing(models.Model):
    @enum.unique
    class State(Enum):
        on = 'on'
        off = 'off'
    state = EnumField(enum=State)
```

## Testing Strategy

- **Unit tests (migration serializer/writer):**
  - Serialize a nested `Field` subclass and assert both the output string (`<module>.Outer.Inner(...)`) and the emitted import set (`{'import <module>'}`).
  - Serialize a nested class used as a value, both a plain class and an `enum.Enum` subclass nested in a class or model, and assert the full dotted path.
  - Cover multi-level nesting.
  - Regression: assert that top-level classes and Django built-in fields serialize exactly as before.
- **Round-trip test:** Write the serialized migration operation and import or `exec` it to confirm it resolves to the original class.
- **Integration test (optional):** Run `makemigrations` against a test app containing the issue's models, then load the resulting migration.
- The test framework and file locations follow the existing Django test suite. Their exact paths are **unknown**.
- No regressions in existing migration tests.

## Boundaries

- **Always:**
  - Add regression tests reproducing both cases from the issue.
  - Keep import statements module-level.
  - Preserve output for top-level classes.
  - Run the existing migrations test suite.
- **Ask first:**
  - Changing the public `deconstruct()` contract or return format.
  - Changing how local (function-scoped) classes are handled.
  - Any behavior change that alters generated output for existing, non-nested projects. That would cause spurious migration diffs.
- **Never:**
  - Fix this only in django-enumfields or another third-party library.
  - Emit imports of class paths as if they were modules.
  - Rewrite users' existing migration files.
  - Remove or weaken existing serializer tests.

## Success Criteria

- [ ] `makemigrations` on the `Outer.Inner` example produces `test1.models.Outer.Inner(max_length=20)`.
- [ ] `makemigrations` on the `Thing.State` example produces `enum=test1.models.Thing.State`.
- [ ] Both generated migrations import and apply successfully with `migrate`.
- [ ] Multi-level nesting serializes with the full qualified path.
- [ ] Output for top-level and built-in classes is byte-identical to before.
- [ ] New unit tests fail before the fix and pass after it, and the full migrations test suite passes.

## Open Questions

1. Which Django version or branch should the fix target, and does it still need Python 2 compatibility (no `__qualname__`)?
2. Should the fix live in field deconstruction (the field's own path), in the generic class/type serializer (class values passed as arguments), or in both? The issue shows both symptoms.
3. How should classes defined inside functions (`<locals>` in the qualified name) be handled: an explicit error with a helpful message, or the current behavior?
4. Should `makemigrations` detect and warn about existing migrations that contain the old incorrect paths, or is that out of scope?
5. Are there other serialization paths that should be covered and verified in the same change, such as managers, validators, or `default` callables that are nested classes?
6. What are the exact test commands and test file locations for the target repository?