# Spec: Fix false-positive `templates.E003` when a tag library is also listed in `TEMPLATES['OPTIONS']['libraries']`

## Objective

The system check `check_for_template_tags_with_the_same_name` reports `templates.E003` when one template tag module is reachable two ways under the same name:

1. Through `TEMPLATES[...]['OPTIONS']['libraries']`.
2. Through auto-discovery of an installed app's `templatetags` package.

The error lists the same module path twice:

```
(templates.E003) 'my_tags' is used for multiple template tag modules:
'someapp.templatetags.my_tags', 'someapp.templatetags.my_tags'
```

This is a false positive. E003 exists to catch a name that maps to *different* modules, because only one of them can win at load time. A module registered under the same name more than once is not a conflict.

**Who is affected:** Django project developers who list app tag libraries in `TEMPLATES['OPTIONS']['libraries']`. This could be for explicit naming, or for libraries that apps already expose.

**Goal:**
- E003 fires only when one library name maps to two or more distinct module paths.
- Duplicate registrations of the same name → same module do not trigger E003.

### Acceptance criteria

- **AC1:** No E003 when a library name maps to the same module path through both `OPTIONS['libraries']` and app auto-discovery.
- **AC2:** No E003 when the same name/module pair appears in `OPTIONS['libraries']` of more than one `TEMPLATES` entry.
- **AC3:** E003 is still raised when one name maps to two different module paths. This covers:
  - two apps' `templatetags` packages;
  - a `libraries` entry plus an app module;
  - two `libraries` entries in different `TEMPLATES` backends.
- **AC4:** When E003 is raised, each distinct conflicting module path appears exactly once in the message.
- **AC5:** Existing behaviour and message format for genuine conflicts are otherwise unchanged.

## Assumptions

1. This is the Django framework codebase. The check lives in Django's template system checks module (believed to be `django/core/checks/templates.py`; not verified against the repo).
2. The check builds a mapping of library name → module paths. It gathers paths from each `TEMPLATES` entry's `OPTIONS['libraries']` and from app tag discovery (believed to be `get_template_tag_modules()`). It then flags any name with more than one entry. The suspected root cause is that this mapping counts duplicates rather than distinct paths. This is inferred from the error text, not verified.
3. The issue's typo `librairies` means the correct key `libraries`.
4. The fix should not change the error id (`templates.E003`), its severity, or its message wording.
5. Ordering of module paths in the E003 message may matter to existing tests. Deterministic ordering should be preserved, e.g. first-seen order.
6. This is a bug fix and may be eligible for backport. Which branches is the maintainers' decision.

## Tech Stack

- Python and Django. The exact supported versions for the target branch are unknown.
- Django's system checks framework (`django.core.checks`).
- Django template engine (`DjangoTemplates` backend, `OPTIONS['libraries']`).

## Commands

Unknown. They cannot be confirmed without repository access. Likely candidates to confirm:

- Test runner: Django's own test runner from `tests/`, e.g. `./runtests.py check_framework`.
  - Unverified; the exact invocation and the test label are unknown.
- Lint/format: unknown. The project likely uses its configured linters, but this is not verified.

## Project Structure

Unknown and unverified. Believed relevant locations:

- Template system checks source: likely `django/core/checks/templates.py`.
- Tag module discovery: likely in `django/template/backends/django.py`.
- Tests for template checks: likely under `tests/check_framework/` (e.g. a `test_templates.py`), with fixture apps containing `templatetags` packages.

## Code Style

Follow existing Django conventions in the surrounding module and tests. No snippet is available from the issue. Expectations:

- Match the existing message construction for E003.
- Keep the change minimal and localized to the check.

## Testing Strategy

- **Framework:** Django's test suite (`unittest`-based `SimpleTestCase`), using `override_settings` for `TEMPLATES` and `INSTALLED_APPS`.
- **Level:** unit tests of the check function, invoked directly and asserting on the returned list of errors.
- **New tests (regression):**
  - Same module registered via `OPTIONS['libraries']` and app auto-discovery under the same name → `[]` (AC1).
  - Same name/module in `libraries` of two `TEMPLATES` entries → `[]` (AC2).
- **Existing/extended tests:**
  - Different modules under the same name, via each source combination → one E003 per conflicting name (AC3).
  - Message lists each distinct path once (AC4).
- All existing template check tests must still pass (AC5).

## Boundaries

**Always:**
- Add a regression test reproducing the issue before or alongside the fix.
- Keep the E003 id, severity, and message format.
- Run the template checks test module.

**Ask first:**
- Changing the E003 message wording or path ordering.
- Changing which sources the check inspects.
- Touching the template engine's library loading/resolution logic rather than the check.
- Adding a release note or backport target.

**Never:**
- Silence E003 globally.
- Treat different modules sharing a name as acceptable.
- Delete or weaken existing conflict tests.

## Success Criteria

- A project with `someapp` in `INSTALLED_APPS` and `TEMPLATES[0]['OPTIONS']['libraries'] = {'my_tags': 'someapp.templatetags.my_tags'}` produces no `templates.E003` from `manage.py check`.
- Genuine name conflicts across distinct modules still produce `templates.E003`, listing each distinct module path once.
- New regression tests fail before the fix and pass after it.
- The existing template check test suite passes.

## Open Questions

1. Should a name mapped to the same module under multiple `TEMPLATES` backends also be exempt (AC2)? This is assumed yes.
2. Should module paths in the E003 message be deduplicated while preserving first-seen order, or sorted? Existing tests may depend on the current order.
3. Should paths be normalized before comparison, or is exact string comparison sufficient? An example would be a library pointing to a re-exporting module vs. the original. Exact string comparison is assumed.
4. Which Django branches should receive the fix, and is a release note required?
5. Can the reporter confirm the exact configuration, i.e. the `libraries` key and value plus `INSTALLED_APPS`, to rule out a different cause?