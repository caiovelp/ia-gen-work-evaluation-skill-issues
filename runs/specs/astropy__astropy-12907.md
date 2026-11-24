# Spec: Correct `separability_matrix` for Nested CompoundModels

## Assumptions
1. The bug is in `astropy.modeling.separable`, the module that provides `separability_matrix` per the issue's import. The exact source file path is not shown in the issue, so it is unverified.
2. Separability is a property of the model's mathematical structure. Grouping with parentheses or nesting with `&` must not change the result, because `&` is associative in meaning. So `A & (B & C)` should give the same matrix as `(A & B) & C`.
3. The flat results shown in the issue are correct and are the reference behavior:
   - `Linear1D & Linear1D` gives a diagonal matrix.
   - `Pix2Sky_TAN & Linear1D & Linear1D` gives a 2×2 block plus a diagonal.
4. The fault is not specific to `Pix2Sky_TAN` or `Linear1D`. It most likely affects any compound model whose right-hand operand (and possibly left-hand) of `&` is itself a `CompoundModel`.
5. Other operators that build compound models (for example `|`) may hit the same nesting problem. This is not confirmed by the issue.
6. The public API (`separability_matrix` signature, return type: a boolean numpy array of shape `(n_outputs, n_inputs)`) must not change.
7. The test framework is pytest. This is assumed from the astropy ecosystem and not confirmed by the issue.

## Objective
`separability_matrix` returns wrong results when a `CompoundModel` is nested inside another `CompoundModel`.

Reproduction from the issue:

```python
from astropy.modeling import models as m
from astropy.modeling.separable import separability_matrix

cm = m.Linear1D(10) & m.Linear1D(5)
separability_matrix(m.Pix2Sky_TAN() & cm)
```

Actual result (the bottom-right block wrongly says the two linear models are coupled):

```
[[ True,  True, False, False],
 [ True,  True, False, False],
 [False, False,  True,  True],
 [False, False,  True,  True]]
```

Expected result (identical to the non-nested `Pix2Sky_TAN() & Linear1D(10) & Linear1D(5)`):

```
[[ True,  True, False, False],
 [ True,  True, False, False],
 [False, False,  True, False],
 [False, False, False,  True]]
```

**Users:** astropy modeling users, e.g. people building WCS / GWCS transforms. They rely on separability to tell which outputs depend on which inputs.

**Success means:** the separability matrix of a compound model depends only on its structure, never on how it was grouped or nested.

## Tech Stack
- Python, astropy (`astropy.modeling`), numpy.
- Supported Python, numpy and astropy versions: unknown, not stated in the issue.
- The astropy version the bug was observed on: unknown.

## Commands
- Build: unknown
- Test: unknown. Presumably pytest scoped to the modeling separability tests; the exact command and path are unverified.
- Lint: unknown
- Dev: unknown

## Project Structure
- Implementation: the module behind `astropy.modeling.separable`. Its file path is unknown and not shown in the issue.
- Tests: the existing test location for separability is unknown and needs to be found in the repo.
- Docs / changelog: astropy's changelog convention is unknown.

## Code Style
- Follow the existing style in `astropy.modeling.separable`. It is not visible from the issue.
- No code snippet is available.

## Testing Strategy
- **Unit tests** for `separability_matrix` (and `is_separable`, if it shares the same code path) using nested compound models. Compare against the hand-computed expected matrix and against the equivalent flat model.
- **Regression test:** the exact case from the issue, `Pix2Sky_TAN() & (Linear1D & Linear1D)`.
- **Grouping-invariance tests:**
  - `A & (B & C)` vs `(A & B) & C` vs `A & B & C`.
  - Nesting on the left side as well as the right side.
  - Deeper nesting (3+ levels).
- **Mixed-operator tests:** nested sub-models combined with `|` (and other compound operators, if supported by separability). Check that results match the equivalent flat expression.
- **Existing separability tests** must keep passing, with no expectations changed.
- Coverage target: unknown. At minimum, every branch touched by the change must be exercised.

## Boundaries
- **Always:**
  - Keep the public signature and return type of `separability_matrix` unchanged.
  - Add a regression test reproducing the issue.
  - Run the existing modeling test suite before committing.
- **Ask first:**
  - Changing the behavior of `is_separable` or other public functions in `separable`.
  - Changing how `CompoundModel` represents its tree.
  - Adding dependencies.
  - Changing results for any non-nested case.
- **Never:**
  - Modify or delete existing passing tests to make the fix pass.
  - Special-case specific model classes (e.g. `Linear1D`, `Pix2Sky_TAN`) instead of fixing the general nesting logic.

## Success Criteria
1. `separability_matrix(m.Pix2Sky_TAN() & cm)` returns the expected matrix shown above, where `cm = m.Linear1D(10) & m.Linear1D(5)`.
2. For models A, B, C, these all return identical matrices: `A & (B & C)`, `(A & B) & C`, and `A & B & C`. This holds for nesting on either side and at any depth.
3. Expressions combining nested compound sub-models with `|` produce the same matrix as their equivalent flat expression.
4. All pre-existing separability tests pass unchanged.
5. The output shape stays `(n_outputs, n_inputs)` and the dtype stays boolean.

## Open Questions
1. Which astropy version(s) show the bug, and should the fix be backported?
2. Are operators other than `&` (`|`, arithmetic operators, `fix_inputs`, etc.) also affected? Are they in scope for this change?
3. Does `is_separable` share the same faulty path? Should it be covered by the same fix and tests?
4. Are there models with custom separability definitions that need specific nested test cases?
5. What is the exact test command, test file location and changelog convention for this repository?
6. Should the fix be accompanied by a documentation note on separability of nested models?