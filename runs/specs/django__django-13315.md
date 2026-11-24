# Spec: Prevent duplicate options when `ForeignKey.limit_choices_to` uses a Q object with a join

## Assumptions
1. This is a bug in Django's ORM/forms integration: `ForeignKey.formfield()` produces a model choice field whose choices come from a queryset filtered by `limit_choices_to`.
2. "Involving a join" means the Q object filters across a relation, for example `Q(related__field=...)` traversing a reverse FK or M2M. A join can multiply rows, so the same target object appears more than once.
3. The duplicates are object-level, meaning the same primary key appears more than once. They are not distinct objects with identical labels.
4. The fix must not change which objects are allowed. It only collapses repeated rows of the same object into one choice.
5. The same `limit_choices_to` mechanism applies wherever a ForeignKey's form field queryset is built, including ModelForms, admin forms, and admin raw ID/autocomplete lookups. Only the form field path is confirmed by the issue.
6. `limit_choices_to` can be a dict, a Q object, or a callable that returns either. The bug is reported for Q objects but may also affect dicts or callables that span multi-valued relations.
7. The "regression test in patch" the issue mentions is not available to me. Its exact models and assertions are unknown.

## Objective
When a ForeignKey declares a `limit_choices_to` that filters through a multi-valued relation, its form field should list each eligible target object exactly once.

Today, the join can return the same target row several times, so the rendered `<select>` contains duplicate `<option>`s. This confuses users and may cause validation or selection oddities.

**Users affected:**
- Developers who declare `limit_choices_to` with relational lookups on ForeignKey fields.
- End users of ModelForms and admin forms built from those fields.

**Acceptance criteria:**
- Given a ForeignKey whose `limit_choices_to` is a Q object over a join that matches a target object through several related rows, the generated form field's choices contain that object once.
- The set of eligible objects is unchanged compared with the current behavior, ignoring duplicates.
- Submitting a valid choice still validates and saves correctly. Submitting a choice excluded by `limit_choices_to` is still rejected.
- Existing behavior for `limit_choices_to` without joins (simple dict or Q) is unchanged.

## Tech Stack
- Python / Django, assumed from the issue terminology. Supported versions are **unknown**.
- Database backends that must be covered: **unknown**. The fix should behave the same on every backend Django supports.

## Commands
- Build: **unknown** (not stated in issue)
- Test: **unknown** (not stated in issue; Django's own test runner invocation not visible)
- Lint: **unknown**
- Dev: N/A

## Project Structure
**Unknown.** The repository is not visible. The relevant areas, which are assumptions and need confirmation, are:
- The model field code that implements `ForeignKey.formfield()` and applies `limit_choices_to`.
- The forms code that applies `limit_choices_to` to a model choice field's queryset.
- The existing regression test suites for model forms and `limit_choices_to`.

## Code Style
Follow the existing project style. No snippets can be cited because no source is visible. Unknown.

## Testing Strategy
- **Regression test:** use the issue's scenario. A model has a ForeignKey whose `limit_choices_to` is a Q across a relation, and the data makes one target match through several related rows. Assert that the form field's choices or queryset contain no duplicate primary keys and that the eligible set is correct.
- **Rendering check:** assert that the rendered widget HTML contains a single `<option>` for that object.
- **Validation check:** a valid choice cleans to the right instance. An ineligible choice raises a validation error.
- **Non-regression:** existing `limit_choices_to` tests (dict, Q, callable) pass unchanged.
- **Optional coverage, pending scope decision:** callable `limit_choices_to`, ModelChoiceField subclasses, and admin paths.
- Test framework and file locations: **unknown**.

## Boundaries
- **Always:** keep the eligible-object semantics of `limit_choices_to` exactly as they are; add a regression test that fails before the fix; run the existing model-forms and `limit_choices_to` tests.
- **Ask first:**
  - Changing the public signature or documented behavior of `limit_choices_to`, `formfield()`, or the model choice field.
  - Applying a blanket `.distinct()`, which affects ordering, performance, and backends with restrictions on `DISTINCT` combined with ordering or certain field types.
  - Extending the fix to admin or other code paths.
- **Never:** silently drop valid choices; change the results for queries without joins; remove or weaken existing tests.

## Success Criteria
- [ ] The new regression test (Q-object `limit_choices_to` across a join, with multiple matching related rows) fails on the current code and passes after the fix.
- [ ] The form field's choices contain each eligible object exactly once.
- [ ] The eligible set equals the current deduplicated set; no objects are added or lost.
- [ ] Validation of the field still accepts eligible values and rejects ineligible ones.
- [ ] All existing related-field / model-form / `limit_choices_to` tests pass.
- [ ] No backend-specific failures, for example from DISTINCT combined with ordering or with field types that can't be compared for DISTINCT. Backends in scope are unknown.

## Open Questions
1. Can the regression test from the referenced patch be shared? Its models and data define the exact reproduction.
2. Which Django versions and database backends must the fix support?
3. Is the scope only the form field's choices, or also other places that apply `limit_choices_to`, such as admin raw ID / autocomplete and model validation?
4. Is a `.distinct()`-based approach acceptable, given possible performance cost and backend limitations? Or is an approach that avoids DISTINCT preferred, such as filtering by a subquery (`pk__in=...`)?
5. Should dict-based and callable `limit_choices_to` that span multi-valued relations be covered by the same fix and tests?
6. Should the `limit_choices_to` documentation be updated, for example with a note about joins and duplicates or a release note?
7. What are the exact build, test, and lint commands, and where should the new test live?