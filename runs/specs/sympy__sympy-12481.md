# Spec: Allow Non-Disjoint Cycles in the `Permutation` Constructor

## Assumptions

1. The `Permutation` class is SymPy's `sympy.combinatorics.permutations.Permutation`. The issue does not name the library. This is inferred from the API shape: `Permutation` accepts a list of cycles as a list of lists.
2. Today the constructor rejects cycle-form input whose cycles share an element. It raises `ValueError` before it builds anything. The exact check and error message are unknown, because the repository is not visible.
3. "Applied in left-to-right order" means the first cycle in the list acts on an element first, then the second cycle acts on the result, and so on. This matches SymPy's documented convention for composing cycles, such as `Cycle(1, 2)(2, 3)`. It must be confirmed (see Open Questions).
4. Only **cycle-form** input changes. **Array-form** input, such as `Permutation([1, 0, 2])`, must still reject repeated elements. A repeated element there means the input is not a permutation.
5. Repeated elements **inside a single cycle** remain invalid. For example, `[[0, 1, 0]]` is not a well-formed cycle. Only overlap **between** cycles becomes legal.
6. Existing behavior for disjoint cycles must not change. That includes the result, the `size` inference, and the handling of the `size=` keyword.
7. A singleton cycle such as `[[3]]` keeps its current meaning: it fixes the point and can extend the size.

## Objective

**Problem.** `Permutation([[0, 1], [0, 1]])` raises `ValueError`. Cycle notation with overlapping cycles is a standard and well-defined way to write a product of cycles, so the constructor should accept it.

**Goal.** When `Permutation` gets a list of cycles, some of which share elements, it composes them in left-to-right order and returns the resulting permutation. It does not raise an error.

**Users.** Users of the combinatorics module who write permutations as products of cycles. This includes users who build permutations from products of transpositions.

**Acceptance criteria (user-facing):**
- `Permutation([[0, 1], [0, 1]])` returns the identity permutation on 2 elements, with array form `[0, 1]`.
- For `Permutation([[0, 1], [1, 2]])`, apply `(0 1)` first and then `(1 2)`:
  - 0 → 1 → 2
  - 1 → 0 → 0
  - 2 → 2 → 1

  The array form is therefore `[2, 0, 1]`. This depends on Assumption 3.
- In general, the result equals the composition of the cycles constructed one by one, using the library's existing left-to-right product convention. For SymPy, that is `Cycle(*c1)(*c2)...`.

## Tech Stack

- Language: Python. The version is unknown.
- Library: assumed to be SymPy (see Assumption 1). The version and branch are unknown.
- Dependencies: no new dependencies expected.

## Commands

- Build: unknown. This is likely a pure-Python package with no build step, but that is unconfirmed.
- Test: unknown. The project test runner and the exact invocation for the combinatorics/permutations tests are not visible.
- Lint: unknown.
- Dev: not applicable or unknown.

## Project Structure

- Location of the `Permutation` constructor: unknown. It is presumably the permutations module of the combinatorics package.
- Location of existing permutation tests: unknown.
- Docs and docstrings: the `Permutation` class docstring presumably documents cycle input. Its location and wording are unknown.

## Code Style

- Follow the existing style of the permutations module. No snippet is available.
- Reuse the module's existing cycle-composition mechanism, for example a `Cycle` helper, if one exists. Do not introduce a parallel implementation. Whether such a helper exists is unconfirmed.

## Testing Strategy

The test framework is unknown. The new tests go alongside the existing `Permutation` constructor tests, whose location is unknown.

Required test cases:

1. **Regression from the issue.** `Permutation([[0, 1], [0, 1]])` equals the identity of size 2 and does not raise.
2. **Order sensitivity.**
   - `Permutation([[0, 1], [1, 2]])` gives array form `[2, 0, 1]`.
   - `Permutation([[1, 2], [0, 1]])` gives the result for the opposite order, `[1, 2, 0]`.
   - The two results differ. This proves the order is left-to-right and not arbitrary.
3. **Equivalence to explicit composition.** For several overlapping inputs, the constructed permutation equals the product of the individual cycles under the library's convention.
4. **Disjoint cycles unchanged.** The existing disjoint-cycle tests still pass, including size inference.
5. **`size=` keyword with overlap.** Overlapping cycles combined with an explicit larger `size` produce the correct padded permutation.
6. **Still-invalid input still raises.**
   - Array form with duplicates, such as `Permutation([0, 0, 1])`, still raises `ValueError`.
   - A single cycle with a repeated element, such as `[[0, 1, 0]]`, still raises `ValueError`, if that is current behavior (see Open Questions).
7. **Edge cases.**
   - Three or more overlapping cycles.
   - A cycle repeated an odd and an even number of times.
   - Overlapping input mixed with singleton cycles.

Coverage expectation: every new branch in the constructor's cycle-handling path is exercised.

## Boundaries

**Always:**
- Keep the disjoint-cycle and array-form behavior bit-for-bit unchanged.
- Add regression tests for the reported case.
- Update the constructor docstring so it states that non-disjoint cycles are allowed and composed left to right.

**Ask first:**
- Changing the composition convention, or any public multiplication semantics of `Permutation` or `Cycle`.
- Changing error types or messages for inputs that remain invalid.
- Altering how `size` is inferred.

**Never:**
- Relax duplicate checking for array-form input.
- Silently accept malformed single cycles.
- Delete or weaken existing tests that assert `ValueError` without approval. If an existing test asserts that overlapping cycles raise, update that test explicitly and call out the change.

## Success Criteria

- [ ] `Permutation([[0, 1], [0, 1]])` returns the identity permutation of size 2.
- [ ] Overlapping cycle input gives the same permutation as composing the cycles left to right using the library's existing product convention. This is verified by tests 2 and 3.
- [ ] All pre-existing permutation tests pass, except tests that explicitly assert the old `ValueError` on overlapping cycles. Those are updated, and the change is noted.
- [ ] Array-form duplicates and malformed single cycles still raise `ValueError`.
- [ ] The constructor docstring documents the new behavior with at least one example of non-disjoint cycles.

## Open Questions

1. **Composition order.** Confirm that "left-to-right" means the first listed cycle acts first. With that reading, `[[0, 1], [1, 2]]` gives `[2, 0, 1]`. Under the opposite, function-composition reading it would give `[1, 2, 0]`. Does this match the library's existing `Cycle`/`Permutation` multiplication convention?
2. **Repeats within one cycle.** Should a single cycle with a repeated element, such as `[[0, 1, 0]]`, keep raising `ValueError`? This spec assumes yes.
3. **Existing tests.** Are there existing tests or documentation that assert overlapping cycles raise `ValueError`? Is the maintainers' intent to reverse that deliberately?
4. **Size inference.** With overlapping cycles, should the inferred size still be `max(element) + 1` across all cycles, as for disjoint input? Example: `[[0, 1], [0, 1]]` gives size 2.
5. **Performance.** Is there any constraint on construction cost for very long cycle lists? This would matter if composing them is noticeably slower than the current disjoint path.
6. **Repository details.** The library identity and version, the file locations, and the test and lint commands are all unknown and need confirmation.