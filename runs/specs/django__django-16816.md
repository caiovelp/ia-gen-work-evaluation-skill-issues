# Spec: Admin system check E108 must flag `list_display` entries that fail at changelist render time

## Assumptions

1. The models follow the Django tutorial shape. `Choice` has a `ForeignKey` to `Question`, and `Question` has no field or attribute named `choice`. The reproduction is only linked ("see github"), so this is inferred.
2. `"choice"` therefore resolves through `Question._meta.get_field("choice")` to the **reverse** side of the FK, a one-to-many relation. The system check accepts this because the lookup succeeds. At render time, `_get_non_gfk_field` rejects reverse relations with `FieldDoesNotExist`, as the traceback shows. `label_for_field` then falls back to attribute lookup, finds nothing, and raises `AttributeError`.
3. The root cause is a mismatch. The check uses a looser definition of "valid field" than the runtime code in `django/contrib/admin/utils.py` (`label_for_field` / `_get_non_gfk_field`).
4. The fix belongs to Django itself (`django.contrib.admin` system checks), not to the reporter's project. The exact file holding the E108 check is not shown in the issue and is **unknown** here. It is presumably `django/contrib/admin/checks.py`.
5. Other relation kinds that `_get_non_gfk_field` rejects may have the same gap. Examples are reverse one-to-many relations reached through a `related_query_name`, and generic foreign keys. These are in scope only if they also pass the check and then crash at render time.
6. Many-to-many fields are already covered by a separate check (admin.E109). They are out of scope unless that check also misses reverse many-to-many relations.
7. The Django version is unknown. The traceback mentions Python list comprehensions (`<listcomp>`), which suggests Python ≤ 3.11 and a Django 4.x-era codebase.

## Objective

When a `ModelAdmin.list_display` entry cannot be rendered by the changelist, Django should report it at system-check time, through `manage.py check` or server startup. It should not let the changelist page fail with HTTP 500.

**User:** Django developers configuring `ModelAdmin.list_display`.

**User story:** As a developer, if I put the name of a reverse relation (e.g. `"choice"`) in `list_display`, I want `manage.py check` to report an error that explains the problem, instead of finding out from an `AttributeError: Unable to lookup 'choice' on Question or QuestionAdmin` when I open `/admin/polls/question/`.

**Success looks like:** Any `list_display` item that passes the system checks can be resolved by `label_for_field` without raising. Any item that `label_for_field` would reject is reported by a check.

## Tech Stack

- Python, with the version unknown (≤ 3.11 judging by the traceback).
- Django, with the version unknown.
- Components involved:
  - `django.contrib.admin` system checks (admin.E108, possibly admin.E109).
  - `django/contrib/admin/utils.py` (`label_for_field`, `_get_non_gfk_field`).
  - `django/contrib/admin/templatetags/admin_list.py` (`result_headers`).

## Commands

- Build: unknown (not given in the issue).
- Test: unknown. Django's own test-runner invocation is not shown in the issue.
- Lint: unknown.
- Reproduce (user project): `python manage.py check`, which currently reports no errors. Then `GET /admin/polls/question/`, which currently returns HTTP 500.

## Project Structure

Only paths visible in the traceback are listed:

```
django/contrib/admin/utils.py                    → label_for_field, _get_non_gfk_field (runtime lookup)
django/contrib/admin/templatetags/admin_list.py  → result_headers / result_list (changelist rendering)
django/core/exceptions.py                        → FieldDoesNotExist
```

- Location of the E108 check implementation: unknown (assumed `django/contrib/admin/checks.py`).
- Location of the relevant tests: unknown.
- Location of the system-check documentation listing E108: unknown.

## Code Style

Follow the existing conventions of the surrounding Django admin checks code. No snippet is available from the issue.

- Error messages should follow the existing E108 wording style. That style names the offending `list_display[n]` item, the value, and the model/admin class.
- Reuse existing check IDs. Do not invent new ones unless maintainers agree (see Open Questions).

## Testing Strategy

- Framework: Django's own test suite. The runner command and test locations are unknown.
- Test level: unit tests on `ModelAdmin.check()` output, plus a regression assertion that matches the runtime behaviour.
- Required cases:
  1. A `list_display` entry naming a **reverse FK relation** (e.g. `"choice"` on `QuestionAdmin`) produces a check error. Today it produces none.
  2. Existing valid entries produce **no new errors**. These include:
     - concrete fields;
     - forward FKs;
     - callables;
     - `ModelAdmin` methods;
     - model attributes/properties;
     - the `"__str__"` string;
     - `"field__related"` lookups, if the Django version in use supports them.
  3. Existing E108 cases (a name that is neither field nor attribute) still produce E108 with unchanged wording, unless wording changes are approved.
  4. Existing E109 (many-to-many) behaviour is unchanged.
  5. Consistency property: for each case in the tests, "check passes" ⇔ "`label_for_field` does not raise."
- Coverage expectations: every relation type that `_get_non_gfk_field` rejects has at least one check test.

## Boundaries

- **Always:**
  - Keep the check and the runtime lookup consistent.
  - Add regression tests for the reported case.
  - Preserve existing error IDs and messages for already-covered cases.
- **Ask first:**
  - Changing the text of E108 or E109.
  - Deciding whether reverse relations should be reported under E108 or E109, or under a new ID.
  - Changing runtime `list_display` behaviour, e.g. making reverse relations renderable.
  - Touching documentation for system checks or release notes.
- **Never:**
  - Turn currently valid `list_display` configurations into check errors.
  - Silence the runtime `AttributeError` as a way of "fixing" the issue.
  - Weaken existing checks.

## Success Criteria

1. With `Choice.question = ForeignKey(Question)` and `QuestionAdmin.list_display = ["choice"]`, the system checks report an admin error that identifies `list_display[0]` and the value `'choice'`.
2. No configuration that passes the admin system checks causes `label_for_field` to raise `AttributeError` for a reverse-relation `list_display` entry.
3. All previously valid `list_display` configurations still pass checks.
4. The existing E108/E109 tests still pass. New regression tests cover reverse FK relations.
5. Documentation for the affected check ID reflects the expanded coverage, if the wording changes.

## Open Questions

1. **Which check ID should report reverse relations?**
   - E108 ("refers to X, which is not a callable, an attribute of …, or an attribute or method on …").
   - E109 ("must not be a ManyToManyField"), with its message broadened to "many-to-many field or reverse foreign key".
   - A new ID.
2. Should **reverse one-to-one** and **reverse many-to-many** relations be covered too? Is their runtime behaviour actually broken? This needs verification against `_get_non_gfk_field`.
3. Are **generic foreign keys** (`GenericForeignKey`) in `list_display` affected the same way, or are they handled by attribute fallback?
4. If the related model defines `related_query_name` or `related_name`, should the check consider the query name, the accessor name, or both? For example, `"choice_set"` would succeed via attribute lookup and must not be flagged.
5. Which Django version(s) should the fix target? Is backporting expected?
6. Exact paths of the check implementation, its tests, and the system-check docs are unknown from the issue. They need confirmation.
7. The linked GitHub reproduction was not available. Does it match Assumption 1, or does `"choice"` refer to something else?