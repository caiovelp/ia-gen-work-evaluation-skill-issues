# Spec: Serialize Enum Defaults in Migrations by Member Name, Not Value

## Objective

**Problem.** When an `Enum` member is used as a field argument, such as `default=Status.GOOD` on a `CharField`, the generated migration rebuilds it from its value: `Status('Good')`. If the value is a lazy translation (`gettext_lazy`), it resolves to a different string once the active language changes. The enum then has no member with the original value. Loading the old migration file raises:

```
ValueError: 'Good' is not a valid Status
```

This error breaks every management command that loads migrations whenever a non-default language is active.

**Goal.** The migration writer should reference Enum members by their **name**, which is stable. It should not use the **value**, which may be translated, computed or later changed. For the example in the issue, the output should be:

```python
('status', models.CharField(default=Status['GOOD'], max_length=128))
```

**Users.** Django developers who use `Enum` members in model field arguments that end up in migrations, especially when the enum values are translatable strings.

**Acceptance criteria / user stories:**
- As a developer, when I run `makemigrations` on a model with `default=Status.GOOD`, the migration file references the member by name.
- As a developer, when I activate another language and then load or apply migrations, I get no `ValueError` from enum lookup.
- As a developer, when I rename an enum *value* but keep the *name*, migrations that are already generated still load.

## Assumptions

1. The bug is in how the migration writer serializes `enum.Enum` instances. It is not in model field logic or in translation machinery.
2. The fix applies to all `enum.Enum` subclasses that the migration serializer handles. This includes Django's own choice enums (e.g. `TextChoices`/`IntegerChoices`), which are `Enum` subclasses.
3. Lookup by name (`Cls['NAME']` or `Cls.NAME`) gives back the same member that the current value-based lookup gives back. The deserialized object is therefore identical, and `makemigrations` will not see a change for fields whose enum value has not changed.
4. Migration files that already exist and contain `Status('Good')` will not be rewritten. They will keep failing under translation until the user regenerates or edits them by hand. This fix only affects newly generated migrations.
5. Required imports in the generated migration (the module that defines the enum) stay the same as today.
6. Enum aliases (two names with the same value) resolve to the canonical member. Serializing with the canonical member's `.name` is correct.

## Tech Stack

- Python, Django (migrations framework, `django.utils.translation`), standard-library `enum`.
- Versions: **unknown** (not stated in the issue).

## Commands

- Build: **unknown** (not visible from the issue)
- Test: **unknown** (presumably the project's standard test runner targeting migration-writer tests; exact command not available)
- Lint: **unknown**
- Dev/repro: `makemigrations` on the example app (exact invocation path **unknown**)

## Project Structure

- Location of the migration serializer/writer code: **unknown** (no repository access; assumed to be the migrations serialization module).
- Location of the existing migration-writer tests: **unknown**.
- Docs that describe what migrations can serialize: **unknown**, but they may need updating.

## Code Style

- Follow the existing conventions of the surrounding serializer code. These conventions are **unknown** because the code is not visible.
- Expected generated-output style, as given in the issue:
  ```python
  default=Status['GOOD']
  ```
  The final form (`Status['GOOD']` vs `Status.GOOD`) is listed under Open Questions.

## Testing Strategy

- **Unit tests (migration writer/serializer):**
  - Serializing a plain `Enum` member produces a name-based reference and the correct import set.
  - Round trip: the serialized string, evaluated with its imports, returns the identical member (`is`).
  - Enum whose values are `gettext_lazy` strings: the output contains the member name and no translated or untranslated value.
  - Enums with non-string values (int, bytes, tuple) are serialized by name too.
  - Django choice enums (`TextChoices`, `IntegerChoices`) produce name-based output.
- **Regression test:** with the enum value changed or translated after serialization, the serialized string still evaluates to the correct member.
- **Integration (if the existing suite supports it):** run `makemigrations` and load the migration under a non-default active language without error.
- Coverage target: **unknown**. At minimum, every branch of the changed serialization path.

## Boundaries

- **Always:**
  - Keep the deserialized object identical to the original member.
  - Keep existing serializer tests passing, updating expected strings only where the format change requires it.
  - Add regression tests for the translated-value scenario.
- **Ask first:**
  - Choose between output forms (`Cls['NAME']` vs `Cls.NAME`).
  - Decide how to handle combined `Flag`/`IntFlag` values, which have no single name.
  - Make any change that would cause `makemigrations` to detect changes in projects that are otherwise unchanged.
  - Add any release-note or documentation change about the new serialization format.
- **Never:**
  - Rewrite or auto-migrate users' existing migration files.
  - Change model field behaviour or translation behaviour to work around the issue.
  - Remove or weaken existing serializer tests without approval.

## Success Criteria

1. Serializing `Status.GOOD` from the issue example produces a name-based reference (e.g. `Status['GOOD']`) and never `Status('Good')`.
2. Evaluating the serialized output with its imports returns `Status.GOOD`, whatever language is active.
3. A migration generated after the fix loads without `ValueError` after the enum's translated values change.
4. Running `makemigrations` again on a project with no model changes produces no new migration after the fix.
5. Existing serializer tests pass, with expected strings updated for the new format where needed. New tests cover the cases listed in the Testing Strategy.

## Open Questions

1. **Output form:** should it be `Status['GOOD']` (as the issue proposes) or `Status.GOOD`? Both are name-based. Attribute access is more readable but would break for names that are not valid identifiers, or for names that clash with methods or attributes.
2. **Flag enums:** a combined `Flag` value (e.g. `Perm.READ | Perm.WRITE`) may have no single `.name`, depending on the Python version. Should we serialize it as an OR of member names, fall back to value-based serialization, or raise an error?
3. **Backward compatibility:** do we need a documentation or release note telling users to regenerate or hand-edit old migrations that contain value-based references?
4. **Scope:** should the same name-based approach apply everywhere the serializer meets an `Enum` (e.g. `choices`, validators, custom field kwargs), or only defaults? The assumption here is everywhere.
5. **Supported Python/Django versions** for this change, and whether it should be backported. These are unknown.
6. **Test command and file locations** in the repository are unknown and need confirming.