# Spec: Make `ManyToManyRel.identity` hashable when `through_fields` is a list

## Objective

**Problem.** Since Django 3.2, every `ForeignObjectRel` has an `identity` property, which is a tuple. `ForeignObjectRel.__hash__` returns `hash(self.identity)`. The base identity already passes `limit_choices_to` through `make_hashable`. `ManyToManyRel` adds `through_fields` to its identity without that call. Users may legally pass `through_fields` as a list, for example `through_fields=['child', 'parent']`. In that case hashing the rel fails with:

```
TypeError: unhashable type: 'list'
```

The issue's traceback shows the failure inside `Model._check_field_name_clashes` (`if f not in used_fields:`) while system checks run (`manage.py` → `check()` → `check_all_models`). According to the reporter it shows up only when a proxy model of the M2M target exists. The reporter's guess about why is unverified.

**Users.**
- Django developers who declare `ManyToManyField(..., through=..., through_fields=[...])` with a list.
- Any code path that hashes or compares `ManyToManyRel` objects.

**Goal.**
- A `ManyToManyRel` whose `through_fields` is a list hashes without error.
- System checks pass for the reporter's minimal reproduction.
- Equality and hash semantics for rels stay consistent: equal identities give equal hashes.

**Acceptance criteria / user stories.**
1. As a developer, when I declare `through_fields` as a list and have a proxy model of the target model, `manage.py check` (and any command that runs checks) finishes without `TypeError`.
2. As a developer, `hash(field.remote_field)` works for an M2M rel whether `through_fields` is a list, a tuple, or `None`.
3. Two `ManyToManyRel` instances that differ only in `through_fields` container type (list vs. tuple with the same items) compare as described in the Open Questions decision. Whatever that decision is, `__eq__` and `__hash__` agree.

## Tech Stack

- Python and Django. The issue names Django 3.2 as the version that introduced `identity`, and the traceback was produced on Python 3.8.
- The affected code is `django/db/models/fields/reverse_related.py`, which the traceback names. It contains `ForeignObjectRel.identity`, `ForeignObjectRel.__hash__`, and `ManyToManyRel.identity`.
- The fix relies on the existing helper `make_hashable`. The issue says the base identity already uses it, but its import location is not shown in the issue (unknown).

## Commands

All commands are unknown because they are not given in the issue:
- Build: unknown (pure Python; likely none)
- Test: unknown (Django's own test runner invocation and the test module to run are not shown)
- Lint: unknown
- Reproduce: `python manage.py check` in a project containing the reproduction models below (from the issue's traceback)

## Project Structure

Known from the traceback:
```
django/db/models/fields/reverse_related.py → ForeignObjectRel / ManyToManyRel, identity, __hash__ (the fix location)
django/db/models/base.py                   → Model.check, _check_field_name_clashes (where the hash is triggered)
django/core/checks/model_checks.py         → check_all_models
```
The location of the regression tests is unknown, for example which test app or module covers M2M through models or model checks.

## Code Style

- Follow the existing pattern in the base `ForeignObjectRel.identity`, which wraps `limit_choices_to` in `make_hashable(...)`.
- Apply the same wrapping to `through_fields` in `ManyToManyRel.identity`.
- Do not introduce new helpers.
- Exact surrounding code is not visible in the issue, so no snippet is reproduced here.

## Testing Strategy

- **Regression test (model checks level).** Define the reporter's models in an isolated test app:
  - `Parent`
  - proxy `ProxyParent`
  - `Child` with `ManyToManyField(to=Parent, through="ManyToManyModel", through_fields=['child', 'parent'], related_name="something")`
  - `ManyToManyModel` with FKs `parent`, `child`, `second_child`

  Run model checks and assert no exception is raised and no errors are reported.
- **Unit level.** Assert `hash(<ManyToManyRel with list through_fields>)` does not raise. Also assert that it equals the hash of an equal rel built the same way.
- **Before/after.** The new test must fail with `TypeError: unhashable type: 'list'` before the change and pass after it.
- **Full suite.** The existing tests for reverse-related fields, M2M through models, and model checks must still pass. The exact test labels are unknown.
- Coverage targets are unknown.

## Boundaries

- **Always:**
  - Keep `__eq__` and `__hash__` derived from the same `identity`.
  - Add a regression test reproducing the reported crash.
  - Keep the change confined to `ManyToManyRel.identity` unless investigation shows other identity elements have the same defect.
- **Ask first:**
  - Normalizing `through_fields` to a tuple at construction time instead of in `identity`, since that changes a public attribute's type.
  - Auditing or changing identity elements of other rel classes (`ManyToOneRel`, `OneToOneRel`, `ForeignObjectRel`).
  - Backporting to stable branches.
- **Never:**
  - Change the order or meaning of identity tuple elements.
  - Make `__hash__` ignore fields to dodge the error.
  - Alter `_check_field_name_clashes` or the checks framework to avoid hashing.
  - Weaken or remove existing tests.

## Success Criteria

1. With the reporter's minimal models, running system checks raises no `TypeError` and reports no errors attributable to this field.
2. `hash()` succeeds on `ManyToManyRel` for `through_fields` given as a list, a tuple, or `None`.
3. For any two rels `a` and `b`, `a == b` implies `hash(a) == hash(b)`.
4. A new regression test exists, fails on the unpatched code, and passes on the patched code.
5. The existing test suite shows no regressions.

## Assumptions

1. `ManyToManyRel.identity` currently appends `self.through_fields` raw. The issue states this but the code is not visible.
2. `make_hashable` converts lists to tuples, and is the same helper already used for `limit_choices_to`.
3. The bug affects any code path that hashes the rel. The proxy-model condition is only what triggers hashing during checks in the reporter's setup.
4. The target is the Django version line containing the 3.2 `identity` change; the main development branch is assumed.
5. `through_fields` given as a tuple or `None` already hashes correctly and must keep doing so.

## Open Questions

1. Should a list `through_fields` and an equal tuple `through_fields` produce equal identities? Using `make_hashable` implies yes, since both become tuples. Is that acceptable?
2. Why does the failure occur only with a proxy model present? Should the root cause be confirmed and documented in the test, or is the hashability fix sufficient?
3. Are other elements of any rel's `identity` (for example `related_name`, `related_query_name`, `through`) potentially unhashable user input and in scope?
4. Which stable branches, if any, should receive a backport, and is a release note required?
5. Where should the regression test live, and what is the exact test command? Both are unknown from the issue.