# Spec: System Check for Fields Referenced by `UniqueConstraint`

## Assumptions

1. The project is **Django**, and the issue concerns the model system checks framework (`models.E012` is a Django system check ID).
2. "makemigrations doesn't check" means the **system checks** that run before management commands such as `makemigrations` and `check` do not validate `UniqueConstraint.fields`. The fix belongs in model checks, not in the migration autodetector.
3. The desired behavior is **parity with `unique_together`**: the same validations and the same error IDs (`models.E012`, plus related IDs that `unique_together` already emits).
4. `unique_together` already emits these checks, as I recall from Django:
   - `models.E012`: field does not exist.
   - `models.E013`: ManyToMany field referenced.
   - `models.E016`: field not local to the model, for example an inherited field from multi-table inheritance.

   Reusing the existing field-validation helper is assumed to be the intended approach. **This is unverified because I have no repository access.**
5. Only `UniqueConstraint.fields` is in scope. `CheckConstraint` has no `fields` attribute, and expression-based constraints are out of scope.
6. Constraints are read from `Meta.constraints`.
7. The error message should name the option as `'constraints'`, in the same style as the `'unique_together'` message, e.g. `"'constraints' refers to the nonexistent field 'foo'."`.
8. No new check ID is needed. E012, E013 and E016 are reused.
9. The checks run once per model class. Abstract models follow the same rules `unique_together` already follows.

→ These are recorded here instead of being confirmed with a human. See Open Questions.

## Objective

When a model declares `Meta.constraints = [UniqueConstraint(fields=[...], name=...)]` and one of the named fields does not exist on the model, Django's system checks currently pass silently. The error only surfaces later, for example when the migration is applied or at DB level, or not at all.

The older `unique_together` option reports this case immediately as `models.E012`. This feature brings `UniqueConstraint.fields` to parity, so developers get an early, actionable error when running `makemigrations`, `check`, or any command that runs system checks.

**Users:** Django developers who define models with `UniqueConstraint`.

**Acceptance criteria (user-story form):**
- As a developer, if I typo a field name in a `UniqueConstraint`, `manage.py makemigrations` and `manage.py check` report `models.E012` pointing at my model.
- As a developer, if my `UniqueConstraint` references valid local concrete fields, no new errors appear.

## Tech Stack

- Python / Django: exact supported versions **unknown**.
- Django system checks framework (`django.core.checks`): `Error` objects with `obj` and `id`.
- Relevant classes: `django.db.models.UniqueConstraint` and model `Meta.constraints`.

## Commands

- **Build:** unknown (none needed for a Python library change).
- **Test:** unknown. Django typically uses `tests/runtests.py <test_label>`, but the exact invocation and test labels are not visible from the issue.
- **Lint:** unknown (likely flake8/isort per Django contributor docs; not verified).
- **Reproduce:**
  - `python manage.py makemigrations` against the attached demo project. Its contents are not available.
  - Per the reporter, uncomment `"with_unique_together"` in the demo's `settings.py` to see E012 raised for `unique_together`.

## Project Structure

Unknown; no repository access. Expected locations, **to be confirmed**:
- Model check logic: the model base class's `check()` / `_check_*` classmethods (believed to be in `django/db/models/base.py`).
- Check tests: Django's invalid-models / model-checks test suite (believed to be `tests/invalid_models_tests/`).
- Docs: the system checks reference listing `models.E012` (believed to be `docs/ref/checks.txt`), plus release notes.

## Code Style

- Follow existing Django conventions in the check code.
- Errors are `checks.Error(msg, obj=cls, id='models.E0xx')`.
- Messages use the existing quote style, e.g. `"'%s' refers to the nonexistent field '%s'."`.
- Reuse the existing helper that validates `unique_together` / `index_together` / `indexes` field lists rather than duplicating logic.
- The exact helper name and signature are unknown; do not invent them.

## Testing Strategy

- **Level:** unit tests of model system checks. Define a model in the test, then assert `Model.check()` returns the exact expected list of `Error` objects, including message, `obj` and `id`.
- **Location:** alongside existing `unique_together` / `Meta.constraints` check tests (exact file unknown).
- **Cases required:**
  1. `UniqueConstraint(fields=['missing_field'])` → exactly one `models.E012` whose message references `'constraints'` and `missing_field`.
  2. `UniqueConstraint` referencing a ManyToMany field → `models.E013` (if parity with `unique_together` is confirmed).
  3. `UniqueConstraint` referencing a field inherited from a multi-table parent → `models.E016` (if parity is confirmed).
  4. `UniqueConstraint` referencing valid local fields → no errors.
  5. `CheckConstraint` on the same model → unaffected; no field check performed.
  6. Existing `unique_together` E012 tests continue to pass unchanged.
- **Coverage:** every new branch is exercised; no regression in the existing check suite.

## Boundaries

- **Always:**
  - Reuse existing field-validation logic and error IDs.
  - Add tests for each error path and the happy path.
  - Document the new behavior under the existing check IDs and in release notes.
- **Ask first:**
  - Introducing a new check ID instead of reusing E012/E013/E016.
  - Changing message wording for existing `unique_together` errors.
  - Validating `UniqueConstraint.condition` or expression-based constraints.
  - Making changes in the migration autodetector.
- **Never:**
  - Change the semantics of `unique_together` checks.
  - Raise exceptions instead of returning `checks.Error`.
  - Silence or remove existing failing tests.
  - Alter DB schema generation behavior.

## Success Criteria

- [ ] A model whose `UniqueConstraint.fields` contains a nonexistent field causes `Model.check()` (and therefore `makemigrations` / `check`) to return `models.E012` with `obj` set to the model class.
- [ ] The E012 message identifies the option (`'constraints'`) and the offending field name.
- [ ] ManyToMany and non-local field references produce the same error IDs as `unique_together` does (pending confirmation of the parity scope).
- [ ] Valid `UniqueConstraint` definitions and all `CheckConstraint` definitions produce no new errors.
- [ ] The reporter's demo project now reports E012 for the `UniqueConstraint` case without needing the `with_unique_together` toggle.
- [ ] All existing model-check tests pass.
- [ ] `models.E012` (and E013/E016 if extended) documentation mentions `constraints` alongside `unique_together`/`index_together`.

## Open Questions

1. Should the check cover only nonexistent fields (E012, as the issue literally asks), or full parity with `unique_together` (E013 ManyToMany, E016 non-local fields)?
2. Is reusing E012 acceptable, or is a distinct check ID preferred for constraints?
3. What exact message wording is wanted? Is `"'constraints' refers to the nonexistent field '…'"` acceptable?
4. Should field names in `UniqueConstraint.condition` (Q objects) also be validated? This is assumed out of scope.
5. Which Django version(s) should receive this (main only vs. backport)?
6. What are the exact test command, test module, and file locations? Repository access is needed to confirm.
7. What does the attached demonstration contain? It is not available; it is needed only to confirm the reproduction.