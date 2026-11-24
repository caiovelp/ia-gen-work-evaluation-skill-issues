# Spec: Allow subclasses of BigAutoField / SmallAutoField as `DEFAULT_AUTO_FIELD`

## Assumptions

1. The issue describes Django's handling of the `DEFAULT_AUTO_FIELD` setting. The traceback suggests Django 3.2.x (`venv/.../django/db/models/options.py`, Python 3.9). The exact version and branch are **unknown**.
2. The failing check is in `Options._get_default_pk_class()` (`django/db/models/options.py`, around line 246 in the reporter's install). It raises `ValueError` when the configured class does not "subclass AutoField".
3. That check uses `issubclass(pk_class, AutoField)`. The result comes from `AutoFieldMeta.__subclasscheck__` (the reporter names this), which consults a `_subclasses` property. I assume that property contains `BigAutoField` and `SmallAutoField` and checks them by **identity/membership**, not by subclass relationship. Under that assumption, `BigAutoField` passes but a user subclass of it does not. The source itself was not seen.
4. The same metaclass likely implements `__instancecheck__` as well. I assume it has the same identity-based flaw for instances of user subclasses, though the issue does not show this.
5. Direct subclasses of `AutoField` (e.g. `class MyAutoField(models.AutoField)`) already work, through normal inheritance.
6. Multi-level subclasses (e.g. `class A(BigAutoField)`, `class B(A)`) should be accepted the same way as single-level ones.
7. No change to the error message or to the `DEFAULT_AUTO_FIELD` / `AppConfig.default_auto_field` semantics is intended. Only the subclass detection is wrong.
8. Any setting that resolves through `_get_default_pk_class()` is affected the same way. This includes the per-app `AppConfig.default_auto_field`, which I assume uses the same code path (not confirmed).

## Objective

Django users must be able to set `DEFAULT_AUTO_FIELD` (or `AppConfig.default_auto_field`) to a custom subclass of `models.BigAutoField` or `models.SmallAutoField`. Today, Django crashes during `django.setup()` / model import with:

```
ValueError: Primary key 'example.core.models.MyBigAutoField' referred by DEFAULT_AUTO_FIELD must subclass AutoField.
```

The fix scope is the subclass check: `issubclass(X, AutoField)` must return `True` for any class that inherits, directly or indirectly, from `BigAutoField` or `SmallAutoField`. It must return `False` for classes that do not.

**User story:** As a Django developer, I define `class MyBigAutoField(models.BigAutoField): pass` and set `DEFAULT_AUTO_FIELD` to it. I expect my models to get an auto-created primary key of that type, without errors.

**Reproduction (from the issue):**

```python
# example/core/models.py
from django.db import models

class MyBigAutoField(models.BigAutoField):
    pass

class MyModel(models.Model):
    pass
```

```python
# settings
DEFAULT_AUTO_FIELD = "example.core.models.MyBigAutoField"
```

## Tech Stack

- Python (3.9 in the report; supported range unknown)
- Django (3.2.x inferred from the traceback; exact version unknown)
- Relevant modules named in the traceback/issue:
  - `django/db/models/options.py` (`Options._prepare`, `Options._get_default_pk_class`)
  - `django/db/models/base.py` (`ModelBase.__new__`, `_prepare`)
  - `AutoFieldMeta` (`__subclasscheck__`, `_subclasses`). Its location is presumed to be `django/db/models/fields/__init__.py`, which is **unconfirmed**.

## Commands

Unknown. The repository is not visible. The project's test runner invocation and any lint commands must be confirmed. See Open Questions.

- Build: unknown / not applicable
- Test: unknown
- Lint: unknown

## Project Structure

Only the paths visible in the traceback are known:

```
django/db/models/base.py      → ModelBase metaclass, model preparation
django/db/models/options.py   → Options._get_default_pk_class (raises the ValueError)
django/apps/config.py         → AppConfig.import_models
django/apps/registry.py       → Apps.populate
```

The location of `AutoFieldMeta` and of the relevant existing test modules is **unknown**.

## Code Style

Unknown. Follow the existing conventions of the surrounding code in `AutoFieldMeta` and `options.py`. No style sample is available from the issue.

## Testing Strategy

- **Framework:** the project's existing test suite. The runner and command are unknown.
- **Unit level (metaclass):**
  - `issubclass(MyBigAutoField, models.AutoField)` is `True`.
  - `issubclass(MySmallAutoField, models.AutoField)` is `True`.
  - The same holds for a second-level subclass.
  - The existing truths still hold: `issubclass(BigAutoField, AutoField)`, `issubclass(SmallAutoField, AutoField)`, `issubclass(AutoField, AutoField)`.
  - Unrelated fields still return `False`, e.g. `issubclass(models.TextField, AutoField)`, and also `IntegerField` / `BigIntegerField`.
- **Instance level (if assumption 4 holds):** `isinstance(MyBigAutoField(), models.AutoField)` is `True`.
- **Integration level (options):**
  - A model defined under `override_settings(DEFAULT_AUTO_FIELD=<path to subclass of BigAutoField>)` gets an auto-created `id` primary key of that subclass type, without raising. Repeat for a `SmallAutoField` subclass.
  - Repeat for `AppConfig.default_auto_field` if it shares the code path.
- **Regression:** a non-AutoField class (e.g. `TextField`) set as `DEFAULT_AUTO_FIELD` still raises the same `ValueError` with the same message.
- Existing tests for `DEFAULT_AUTO_FIELD` and the AutoField hierarchy must continue to pass.

## Boundaries

- **Always:**
  - Keep the fix limited to subclass/instance detection for the AutoField family.
  - Add regression tests for both `BigAutoField` and `SmallAutoField` subclasses.
  - Run the existing model/options test suites.
- **Ask first:**
  - Changing the `ValueError` message.
  - Changing the public `AutoField` / `BigAutoField` / `SmallAutoField` class hierarchy (e.g. making them true `AutoField` subclasses), rather than fixing the metaclass check.
  - Backporting to release branches.
  - Changing `__instancecheck__` behavior beyond mirroring the subclass fix.
- **Never:**
  - Remove or weaken the validation that `DEFAULT_AUTO_FIELD` must be an AutoField-family class.
  - Make unrelated fields (e.g. `BigIntegerField`) pass the check.
  - Alter behavior for the built-in default (`AutoField`).

## Success Criteria

1. With the reproduction above, `django.setup()` / importing the models module completes without `ValueError`.
2. `MyModel._meta.pk` is an instance of `MyBigAutoField`.
3. Points 1 and 2 also hold for a subclass of `SmallAutoField`, and for a multi-level subclass (subclass of a subclass) of either.
4. `issubclass(X, models.AutoField)` is `True` for subclasses of `BigAutoField`/`SmallAutoField`. It is unchanged (`True`) for `AutoField`, `BigAutoField`, `SmallAutoField` and direct `AutoField` subclasses.
5. `issubclass(X, models.AutoField)` remains `False` for non-AutoField-family classes. Setting such a class as `DEFAULT_AUTO_FIELD` still raises the existing `ValueError`.
6. New regression tests covering points 1–5 pass. All pre-existing tests pass.

## Open Questions

1. Which Django version(s)/branches does the fix target, and should it be backported to the 3.2 release branch?
2. Where exactly is `AutoFieldMeta` defined, and what is the current implementation of `_subclasses`, `__subclasscheck__` and `__instancecheck__`? This would confirm assumptions 3 and 4.
3. Should `isinstance()` checks for instances of user subclasses also be fixed in the same change, if they are affected?
4. Does `AppConfig.default_auto_field` go through the same `_get_default_pk_class()` check, so it should be covered by tests too?
5. What are the exact test command and the appropriate test modules for metaclass and `DEFAULT_AUTO_FIELD` tests?
6. Is the reporter's suggested approach the preferred one: fixing `AutoFieldMeta.__subclasscheck__` / `_subclasses` to recognize subclasses of `BigAutoField` and `SmallAutoField`? Or is a broader hierarchy change acceptable?