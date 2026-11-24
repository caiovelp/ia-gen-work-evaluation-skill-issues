# Spec: Allow `FilePathField.path` to Accept a Callable

## Objective

**Problem.** `django.db.models.FilePathField(path=...)` takes a string. When the path is built from machine-specific settings, e.g. `os.path.join(settings.LOCAL_FILE_DIR, 'example_dir')`, the string is evaluated at import time. `makemigrations` then writes the resolved absolute path into the migration, such as `/home/<username>/server_files/example_dir`. That migration is wrong on every other machine, so the reporter had to hand-edit the migration file.

**Goal.** Let `path` accept a callable that returns the path string. Django resolves the callable when the path is actually needed. Migrations serialize a reference to the callable instead of its result, so they stay machine-independent.

**Users.** Django developers whose model field paths depend on the environment (settings, environment variables, deployment layout).

**User story.**
> As a developer, I can write `models.FilePathField(path=get_local_dir)` where `get_local_dir` is a module-level function. `makemigrations` records a reference to `get_local_dir` rather than a hard-coded absolute path. Forms built from the field list files from the directory that the callable returns at runtime.

**Acceptance criteria**
1. `FilePathField(path=<callable>)` can be declared on a model without error.
2. When the field's form field is built (e.g. via `ModelForm` or `formfield()`), the callable is invoked. The resulting form field receives the returned string as its `path`.
3. `deconstruct()` returns the callable itself in `kwargs['path']`, not its return value. The migration writer serializes it as an import reference, the same way other callable field arguments are handled (e.g. `FileField.upload_to`, `default`).
4. Existing string-based `path` usage behaves exactly as before, including deconstruction, the default `path=''`, migrations, and form output.
5. The other `FilePathField` options keep working with a callable `path`: `match`, `recursive`, `allow_files`, `allow_folders`, and `max_length`.
6. The model field docs state that `path` may be a callable, with an example. A release note / "versionchanged" entry is added according to the project's conventions.

## Assumptions

1. This change targets Django's model field `django.db.models.FilePathField`. The form field `django.forms.FilePathField` stays string-only and receives the resolved path.
2. The callable takes **no arguments** and returns a `str` (or path-like) directory path. Unlike `upload_to`, it does not receive an instance or filename.
3. The callable is resolved **lazily**, at form-field construction time, and not at model class definition time. Otherwise the import-time problem persists.
4. Callables must be serializable by the existing migration writer, meaning importable module-level functions. Lambdas and nested functions get the same serialization error that other callable field args get today.
5. No database schema change is involved. The field stays a `varchar`, and `path` has no effect at the DB level.
6. The fix belongs in Django core, not in a third-party package or project-local workaround.
7. Resolved paths are not validated for existence at model-check time. The existing behavior, failing when the form field scans the directory, is kept.

## Tech Stack

- Python and Django (exact supported versions **unknown**; follow the target branch's minimums).
- Affected areas: the model fields module (`FilePathField`), migration serialization (expected to need no change if callables already serialize), and the model field reference docs. Exact file paths are **unknown** from the issue.

## Commands

| Purpose | Command |
|---|---|
| Run tests | **Unknown.** Use the project's standard test runner. |
| Run relevant subset | **Unknown.** Expected to target model field tests, form field tests, and migration writer tests. |
| Lint | **Unknown.** |
| Build docs | **Unknown.** |

## Project Structure

Not visible from the issue. Expected (unverified) locations:
- Model field implementation: Django's model fields module, where `FilePathField` is defined.
- Tests: the existing test packages for model fields, form fields, and the migration writer.
- Docs: the model field reference page that documents `FilePathField.path`, plus the release notes for the target version.

Exact paths: **unknown**.

## Code Style

Follow existing Django conventions in the surrounding code. The intended public usage, taken from the issue and adapted:

```python
import os
from django.conf import settings
from django.db import models

def local_files_dir():
    return os.path.join(settings.LOCAL_FILE_DIR, 'example_dir')

class LocalFiles(models.Model):
    name = models.CharField(max_length=255)
    file = models.FilePathField(path=local_files_dir)
```

The implementation code style is **unknown** beyond "match existing Django style". No implementation snippet is specified here.

## Testing Strategy

- **Unit (model field):**
  - `formfield()` on a `FilePathField` with a callable `path` produces a form field whose `path` equals the callable's return value.
  - The callable is not invoked at field or model definition time. Assert this with a call-tracking callable, if feasible.
  - `deconstruct()` returns the callable object unchanged in `kwargs['path']`.
  - String `path` regression: `deconstruct()` and `formfield()` output are unchanged.
- **Migration serialization:** the migration writer serializes a field with a module-level callable `path` as an import reference, and the serialized output contains no absolute filesystem path.
- **Integration (forms):** a `ModelForm` over a model with callable `path` lists the files from the directory the callable returns, and honors `match` / `recursive` / `allow_files` / `allow_folders`.
- **Docs:** documentation builds without warnings (command unknown).
- Coverage: no explicit target known. Every acceptance criterion has at least one test.

## Boundaries

- **Always:**
  - Keep string `path` behavior fully backward compatible.
  - Add tests for every acceptance criterion.
  - Update the field docs and release notes.
  - Run the full relevant test subset before committing.
- **Ask first:**
  - Passing arguments to the callable (e.g. the model instance).
  - Changing `django.forms.FilePathField` to also accept callables.
  - Adding system checks for the callable's return value.
  - Changing migration serializer behavior.
- **Never:**
  - Resolve the callable at import or class-definition time.
  - Bake resolved absolute paths into `deconstruct()` output.
  - Add new dependencies.
  - Introduce DB schema changes.

## Success Criteria

- A model using `FilePathField(path=<module-level callable>)` produces a migration that references the callable by import path and contains no machine-specific absolute path.
- That migration applies identically on machines with different `LOCAL_FILE_DIR` values.
- Forms derived from the field list files from the callable's runtime return value.
- All existing `FilePathField` tests pass unchanged.
- The docs describe callable support with an example.

## Open Questions

1. Should the callable receive any arguments (e.g. the model instance, like `upload_to`), or be strictly zero-argument? The assumed answer is zero-argument.
2. Should the form-level `django.forms.FilePathField` also accept a callable, or only the model field?
3. When should the callable be resolved: on every `formfield()` call, or once and cached? Per-call resolution is assumed, to reflect settings changes.
4. Should a system check warn when `path` is a lambda or otherwise non-serializable callable, or is the migration writer's existing error enough?
5. Should path-like return values (`pathlib.Path`) be accepted and normalized to `str`?
6. Which Django version or branch does this target, and in which release notes section does the entry belong?
7. Are any other code paths reading `FilePathField.path` directly (e.g. admin, serializers, `check()`) that would need to handle a callable? This is unknown without repository access.