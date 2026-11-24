# Spec: translation.E004 Accepts a Sublanguage When Its Base Language Is Available

## Objective

When `LANGUAGE_CODE` is a sublanguage such as `de-at`, Django's system check framework raises `translation.E004` ("You have provided a value for the LANGUAGE_CODE setting that is not in the LANGUAGES setting") even when the base language (`de`) is in `LANGUAGES`. This contradicts Django's documented fallback behavior:

> If a base language is available but the sublanguage specified is not, Django uses the base language. For example, if a user specifies de-at (Austrian German) but Django only has de available, Django uses de.

**Observed (Django 3.0.2):**
- `LANGUAGE_CODE = "de-at"` fails with `SystemCheckError` / `translation.E004`.
- `LANGUAGE_CODE = "es-ar"` works, because `es-ar` is itself in the default `LANGUAGES`.

**Goal:** Make the E004 consistency check agree with the runtime language-resolution rules. E004 should fire only when Django could not actually resolve `LANGUAGE_CODE` to an entry in `LANGUAGES`.

**Users:** Django project developers who set a regional `LANGUAGE_CODE` for which only the base language is listed in `LANGUAGES`.

### Acceptance criteria / user stories
- As a developer, I can set `LANGUAGE_CODE = "de-at"` while `LANGUAGES` contains `de` but not `de-at`, and the system checks pass.
- As a developer, if I set a `LANGUAGE_CODE` whose exact value and base language are both missing from `LANGUAGES`, I still get `translation.E004`.

## Assumptions

1. The bug is in the system check that emits `translation.E004`, not in runtime language selection. The issue implies runtime fallback already works as documented.
2. "Base language" means the part of the code before the first `-`, as in the documented example (`de-at` → `de`).
3. The check should apply the same resolution rules Django uses at runtime when picking a supported language variant. It should not implement a separate, divergent rule.
4. Behavior applies both with the default `LANGUAGES` and with a user-defined `LANGUAGES`.
5. The fix targets the main development branch. Backporting to 3.0.x is a release-policy decision, not part of this spec.
6. No change to the E004 message text, ID, or severity is required.
7. Other translation checks (E001–E003) are out of scope.

## Tech Stack

- Python / Django. The target branch and its minimum Python version are **unknown** from the issue.
- Components involved: Django system checks framework and translation/i18n utilities. The exact module locations are **unknown** from the issue and must be confirmed in the repository.

## Commands

Unknown. The issue doesn't specify how to run the Django test suite in this environment. To be filled in after inspecting the repository:
- Test: *unknown*
- Lint: *unknown*

## Project Structure

Unknown. These are to be confirmed in the repository:
- Location of the module defining the `translation.E004` check.
- Location of the existing tests for translation system checks.
- Location of the documentation for system checks (E004 description) and for language fallback.

## Code Style

Follow the existing Django codebase conventions, which are not visible from the issue. The change should reuse existing i18n resolution helpers rather than duplicating language-matching logic in the check.

## Testing Strategy

- **Level:** unit tests for the system check, alongside the existing translation check tests (location unknown).
- **Cases to cover:**
  1. `LANGUAGE_CODE="de-at"` with `LANGUAGES` containing `de` only: no errors.
  2. `LANGUAGE_CODE="es-ar"` with `LANGUAGES` containing `es-ar`: no errors (regression guard for exact match).
  3. `LANGUAGE_CODE` that is a sublanguage whose base is also absent from `LANGUAGES` (e.g. `fr-ca` with only `de`): E004 is raised.
  4. `LANGUAGE_CODE` that is a plain language absent from `LANGUAGES`: E004 is still raised.
  5. Existing E004 tests continue to pass unchanged.
- Tests must override `LANGUAGE_CODE` and `LANGUAGES` explicitly so they don't depend on global defaults.

## Boundaries

- **Always:**
  - Keep the check consistent with documented runtime fallback.
  - Add regression tests for the reported case.
  - Run the existing check and i18n test suites.
- **Ask first:**
  - Changing E004's message, ID, or severity.
  - Changing runtime language-resolution behavior.
  - Updating documentation wording.
  - Backporting.
- **Never:**
  - Silence E004 entirely.
  - Hard-code specific language codes in the check.
  - Remove or weaken existing E004 tests.

## Success Criteria

- With `LANGUAGES` containing `de` but not `de-at`, `LANGUAGE_CODE="de-at"` yields zero system check errors.
- A `LANGUAGE_CODE` that resolves to neither an exact nor a base-language entry in `LANGUAGES` still yields exactly one `translation.E004`.
- All new and existing translation check tests pass.

## Open Questions

1. Should the check use the full runtime resolution logic, or only exact-match plus base-language fallback? The runtime logic may also consider other variants and installed locale files. Which behavior is intended for the check?
2. Should the fallback also cover codes with script/region subtags such as `zh-hant-hk` or `sr-latn`? What counts as "base" for multi-part codes?
3. Should the check be case-insensitive (e.g. `de-AT` vs `de-at`), matching runtime behavior?
4. Should the E004 documentation (and possibly the message) be clarified to say that a base-language fallback is accepted?
5. Is a backport to the 3.0.x series desired?
6. What are the exact commands and paths for running the relevant test suites in this repository?