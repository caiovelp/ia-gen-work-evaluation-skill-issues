## Summary

Annotating a queryset with a multi-level `FilteredRelation` (e.g. `FilteredRelation('pool__tournament__pool')`) and then passing that annotation to `select_related()` can set the wrong related object. In the reported case, the `tournament` attribute of the filtered-relation object is a `PoolStyle` instance instead of a `Tournament` instance.

## Steps to reproduce

1. Use the models from Django's `known_related_objects` test app (`PoolStyle`, `Pool`, `Tournament`) and its existing test data.
2. Add the test method shown under **Test case** to `known_related_objects.tests.ExistingRelatedInstancesTests`.
3. Run the test, `known_related_objects.tests.ExistingRelatedInstancesTests.test_wrong_select_related`.
4. The test fails on the `assertEqual` line.

## Observed behavior

`p[0].tournament_pool.tournament` is a `PoolStyle` object (`<PoolStyle: PoolStyle object (1)>`). The equality check against `p[0].pool.tournament`, which is `<Tournament: Tournament object (1)>`, fails.

## Expected behavior

`p[0].tournament_pool.tournament` should be the correct `Tournament` instance and equal to `p[0].pool.tournament`. The test also expects the whole block to run in 3 queries (`assertNumQueries(3)`).

## Stack trace / error output

```
======================================================================
FAIL: test_wrong_select_related (known_related_objects.tests.ExistingRelatedInstancesTests.test_wrong_select_related)
----------------------------------------------------------------------
Traceback (most recent call last):
 File "D:\Work\django\tests\known_related_objects\tests.py", line 171, in test_wrong_select_related
	self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament)
AssertionError: <Tournament: Tournament object (1)> != <PoolStyle: PoolStyle object (1)>
----------------------------------------------------------------------
```

## Test case

Add this to `known_related_objects.tests.ExistingRelatedInstancesTests`:

```python
def test_wrong_select_related(self):
    with self.assertNumQueries(3):
        p = list(PoolStyle.objects.annotate(
            tournament_pool=FilteredRelation('pool__tournament__pool'),
        ).select_related('tournament_pool'))
        self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament)
```

## Code example

This is the core query that triggers the issue:

```python
PoolStyle.objects.annotate(
    tournament_pool=FilteredRelation('pool__tournament__pool'),
).select_related('tournament_pool')
```

## Version and environment

The Django version is not provided in the original report. The traceback path (`D:\Work\django\tests\...`) indicates the test was run from a Django source checkout on Windows. The Python version and database backend are not provided in the original report.