# Spec: Derive Admin Inline `verbose_name_plural` from Inline `verbose_name`

## Assumptions

1. This change targets the Django framework itself, specifically the admin `InlineModelAdmin` class and its subclasses (`TabularInline`, `StackedInline`). It does not target a project that uses Django.
2. Today, when `verbose_name_plural` is not set on an inline, it falls back to the related model's `Meta.verbose_name_plural`. That value is either explicit or auto-derived from the model's `verbose_name`. The fallback ignores the inline's own `verbose_name`.
3. The pluralization rule should match the one `Model._meta` uses when deriving `verbose_name_plural` from `verbose_name`. The issue describes that rule as "automatically base the plural form on a specified verbose_name". The exact mechanism, presumably appending "s" lazily, has not been checked against the source.
4. `verbose_name` may be a lazy translation object. The derived plural must stay lazy and must not be forced to a string at class-definition time.
5. An explicitly set inline `verbose_name_plural` always wins and stays unchanged.
6. When the inline sets neither attribute, behaviour stays exactly as it is today.
7. This is a user-visible behaviour change and needs a release note and documentation update. It is a new feature, not a bug fix.
8. The reporter's patch, mentioned in the issue, is not available to me. This spec is written independently of it.

## Objective

**Problem:** A developer who overrides an inline's display name has to set both `verbose_name` and `verbose_name_plural`. If they set only `verbose_name`, the plural shown in the admin, such as the inline fieldset heading, still comes from the model's name. The result looks inconsistent. Model `Meta` does not behave this way: setting `verbose_name` there automatically produces a matching plural.

**User:** Django developers who configure admin inlines.

**Goal:** If an inline sets `verbose_name` but not `verbose_name_plural`, derive `verbose_name_plural` from the inline's `verbose_name`, using the same rule model `Meta` uses.

**Behaviour matrix (proposed):**

| Inline `verbose_name` | Inline `verbose_name_plural` | Resulting inline `verbose_name_plural` |
|---|---|---|
| not set | not set | Model `Meta.verbose_name_plural` (unchanged) |
| not set | set | Inline's explicit value (unchanged) |
| set | set | Inline's explicit value (unchanged) |
| set | not set | **Derived from the inline's `verbose_name`** (new) |

Whether the last row should apply when the model `Meta` defines an explicit `verbose_name_plural` is listed under Open Questions.

## Tech Stack

- Python and Django. The supported versions and the target release for this feature are unknown.
- Component: `django.contrib.admin`, specifically `InlineModelAdmin`. The defining module is unknown from the issue and has not been verified.
- Translation utilities for lazy strings. The specific helper is unknown and has not been verified.

## Commands

The issue does not state any commands. All are unknown:

- Build: unknown (likely none, since Django is a pure Python package)
- Test: unknown (Django's own test runner invocation is not given in the issue)
- Lint: unknown
- Docs build: unknown

## Project Structure

The issue does not state any paths. All are unknown and need to be confirmed against the repository:

- Implementation of `InlineModelAdmin`: unknown
- Admin inline tests: unknown
- Admin docs describing `InlineModelAdmin.verbose_name` and `InlineModelAdmin.verbose_name_plural`: unknown
- Release notes for the target version: unknown

## Code Style

- Follow the existing Django coding style and the conventions of the surrounding admin code. No snippet is available from the issue.
- Mirror the pluralization logic and the lazy-string handling that model `Options` already uses, rather than introducing a new rule.

## Testing Strategy

- Framework: Django's own test suite. The location and runner command are unknown.
- Required test cases (one per row of the behaviour matrix, plus edge cases):
  1. Inline sets only `verbose_name`: rendered and computed `verbose_name_plural` is derived from it.
  2. Inline sets both: the explicit plural is used.
  3. Inline sets only `verbose_name_plural`: the explicit plural is used.
  4. Inline sets neither: the model `Meta` plural is used, as today.
  5. Inline sets only `verbose_name` as a lazy translation: the derived plural is still lazy and translates under an active language.
  6. Both tabular and stacked inlines render the derived plural in the admin change form (heading and any other place the plural appears).
  7. The case from Open Question 1: the model has an explicit `Meta.verbose_name_plural` and the inline sets only `verbose_name`.
- Levels: unit-level checks on the inline instance attributes, plus admin view or rendering tests confirming the heading text.

## Boundaries

- **Always:**
  - Preserve explicit inline `verbose_name_plural` values.
  - Keep lazy translations lazy.
  - Add tests for every row of the behaviour matrix.
  - Update the docs and add a release note.
- **Ask first:**
  - Changing the precedence between the model's explicit `Meta.verbose_name_plural` and the inline's `verbose_name`.
  - Adding any deprecation path.
  - Backporting the change to stable branches.
  - Changing the pluralization rule.
- **Never:**
  - Change model `Meta` behaviour.
  - Alter the inline `verbose_name` fallback.
  - Force-evaluate lazy strings at import or class-definition time.
  - Break existing inlines that set neither attribute.

## Success Criteria

- [ ] An inline with only `verbose_name = "Foo"` produces `verbose_name_plural` equal to what model `Meta` would derive from `"Foo"`, and the admin change form shows that plural.
- [ ] Inlines that set `verbose_name_plural` explicitly behave exactly as before.
- [ ] Inlines that set neither attribute behave exactly as before.
- [ ] A lazy `verbose_name` produces a lazy plural that renders correctly translated.
- [ ] Both `TabularInline` and `StackedInline` reflect the new behaviour.
- [ ] Documentation for `InlineModelAdmin.verbose_name_plural` describes the new default.
- [ ] A release note records the behaviour change.
- [ ] The existing admin test suite passes.

## Open Questions

1. **Precedence with model `Meta`:** Suppose the related model defines an explicit `Meta.verbose_name_plural` and the inline sets only `verbose_name`. Should the plural come from the inline's `verbose_name` (new behaviour) or from the model's explicit plural (current behaviour)? The issue implies the former, but this needs confirmation.
2. **Backwards compatibility:** Existing projects that set only an inline `verbose_name` will see different headings after upgrading. Is a release-note mention enough, or is a deprecation period or opt-in needed?
3. **Target release:** Which Django version should receive this? Is it a feature for the next major release only?
4. **Pluralization rule:** Should the derived plural use exactly the same mechanism as model `Meta`? Is that mechanism confirmed to be appending "s" via a lazy format?
5. **Reporter's patch:** Should the existing patch from the issue author be reviewed and adopted as the basis for implementation?
6. **Other plural usages:** Are there other places in the admin where the inline plural is computed or displayed (for example, "Add another …" labels, JavaScript-side strings, or checks) that also need verifying?
7. **Repository specifics:** What are the file paths, test locations, and test, lint, and docs commands? None of them appear in the issue.