# Spec: Correct related-object assignment for multi-level `FilteredRelation` with `select_related()`

## Objective

Using `select_related()` on a `FilteredRelation` whose path spans more than one relation (e.g. `'pool__tournament__pool'`) can populate the selected object, or its cached related objects, with an instance of the wrong model.

**Reproduction (from the issue):**

```python
# add to known_related_objects.tests.ExistingRelatedInstancesTests
def test_wrong_select_related(self):
    with self.assertNumQueries(3):
        p = list(PoolStyle.objects.annotate(
            tournament_pool=FilteredRelation('pool__tournament__pool'),
        ).select_related('tournament_pool'))
        self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament)
```

**Observed:**
`AssertionError: <Tournament: Tournament object (1)> != <PoolStyle: PoolStyle object (1)>`

`p[0].tournament_pool.tournament` resolves to a `PoolStyle` instead of a `Tournament`. The originating `PoolStyle` instance seems to be cached on the related object under an attribute that belongs to a different relation in the chain. That attribute should hold a `Tournament`, but it holds the source `PoolStyle`.

**Who is affected:** Django ORM users who combine a multi-level `FilteredRelation` with `select_related()`. The ORM silently returns wrong data, with no error raised.

**Success looks like:**
- Every model instance reached through a multi-level `FilteredRelation` with `select_related()` has the correct type.
- Every cached relation on those instances points to the correct object.
- Single-level `FilteredRelation` and plain `select_related()` keep working exactly as they do today.

## Assumptions

1. The codebase is Django. The failing test belongs in `tests/known_related_objects/tests.py` in `ExistingRelatedInstancesTests`, as the issue's traceback shows.
2. The `known_related_objects` test models relate as follows: `PoolStyle → Pool` (one-to-one or FK), `Pool → Tournament` (FK), and `Tournament → Pool` (reverse). These are inferred from the field path `pool__tournament__pool` and the assertion. They have not been verified.
3. The bug is in how the SQL compiler or queryset iterator assigns or caches related objects for `FilteredRelation` aliases in `select_related()`. The likely cause is a setter that assumes a single-hop relation and wires the root object back onto the related instance. This is a hypothesis, not a confirmed root cause.
4. The SQL query itself (joins and selected columns) is probably correct, and only the in-memory assignment of objects is wrong. This is unverified.
5. The fix should not change the public API or how `FilteredRelation` is declared.

## Tech Stack

- Python and Django ORM. The affected versions and branch are **unknown**.
- Database backends: **unknown**. The fix should be backend-agnostic.

## Commands

All commands are **unknown**, because the repository is not visible. The usual Django test runner invocation (run from `tests/`) would be something like `./runtests.py known_related_objects filtered_relation select_related`, but this is unconfirmed.

- Build: unknown / not applicable
- Test: unknown (see the note above)
- Lint: unknown

## Project Structure

Only these locations are known from the issue:

- `tests/known_related_objects/tests.py` holds the test class `ExistingRelatedInstancesTests`, where the regression test goes.
- The exact source module containing the defect is **unknown**. Likely candidates are the SQL compiler's related-selection logic and the queryset's related-object population logic.
- Other relevant test packages probably exist, such as `filtered_relation` and `select_related`, but this is unverified.

## Code Style

Follow the existing Django code and test conventions. The issue's test snippet shows the expected test style:
- methods on a `TestCase` subclass
- `assertNumQueries` to guard query counts
- direct comparisons of model instances

No further style details are visible.

## Testing Strategy

- **Regression test:** add the issue's test, or an equivalent, to `known_related_objects.tests.ExistingRelatedInstancesTests`. It must fail before the fix and pass after.
- **Type/identity assertions:** check that `p[0].tournament_pool` is a `Pool` and `p[0].tournament_pool.tournament` is a `Tournament`, in addition to the equality check from the issue.
- **No-regression coverage:** the existing `known_related_objects`, `filtered_relation`, and `select_related`-related test suites must still pass.
- **Additional cases worth covering:**
  - a two-level `FilteredRelation` path, such as `'pool__tournament'`, with `select_related()`
  - a single-level `FilteredRelation` with `select_related()`, which must keep setting the reverse/known-related cache correctly
  - a multi-level `FilteredRelation` combined with ordinary `select_related()` fields in the same query

## Boundaries

- **Always:**
  - Add a regression test reproducing the issue.
  - Keep single-hop `FilteredRelation` and normal `select_related()` behaviour unchanged.
  - Run the related ORM test suites before committing.
- **Ask first:**
  - Changing the generated SQL.
  - Changing query counts in existing tests.
  - Changing public `FilteredRelation` or `select_related()` semantics.
  - Touching code outside the ORM query or compiler layer.
- **Never:**
  - Weaken or delete existing assertions to make tests pass.
  - Silently drop caching for single-level relations, which would add extra queries.
  - Add new dependencies.

## Success Criteria

1. Evaluating `PoolStyle.objects.annotate(tournament_pool=FilteredRelation('pool__tournament__pool')).select_related('tournament_pool')` gives these results:
   - `p[0].tournament_pool` is a `Pool` instance.
   - `p[0].tournament_pool.tournament` is a `Tournament` instance and equals `p[0].pool.tournament`.
2. No object reached via a multi-level `FilteredRelation` has an instance of the wrong model cached on any relation attribute.
3. The regression test passes within the agreed query budget (see Open Questions).
4. All existing tests in the relevant ORM suites pass, with no changes to their expected query counts.

## Open Questions

1. **Query count:** the issue's test asserts `assertNumQueries(3)`, and the block includes the attribute accesses. Is 3 the intended budget, or should some of these relations be served from cache, giving fewer queries? What exactly should be cached for intermediate hops of a multi-level `FilteredRelation`?
2. **Known-related caching:** for multi-level paths, should the related object cache any back-reference to the root instance at all, or should back-reference caching apply only to single-hop relations?
3. **Version scope:** which Django versions or branches are affected, and should the fix be backported?
4. **Other operations:** does the same mis-assignment occur with `prefetch_related()`, or with nested `select_related('tournament_pool__tournament')`? Should those be in scope?
5. **Model verification:** please confirm the actual `known_related_objects` model definitions (field names and relation types) that assumption 2 relies on.