# Spec: Clear deferred fields correctly when `QuerySet.defer()` follows `QuerySet.only()`

## Assumptions

1. This is the Django ORM (`QuerySet.only()` / `QuerySet.defer()`). The project version is unknown.
2. The current semantics of `.only()` and `.defer()` must be preserved, and this fix only changes their interaction:
   - `.only(*fields)` restricts loading to the named fields plus the primary key.
   - `.defer(*fields)` excludes the named fields from loading.
   - The primary key is always loaded, even if deferred.
3. Root-cause hypothesis, not verified against source. The query appears to track loading as either:
   - an "immediate load" set (from `only()`), or
   - a "deferred" set (from `defer()`).

   When `defer()` removes every field from the `only()` set, the empty immediate set seems to be read as "no restriction". That would load all fields. The internal function names and data structures are unknown, because the repository is not visible.
4. The expected result when every `only()` field is later deferred is "load only the primary key". It is not "load everything" and it is not an error. This follows the issue reporter's stated expectation.
5. The `Company` model in the issue (`id`, `name`, `trade_number`, `country`) is illustrative. Tests may use an existing test model with an equivalent shape.
6. The behaviour should be the same on all database backends, since it concerns SQL column selection, not dialect.

## Objective

Make `QuerySet.only(...).defer(...)` produce a column selection consistent with applying the two operations in order. Removing every field named in `only()` via later `defer()` calls must leave only the primary key selected. It must not revert to selecting all columns.

**User:** developers using the Django ORM to limit which columns are fetched.

**Observed (bug):**

| Expression | Current SQL columns |
|---|---|
| `Company.objects.only("name").defer("name")` | id, name, trade_number, country |
| `Company.objects.only("name").defer("name").defer("country")` | id, name, trade_number, country |
| `Company.objects.only("name", "country").defer("name")` | id, country ✅ |

**Expected:**

| Expression | Expected SQL columns |
|---|---|
| `Company.objects.only("name").defer("name")` | id |
| `Company.objects.only("name").defer("name").defer("country")` | id |
| `Company.objects.only("name", "country").defer("name")` | id, country (unchanged) |

## Tech Stack

- Python and Django ORM (exact versions unknown).
- No new dependencies.

## Commands

All commands are unknown, because the repository is not visible.

- Build: unknown (likely none for a Python library)
- Test: unknown. Must be able to run the ORM's deferred-loading / `only()`/`defer()` test suite in isolation.
- Lint: unknown
- Dev: N/A

## Project Structure

Unknown. To be confirmed from the repository:

- **Code location:** where `QuerySet.only()` / `QuerySet.defer()` and the underlying query object's deferred-loading state live.
- **Test location:** where the existing tests for `defer()` / `only()` live.

## Code Style

- Follow the existing project conventions, which cannot be seen from here.
- Keep the change minimal and local to the deferred-loading state transition.
- Add no new public API.

## Testing Strategy

- **Level:** unit/integration tests at the QuerySet level. Assert which fields are deferred or selected, either by inspecting the generated SQL columns or via the existing assertion helpers in the defer test suite (unknown).
- **Regression tests (must fail before the fix, pass after):**
  1. `only("name").defer("name")` → only the pk is loaded.
  2. `only("name").defer("name").defer("country")` → only the pk is loaded.
  3. `only("name").defer("name", "country")` (single call) → only the pk is loaded.
- **Guard tests (must pass before and after):**
  4. `only("name", "country").defer("name")` → pk and `country`.
  5. `only("name").defer("trade_number")` → pk and `name`. Deferring a field not in the `only()` set has no effect.
  6. `defer("name").only("country")` → existing behaviour preserved. A later `only()` replaces earlier deferrals.
  7. Plain `defer(...)` and plain `only(...)` behaviour unchanged.
  8. `defer(None)` still clears all deferrals.
- **Instance check:** for regression case 1, loading an instance and then accessing `name` still works. It triggers a deferred load, consistent with existing deferred-field behaviour.
- Run the full existing defer/only test suite with no regressions.

## Boundaries

**Always**
- Add regression tests reproducing the issue's examples.
- Run the existing defer/only and query-related test suites.
- Preserve "the primary key is always loaded".

**Ask first**
- Changing behaviour of any `only`/`defer` combination other than "`defer()` empties the `only()` set".
- Changing internal data structures used by other code paths (e.g. `values()`, related-field traversal, `select_related`).
- Raising an error or warning instead of selecting only the pk.

**Never**
- Change public method signatures.
- Remove or weaken existing tests.
- Alter `defer(None)` semantics.

## Success Criteria

- `Company.objects.only("name").defer("name")` generates SQL selecting only the pk column.
- `Company.objects.only("name").defer("name").defer("country")` generates SQL selecting only the pk column.
- `Company.objects.only("name", "country").defer("name")` still selects only pk and `country`.
- All new regression tests pass, and all pre-existing tests in the relevant suites pass.
- Model instances from these querysets lazily load deferred fields on access, as with any deferred field.

## Open Questions

1. Is "select only the pk" definitely the desired result when `defer()` removes every `only()` field? The alternative is restoring "load all fields", which is the current behaviour and might be considered intentional. This spec assumes the former.
2. Should the fix also cover related-field lookups? For example, `only("fk__name").defer("fk__name")` together with `select_related`.
3. Which Django version or branch is targeted, and should the fix be backported?
4. What are the exact test command and test module for defer/only behaviour in this repository?
5. Should a release note or documentation update accompany the fix?