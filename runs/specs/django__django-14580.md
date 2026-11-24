# Spec: Missing `models` import in generated migration when `bases` includes `models.Model`

## Objective

`makemigrations` can write a migration file that is not valid Python. When a model's bases are serialized as `models.Model`, the file does not include `from django.db import models`. Importing the migration then raises `NameError: name 'models' is not defined`.

**User:** A Django developer who runs `makemigrations` on a project whose models combine a plain Python mixin with an abstract base model.

**Reproduction (from the issue, Django 3.2.4):**

```python
from django.db import models

class MyField(models.TextField):
    pass

class MyBaseModel(models.Model):
    class Meta:
        abstract = True

class MyMixin:
    pass

class MyModel(MyMixin, MyBaseModel):
    name = MyField(primary_key=True)
```

**Generated migration (abridged):**

```python
import app.models
from django.db import migrations
...
            bases=(app.models.MyMixin, models.Model),
```

**Observed:** `NameError: name 'models' is not defined` at the `bases=` line when the migration module is loaded.

**Expected:** The generated migration is valid Python. It imports everything it references, so it can be loaded and applied.

**Observations from the reproduction:**
- The abstract `MyBaseModel` is replaced by `models.Model` in `bases`. This is expected behaviour.
- `app.models` is imported because of `MyField` and `MyMixin`.
- The `migrations` import is present.
- The `models` import is not emitted. In other generated migrations it is normally merged into `from django.db import migrations, models`.
- In this file, nothing else (for example a built-in field) references `models`, so nothing else pulls the import in.

**User stories / acceptance criteria:**
- When a model's serialized `bases` includes `models.Model`, the migration file includes `from django.db import models`. With the usual merge this reads `from django.db import migrations, models`.
- This holds even when no field or other operation argument references `models`.

## Assumptions

1. The bug is in migration *serialization/writing*, not in autodetection. The `bases` value `(MyMixin, models.Model)` is correct; only the import set is incomplete. The reporter suspects `django.db.migrations.writer`. The exact responsible component (writer vs. serializer) has not been confirmed.
2. The serialization of the `models.Model` class reference produces the string `models.Model` but does not register the matching import. This is the most likely mechanism. It is a hypothesis, not yet verified.
3. The existing import-merging behaviour stays unchanged: `django.db` `migrations` and `models` combine into one line, and imports are sorted.
4. The fix should apply to supported branches affected by the bug, starting with 3.2.x. Backport policy is the maintainers' decision.
5. Output formatting of unaffected migrations must not change. Existing generated files and snapshot-style tests should stay stable.

## Tech Stack

- Python, Django (bug reported on 3.2.4).
- Affected area: migration framework. The reporter names `django.db.migrations.writer`; the serializer module may also be involved (unconfirmed).
- Exact supported Python versions for the target branch: **unknown** (not in the issue).

## Commands

- Build: **unknown** (not applicable / not stated in the issue)
- Test: **unknown.** The Django test runner invocation and the relevant test labels for migration writer tests are not visible.
- Lint: **unknown**
- Reproduce manually: create an app containing the `models.py` above, run `makemigrations`, then load or apply the migration (for example with `migrate`). The exact `manage.py` invocation and project layout are not given beyond the app being named `app`.

## Project Structure

- Source location of the migration writer/serializer: **unknown** (only the module path `django.db.migrations.writer` is mentioned).
- Location of existing migration writer tests: **unknown**.
- Documentation and release-notes location for a bugfix entry: **unknown**.

## Code Style

- Follow the existing conventions of the Django codebase. No code from the affected modules is visible in the issue, so there is no style snippet to show.
- The generated migration output must match Django's existing migration formatting:
  - header comment
  - sorted imports
  - `from django.db import migrations, models` merging

## Testing Strategy

- **Regression test (unit level):** Serialize or write a migration whose `CreateModel` has `bases` containing `models.Model` together with a non-Django class. Assert two things:
  - The output contains the `models` import.
  - The output is valid, executable Python (it compiles and loads without `NameError`).
- **Serializer-level test (if the cause is confirmed there):** Serializing `models.Model` returns both the expected string and the `from django.db import models` import.
- **Scenario test:** The exact reproduction from the issue (mixin + abstract base + custom primary-key field) yields a loadable migration.
- **Non-regression:** The existing migration writer and serializer test suites pass unchanged.
- Test framework and file locations: **unknown** (Django's own test suite assumed).

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue.
  - Keep generated output for unaffected migrations byte-identical.
  - Run the existing migration test suites.
- **Ask first:**
  - Changing how abstract bases are collapsed into `models.Model`.
  - Changing import ordering or merging rules.
  - Touching autodetector logic.
  - Deciding on backport targets.
- **Never:**
  - Work around the problem by emitting unconditional or unused imports in every migration, unless maintainers approve.
  - Alter existing migration files in the repository.
  - Remove or weaken existing tests.

## Success Criteria

1. Running `makemigrations` on the issue's `models.py` produces a migration that imports `models` from `django.db` and loads and applies without error.
2. Every serialized reference to `models.Model` in a migration comes with its required import, whatever other operations or fields are present.
3. A new automated test fails before the fix and passes after it.
4. All existing migration writer/serializer tests pass. Formatting of other generated migrations is unchanged.

## Open Questions

1. Is the root cause in the serializer, e.g. the special-case handling for the `models.Model` type reference? Or is it in the writer's import collection? Confirming this decides where the fix and its test belong.
2. Are other special-cased type references affected by the same missing-import problem and in need of the same fix? For example, other `django.db` references emitted without imports.
3. Which branches should receive the fix: 3.2.x only, or also the development branch and other supported releases?
4. Is a release-notes entry needed for this bugfix, and in which release-notes file?
5. What are the exact test command and test labels for the migration writer/serializer tests in the target branch?