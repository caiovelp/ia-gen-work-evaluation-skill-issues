# Spec: Migration optimizer reduces consecutive `AlterField` operations on the same field

## Objective

When the migration optimizer is given consecutive `AlterField` operations that target the same field on the same model, it should collapse them into a single `AlterField` carrying the final field definition.

**Current behaviour, as reported in the issue:**

- `AddField` followed by several `AlterField` on the same field optimizes down to a single `AddField`. This already works.
- Several `AlterField` on the same field with no preceding `AddField` are not reduced at all. For example, `optimizer.optimize(operations[1:], "books")` returns all three `AlterField` operations unchanged.
- This happens in real use when the `AddField` sits in another migration, such as a non-elidable migration or a migration that was not squashed.

**Root cause, as stated in the reporter's analysis:** `AlterField.reduce` has no case for an incoming operation that is also an `AlterField`.

**Who benefits:** Django users who squash or optimize migrations. Fewer redundant operations mean shorter squashed migrations and fewer schema-alter steps.

**User stories**

- As a developer squashing migrations, I want repeated alterations of one field merged into one, so the squashed migration is minimal.
- As a maintainer, I want the reduction to be semantically safe, so the optimized migration has the same end state and runs without failing where the original would have succeeded.

**Proposed approach (from the issue; not yet validated):** add this case to `AlterField.reduce`:

```python
if isinstance(operation, AlterField) and self.is_same_field_operation(
    operation
):
    return [operation]
```

The issue also asks a second question: if the current behaviour is intentional, should it be documented instead? See Open Questions.

## Assumptions

1. This is a change to Django's migration optimizer (`MigrationOptimizer.optimize`) and the `AlterField` operation's `reduce` method. The exact file paths are not shown in the issue and are unknown here.
2. `is_same_field_operation` already exists on field operations and compares model name and field name the same way other field reductions do. Its exact semantics, such as case-insensitivity, are not shown and are assumed rather than verified.
3. The final `AlterField` fully describes the target field state. So, for the in-memory project state, the earlier `AlterField` operations are redundant.
4. The existing `AddField` + `AlterField` reductions and `AlterField` + `RemoveField` reductions stay unchanged.
5. The optimizer's existing rules for reducing across intervening operations ("optimize through") are unchanged. The new case only defines what happens when two same-field `AlterField` operations meet.
6. A behaviour change is the preferred resolution, rather than only documenting the current behaviour. This is pending confirmation (see Open Questions).

## Tech Stack

- Python and Django. Versions are unknown; the target branch is not stated in the issue.
- Components involved: the migration optimizer, `AlterField`, and its `reduce` and `is_same_field_operation` methods.

## Commands

- Build: unknown (not given in the issue)
- Test: unknown (not given in the issue). The relevant tests are the migration optimizer tests, but their location and runner command are not visible.
- Lint: unknown

## Project Structure

Unknown; not visible from the issue. The following are expected to exist, but their paths are unconfirmed:

- the module that defines field operations (`AddField`, `AlterField`, `RemoveField`, `RenameField`)
- the module that defines `MigrationOptimizer`
- the optimizer test suite

## Code Style

- Follow the existing conventions of the surrounding `reduce` implementations. These are not visible here, beyond the snippet in the issue.
- The new reduction should have the same shape as the sibling cases: an `isinstance` check combined with `self.is_same_field_operation(operation)`, returning a list of operations.

## Testing Strategy

- **Level:** unit tests of the optimizer, using the existing optimizer test suite and its helpers (location unknown).
- **Required cases:**
  1. Two or more consecutive `AlterField` operations on the same model and field reduce to the single last `AlterField`. This uses the issue's example with `operations[1:]`.
  2. `AlterField` operations on different fields of the same model are not merged.
  3. `AlterField` operations on the same field name but different models are not merged.
  4. The existing `AddField` + multiple `AlterField` → single `AddField` behaviour is unchanged.
  5. `AlterField` followed by `RemoveField` on the same field behaves as it does today.
  6. Merging across unrelated intervening operations follows the existing optimize-through rules.
  7. Cases involving `preserve_default=False`, with whatever behaviour is decided under Open Question 2.
- **Regression:** the full existing optimizer test suite passes unchanged, except for tests that intentionally encode the old non-reducing behaviour (see Open Question 4).

## Boundaries

**Always:**
- Keep the reduction semantically safe. Applying the optimized operations must give the same final project state as the originals.
- Add tests for every new reduction path.
- Leave existing reductions untouched.

**Ask first:**
- Changing how `preserve_default` is handled during reduction.
- Changing `is_same_field_operation`.
- Adding documentation or release notes for the behaviour change.
- Altering any existing test expectations.

**Never:**
- Reduce operations that target different models or fields.
- Drop an operation whose side effects are not reproduced by the remaining operation.
- Change the optimizer's general optimize-through algorithm as part of this fix.

## Success Criteria

- [ ] `optimize([AlterField(book.title, A), AlterField(book.title, B), AlterField(book.title, C)], "books")` returns exactly `[AlterField(book.title, C)]`, with the field definition equal to the last one.
- [ ] `AlterField` operations on different fields or different models are not reduced into each other.
- [ ] `AddField` + `AlterField`* still reduces to a single `AddField` with the final definition.
- [ ] `preserve_default` cases behave as decided in Open Question 2, with tests that cover them.
- [ ] All existing optimizer tests pass, or any changes to them are explicitly justified.
- [ ] Documentation or release notes are updated if that is decided under Open Question 3.

## Open Questions

1. **Intended or not?** Is the lack of `AlterField` + `AlterField` reduction deliberate? If yes, the deliverable becomes documentation rather than code. Confirmation from maintainers is needed.
2. **`preserve_default=False` safety.** An earlier `AlterField` with `preserve_default=False` may supply a one-off default used to backfill existing rows, for example when changing a column from null to not-null. If the merge returns only the later operation, that backfill could be lost. Questions to settle:
   - Should a merge be refused when the earlier operation has `preserve_default=False`?
   - Or should the surviving operation carry over that default somehow?
   - What should happen when the later operation has `preserve_default=False`?
3. **Documentation.** Should the new reduction be mentioned in release notes or in the migrations / squashing documentation?
4. **Existing tests.** Do any existing tests assert that consecutive `AlterField` operations are not reduced? If so, can they be updated?
5. **Other operations.** Should the same pattern apply to other same-target operation pairs that currently do not reduce? This spec assumes the scope is limited to `AlterField` + `AlterField` only.
6. **Commands and paths.** What are the exact commands to run the optimizer tests, and where do the relevant source and test files live? Neither is visible from the issue.
7. **Target branch.** Which Django version or branch should receive this change?