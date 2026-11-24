# Spec: `partitions()` yields independent dictionaries

## Assumptions
1. `partitions()` lives in `sympy/utilities/iterables.py`, as the issue states. I have not seen its exact signature. I assume it is roughly `partitions(n, m=None, k=None, size=False)`, and that with `size=True` it yields `(M, dict)` tuples instead of bare dicts.
2. The reuse happens because one dict object is changed in place between `yield`s. Every yielded value is the same object, so `list(partitions(n))` returns N references to the final state.
3. The docstring has a caveat about the reuse. It probably shows a workaround such as `[p.copy() for p in partitions(...)]`. I have not seen the exact text.
4. Each yielded dict maps a part value to how many times it appears (e.g. `{2: 1, 1: 1}` for `3 = 2 + 1`). This format will not change.
5. Copying the dict before yielding costs O(number of distinct parts) per partition. That is small next to the cost of generating the partition. This is the issue author's claim and has not been measured.
6. Other functions in the same module may share the reuse pattern (e.g. multiset or ordered partition helpers). This change covers only `partitions()` unless the Open Questions decide otherwise.
7. Callers that already call `.copy()` will keep working. They will just make one copy they no longer need.
8. Other SymPy code may call `partitions()` and depend on the reuse, for example by changing the yielded dict on purpose. I have not checked this.

## Objective
`partitions()` should yield a new, independent dictionary for each partition. Collecting the results, for example with `list(partitions(n))`, should then give the correct partitions without any extra step. Changing one yielded dict must not affect any other yielded dict, and must not affect the generator's internal state.

**Users:** SymPy users and SymPy-internal code that iterate over integer partitions.

**Why:** The current behaviour surprises users. Simple code like `list(partitions(n))` gives results that look wrong. Code that stores or changes partitions can hit subtle bugs. A docstring warning does not prevent these mistakes.

**User stories / acceptance:**
- As a user, I can write `list(partitions(n))` and get every distinct partition of `n`, each one correct.
- As a user, I can store yielded partitions in a list, set or dict and they stay correct after iteration continues.
- As a user, I can change a yielded dict without breaking later partitions from the same iterator.
- With `size=True`, the dict inside each `(M, dict)` tuple is also independent.

## Tech Stack
- Python. The supported versions are whatever SymPy currently supports (unknown).
- SymPy. The affected module is `sympy.utilities.iterables`.
- No new dependencies.

## Commands
Unknown, because the repository is not visible. Likely candidates to confirm:
```
Test (module):  unknown — e.g. pytest on the iterables test file, or SymPy's own test runner
Doctests:       unknown — SymPy's doctest runner for sympy/utilities/iterables.py
Lint:           unknown
```

## Project Structure
- `sympy/utilities/iterables.py` contains `partitions()` and its docstring. The path comes from the issue.
- Test location: unknown. It is probably a `tests/` directory next to `iterables.py`, with a file such as `test_iterables.py`.
- Other call sites of `partitions()` in SymPy: unknown. They need to be found with a search.

## Code Style
- Follow the existing style of `sympy/utilities/iterables.py`. I have not seen it, so no snippet is given.
- Docstring examples are doctests, so they must stay runnable and correct.

## Testing Strategy
- **Unit tests** (in the existing iterables test file, location unknown):
  - `list(partitions(n))` returns distinct, correct partitions for small `n` (e.g. 0, 1, 5, 6), with and without the `m` and `k` restrictions.
  - Each yielded object is a different object: `len({id(p) for p in ps}) == len(ps)`.
  - Changing a yielded dict does not change the following yields.
  - With `size=True`, the dicts inside the tuples are independent, and `M` matches the sum of the dict's values.
  - Edge cases, such as `n <= 0` and invalid `m`/`k`, behave as before. What "as before" means is unknown and must be checked against the current code.
- **Doctests:** update the `partitions()` docstring examples and make sure they pass.
- **Regression:** the full `sympy.utilities` test suite passes, and so do the test suites of any internal callers of `partitions()`.
- **Performance (optional):** measure iterating all partitions of a moderately large `n` before and after the change, to back up the claim that the cost is small.

## Boundaries
- **Always:** keep the content of each yielded partition and the order of partitions exactly the same. Update the docstring so it matches the new behaviour. Add regression tests for list collection and for independence.
- **Ask first:** changing the signature, or adding a flag that brings back the reuse behaviour. Changing other functions in `iterables.py` that reuse objects the same way. Removing "unnecessary" `.copy()` calls at internal call sites. Adding a deprecation or release note.
- **Never:** change the partition representation (the dict format or the `(M, dict)` tuple). Change how many partitions are produced or their order. Remove or weaken existing tests without approval.

## Success Criteria
- `list(partitions(6))` equals the full list of the 11 distinct partitions of 6. Each element is a separate dict with the correct contents.
- Each object yielded by `partitions()` is new, for every combination of `m`, `k` and `size`.
- Changing a yielded dict has no effect on any later yielded value.
- The docstring no longer warns about reuse and no longer requires `.copy()`. Its examples show direct use such as `list(partitions(...))`, and the doctests pass.
- All existing tests pass, including tests for internal callers of `partitions()`.
- If the slowdown is measured, it is acceptable to the maintainers. The threshold is still open.

## Open Questions
1. Should other functions in `sympy.utilities.iterables` that reuse output objects (if there are any) get the same fix in this change? Or should they be tracked separately?
2. Should there be an opt-in way to keep the old reuse behaviour for performance-critical callers? For example, a keyword argument or a separate internal function.
3. Does this change need a release note, or a note in the docstring about the behaviour change?
4. What slowdown is acceptable? Should a benchmark be required before merging?
5. Does any internal SymPy code depend on the reuse, for example by changing the yielded dict on purpose or comparing object identity?
6. If internal call sites already call `.copy()`, should they be simplified in the same change or left alone?
7. What are the exact test and doctest commands, and where is the test file?