# Spec: Consistent `QuerySet.delete()` Return Value When Zero Objects Are Deleted

## Assumptions

1. The issue refers to Django's ORM `QuerySet.delete()`, written lowercase in code. The issue's "QuerySet.Delete" is a capitalization of that method.
2. The return contract is the documented 2-tuple `(total_deleted, per_model_counts)`. `per_model_counts` maps `Model._meta.label` to an integer count.
3. The difference comes from two internal deletion code paths:
   - a "fast delete" path for models with no cascades, signals or related objects to collect;
   - a "collect then delete" path for models with foreign key relations or cascades.

   I have not seen this code. It is inferred from the symptoms.
4. Only the zero-deletion case is inconsistent. When at least one object is deleted, the current output is correct and must not change.
5. `Model.delete()` (instance-level) probably shares the same machinery, so it may be affected too. Its behaviour must stay correct and consistent after the change.
6. The fix should not change which rows are deleted, the order of deletion, signal dispatch or the SQL queries run. It should change only the returned counts dictionary.
7. Which consistent form to adopt ("empty dict" or "zero-valued keys") is not yet decided. See Open Questions. The success criteria hold for either choice, and the chosen option goes into the spec once decided.

## Objective

Make `QuerySet.delete()` return the same shape of result when nothing is deleted, whatever the model's relationships are.

**Who is affected:** developers who inspect the return value of `QuerySet.delete()`, for example for logging, auditing or assertions in tests. Today they have to handle two different zero-result shapes depending on the model's foreign key structure.

**Current behaviour (from the issue):**

| Scenario | Current result |
|---|---|
| Objects deleted (any model) | `(2, {'my_app.FileAccess': 1, 'my_app.File': 1})` |
| Zero deleted, model with foreign keys / related objects | `(0, {})` |
| Zero deleted, "simple" model without foreign keys | `(0, {'my_app.BlockLibrary': 0})` |

**Desired behaviour:** the two zero-deletion cases return the same form. That form is either:

- **Option A:** `(0, {})` in both cases, meaning only models with at least one deleted row appear as keys; or
- **Option B:** `(0, {'<app_label>.<Model>': 0, ...})` in both cases, meaning the queried model (and possibly the related models considered) appear with zero counts.

The non-zero case must keep its current format and values.

## Tech Stack

- Python, Django ORM (versions: **unknown**, not stated in the issue)
- Database backends affected: **unknown**. Assumed to be backend-independent, because the inconsistency is in result assembly and not in SQL.

## Commands

- Build: **unknown**
- Test: **unknown** (the project's test runner command and flags are not visible from the issue)
- Lint: **unknown**
- Dev: not applicable

## Project Structure

**Unknown.** No repository access. The relevant areas, by responsibility only:

- the `QuerySet.delete()` implementation;
- the deletion "collector" logic that handles cascades and fast deletes;
- the existing tests for deletion behaviour and return values;
- the documentation describing `QuerySet.delete()` / `Model.delete()` return values, and release notes.

Exact file paths are to be confirmed against the repository.

## Code Style

**Unknown.** Follow the existing conventions of the surrounding ORM deletion code and its test suite. No snippet is available from the issue.

## Testing Strategy

- **Framework / location:** unknown. Use the project's existing test suite for deletion behaviour.
- **Regression tests (required), each asserting the full return tuple:**
  1. Zero matches on a model **without** foreign keys or relations (the fast-delete path).
  2. Zero matches on a model **with** foreign keys / reverse relations (the collector path).
  3. Zero matches on a model whose relations would normally cascade.
  4. Delete on an empty table compared with delete on a filter that matches nothing. Both must give the same result.
  5. Tests 1 and 2 must give results of the same shape: both `{}` under Option A, or both with zero-valued label keys under Option B.
- **Non-regression tests:**
  - Existing tests covering non-zero deletions, including cascades, still pass unchanged.
  - Cases with mixed cascade counts, where some related models have zero deletions, behave as the chosen option specifies.
  - `Model.delete()` on a single instance still returns the correct counts.
- **Test levels:** unit/integration tests against the test database. No end-to-end tests are needed.

## Boundaries

- **Always:**
  - Keep the `(int, dict)` tuple type.
  - Keep `_meta.label` as the dictionary key format.
  - Keep the total equal to the sum of the dict values.
  - Add regression tests for both code paths.
  - Update the documentation if the documented zero-case behaviour changes.
- **Ask first:**
  - Choosing between Option A and Option B.
  - Any change to the non-zero result format.
  - Any change to which models appear in the dict when some cascaded models delete zero rows.
  - Adding a release note or deprecation note.
- **Never:**
  - Change which rows are deleted, the deletion order, signal behaviour or the number or shape of SQL queries, beyond what the fix strictly needs.
  - Remove or loosen existing deletion tests.
  - Add new dependencies.

## Success Criteria

1. For any model, `Model.objects.filter(<matches nothing>).delete()` returns a result of one consistent shape, regardless of whether the model has foreign keys or relations.
2. The zero-deletion result matches the chosen option exactly:
   - Option A: `(0, {})`
   - Option B: `(0, {'<label>': 0, ...})`, with the key set defined in the spec once decided.
3. In every result, `result[0] == sum(result[1].values())`.
4. Results for non-zero deletions are identical to current behaviour, for both simple and cascading models.
5. `Model.delete()` on an instance gives correct results that follow the same convention.
6. The new regression tests fail before the change and pass after it. The full existing deletion test suite passes.
7. Documentation of the return value describes the zero-deletion case, if it was ambiguous or now differs.

## Open Questions

1. **Which consistent form should be canonical?**
   - **Option A (`(0, {})`)** matches the collector path and the principle "only models with deleted rows appear".
   - **Option B (zero-valued keys)** keeps the queried model's label visible even when nothing was deleted.

   Which option should we adopt? A tentative preference is Option A, because it seems to need the smaller behavioural change and gives one consistent rule. This needs confirmation.
2. Under Option B, which keys should appear? Only the queried model, or every model the collector considered for cascade, each with 0?
3. In a **non-zero** cascading delete, some related models may delete zero rows. Should they appear with `0` or be left out? The fix should apply one rule to both cases.
4. Is this treated as a bug fix (no deprecation) or as a behaviour change needing a release note? Some callers may rely on the current zero-case shape, for example by checking `result[1]['app.Model'] == 0`.
5. Which Django versions should receive the fix: only the development branch, or backports too?
6. Does the current documentation state anything about the zero-deletion return value that must be kept or corrected?
7. Repository specifics are needed for implementation: test command, file locations and code style conventions are all currently unknown.